"""Build the Word version of the report from the Markdown one.

Both copies of the report must say the same thing, so the .docx is generated from
report/Lab4_1_Report.md, the same source as the PDF (report/build_report.py). The numbers, tables and
code images are filled in exactly as for the PDF. report/title_page_template.docx supplies the title
page (course, group, authors, university logo); its assignment title is set to this lab, and the report
is appended after a page break. The Markdown title and author line are skipped because the title page
already has them.

Run from the repository root (after the notebook has been run):
    .venv/bin/python report/build_docx.py
"""
import re
import sys
import zipfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_report                              # noqa: E402  same tokens, tables and code images

ROOT = Path(__file__).resolve().parent.parent
MARKDOWN = ROOT / "report" / "Lab4_1_Report.md"
DOCX = ROOT / "report" / "Lab4_1_Report.docx"
TEMPLATE = ROOT / "report" / "title_page_template.docx"
TEMPLATE_TITLE = "Lab3: Explainability and BRBES-2"
TITLE = "Lab 4.1: Explaining Phishing Detectors"

PAGE_WIDTH_DXA = 12240 - 540 - 450        # page width minus the template's margins
EMU_PER_INCH = 914400
FIGURE_WIDTH_INCHES = 7.4                 # a figure row uses the whole text width
BODY_SIZE = 20                            # half-points: 10 pt body text
CAPTION_SIZE = 18
TABLE_SIZE = 17


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------------------
# Inline formatting: **bold**, *italic*, `code`
# ---------------------------------------------------------------------------
def runs(text, size=None, bold=False, italic=False):
    out = []
    for piece in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)", text):
        if not piece:
            continue
        properties = []
        body = piece
        if piece.startswith("**") and piece.endswith("**"):
            body, properties = piece[2:-2].replace("`", ""), ["<w:b/>"]
        elif piece.startswith("*") and piece.endswith("*"):
            body, properties = piece[1:-1].replace("`", ""), ["<w:i/>"]
        elif piece.startswith("`") and piece.endswith("`"):
            body, properties = piece[1:-1], ['<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>']
        if bold and "<w:b/>" not in properties:
            properties.append("<w:b/>")
        if italic and "<w:i/>" not in properties:
            properties.append("<w:i/>")
        if size:
            properties.append(f'<w:sz w:val="{size}"/>')
        rpr = f"<w:rPr>{''.join(properties)}</w:rPr>" if properties else ""
        body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)          # links -> their text
        out.append(f'{("<w:r>" + rpr)}<w:t xml:space="preserve">{esc(body)}</w:t></w:r>')
    return "".join(out) or "<w:r><w:t/></w:r>"


def paragraph(text, style=None, size=None, bold=False, italic=False, extra=""):
    properties = "".join(filter(None, [
        f'<w:pStyle w:val="{style}"/>' if style else "",
        extra,
        f'<w:rPr><w:sz w:val="{size}"/></w:rPr>' if size else "",
    ]))
    ppr = f"<w:pPr>{properties}</w:pPr>" if properties else ""
    return f"<w:p>{ppr}{runs(text, size=size, bold=bold, italic=italic)}</w:p>"


# ---------------------------------------------------------------------------
# Blocks
# ---------------------------------------------------------------------------
def table(rows):
    """Markdown table rows -> a TableGrid table; column widths follow the longest cell in each column."""
    header, body = rows[0], rows[1:]
    weights = [max(3, min(40, max(len(re.sub(r"[`*]", "", r[i])) for r in rows))) for i in range(len(header))]
    total = sum(weights)
    widths = [int(PAGE_WIDTH_DXA * w / total) for w in weights]
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)

    xml = ['<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/>'
           f'<w:tblW w:w="{sum(widths)}" w:type="dxa"/>'
           '<w:tblLayout w:type="fixed"/></w:tblPr>'
           f"<w:tblGrid>{grid}</w:tblGrid>"]
    for index, row in enumerate(rows):
        cells = []
        for column, cell in enumerate(row):
            shading = '<w:shd w:val="clear" w:color="auto" w:fill="E7E6E6"/>' if index == 0 else ""
            cells.append(f'<w:tc><w:tcPr><w:tcW w:w="{widths[column]}" w:type="dxa"/>{shading}'
                         '<w:vAlign w:val="center"/></w:tcPr>'
                         + paragraph(cell, size=TABLE_SIZE, bold=(index == 0),
                                     extra='<w:spacing w:before="20" w:after="20"/>') + "</w:tc>")
        header_mark = '<w:trPr><w:tblHeader/></w:trPr>' if index == 0 else ""
        xml.append(f"<w:tr>{header_mark}{''.join(cells)}</w:tr>")
    xml.append("</w:tbl>")
    return "".join(xml) + '<w:p><w:pPr><w:spacing w:after="0"/><w:rPr><w:sz w:val="8"/></w:rPr></w:pPr></w:p>'


def image_row(pictures, first_id, max_height_inches=3.3):
    """One centred paragraph with the pictures side by side, sharing the text width."""
    gap = 0.15
    slot = (FIGURE_WIDTH_INCHES - gap * (len(pictures) - 1)) / len(pictures)
    xml = ['<w:p><w:pPr><w:keepNext/><w:jc w:val="center"/><w:spacing w:after="40"/></w:pPr>']
    for number, (path, relationship_id) in enumerate(pictures):
        with Image.open(path) as picture:
            width, height = picture.size
        w_in = slot
        if w_in * height / width > max_height_inches:
            w_in = max_height_inches * width / height
        cx, cy = int(w_in * EMU_PER_INCH), int(w_in * height / width * EMU_PER_INCH)
        drawing_id = first_id + number
        if number:
            xml.append('<w:r><w:t xml:space="preserve">  </w:t></w:r>')
        xml.append(
            '<w:r><w:drawing>'
            f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
            f'<wp:docPr id="{drawing_id}" name="Picture {drawing_id}"/><a:graphic '
            'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData '
            'uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic '
            'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr>'
            f'<pic:cNvPr id="{drawing_id}" name="Picture {drawing_id}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{relationship_id}"/><a:stretch><a:fillRect/></a:stretch>'
            '</pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/>'
            f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            "</pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>")
    xml.append("</w:p>")
    return "".join(xml)


def caption(text):
    return paragraph(re.sub(r"`([^`]+)`", r"\1", text), size=CAPTION_SIZE, italic=True,
                     extra='<w:jc w:val="center"/>')


# ---------------------------------------------------------------------------
# Markdown -> body XML
# ---------------------------------------------------------------------------
def prepare(markdown):
    """Fill numbers and tables as for the PDF, and skip the title and author line (the title page has them)."""
    text = build_report.expand(markdown)
    return text[text.index("\n## "):]


def figure_paths(line):
    """The image files of a [[figures ...]] or [[code ...]] line, and its caption."""
    if m := re.fullmatch(r"\[\[figures (.+?) \| (.+)\]\]", line):
        return [ROOT / p.strip() for p in m.group(1).split(";")], m.group(2)
    if m := re.fullmatch(r"\[\[code (.+?) \| (.+)\]\]", line):
        return build_report.code_images(m.group(1)), m.group(2)
    return None, None


def convert(markdown, images):
    body, lines, index = [], markdown.splitlines(), 0
    drawing_id = 100
    while index < len(lines):
        line = lines[index].rstrip()
        paths, text = figure_paths(line.strip())
        if not line:
            index += 1
        elif line.strip() == "[[pagebreak]]":
            body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
            index += 1
        elif paths:                                                    # figure row + caption
            code = line.startswith("[[code")
            body.append(image_row([(p, images[p]) for p in paths], drawing_id,
                                  max_height_inches=8.5 if code else 3.3))
            body.append(caption(text))
            drawing_id += len(paths)
            index += 1
        elif line.startswith("|"):                                    # table
            rows = []
            while index < len(lines) and lines[index].startswith("|"):
                cells = [c.strip() for c in lines[index].strip().strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in cells):
                    rows.append(cells)
                index += 1
            body.append(table(rows))
        elif line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            text = line.lstrip("# ").strip()
            body.append(paragraph(text, style=f"Heading{min(level, 3)}"))
            index += 1
        elif line.startswith("- "):                                   # bullet list
            while index < len(lines) and lines[index].startswith("- "):
                body.append(paragraph(lines[index][2:].strip(), style="ListParagraph", size=BODY_SIZE,
                                      extra='<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'))
                index += 1
        else:                                                         # paragraph (possibly a caption)
            text = [line]
            index += 1
            while (index < len(lines) and lines[index].strip()
                   and not re.match(r"^(\||#|- |\[\[)", lines[index])):
                text.append(lines[index].strip())
                index += 1
            joined = " ".join(text)
            if re.match(r"^\*(Table|Figure) \d", joined):             # table caption, keep with table
                body.append(paragraph(joined, size=CAPTION_SIZE,
                                      extra='<w:keepNext/><w:spacing w:after="60"/>'))
            else:
                body.append(paragraph(joined, size=BODY_SIZE, extra='<w:spacing w:after="120"/>'))
    return "".join(body)


def main():
    if not TEMPLATE.is_file():
        sys.exit(f"ERROR: {TEMPLATE.relative_to(ROOT)} is missing (the title page template).")

    markdown = prepare(MARKDOWN.read_text(encoding="utf-8"))
    figures = []
    for line in markdown.splitlines():
        paths, _ = figure_paths(line.strip())
        figures += [Path(p) for p in paths or []]

    with zipfile.ZipFile(TEMPLATE) as template:
        parts = {name: template.read(name) for name in template.namelist()}

    # register the figures as relationships and media parts
    rels = parts["word/_rels/document.xml.rels"].decode("utf-8")
    used = [int(n) for n in re.findall(r'Id="rId(\d+)"', rels)]
    images, additions = {}, []
    for offset, path in enumerate(figures, start=max(used, default=0) + 1):
        relationship_id = f"rId{offset}"
        target = f"media/figure{offset}.png"
        images[path] = relationship_id
        parts[f"word/{target}"] = path.read_bytes()
        additions.append(f'<Relationship Id="{relationship_id}" Type="http://schemas.openxmlformats.org/'
                         f'officeDocument/2006/relationships/image" Target="{target}"/>')
    parts["word/_rels/document.xml.rels"] = rels.replace("</Relationships>",
                                                         "".join(additions) + "</Relationships>").encode()

    # Heading2 / Heading3 are not in the template; add them next to the existing Heading1
    styles = parts["word/styles.xml"].decode("utf-8")
    for level, size in ((2, 26), (3, 23)):
        if f'w:styleId="Heading{level}"' not in styles:
            styles = styles.replace("</w:styles>", (
                f'<w:style w:type="paragraph" w:styleId="Heading{level}"><w:name w:val="heading {level}"/>'
                '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>'
                f'<w:pPr><w:keepNext/><w:spacing w:before="200" w:after="80"/><w:outlineLvl w:val="{level - 1}"/></w:pPr>'
                f'<w:rPr><w:b/><w:color w:val="1F3864"/><w:sz w:val="{size}"/></w:rPr></w:style></w:styles>'))
    parts["word/styles.xml"] = styles.encode()

    # this lab's title on the title page, then the report after a page break
    document = parts["word/document.xml"].decode("utf-8")
    if TEMPLATE_TITLE not in document:
        sys.exit(f"ERROR: the title {TEMPLATE_TITLE!r} was not found in the template")
    document = document.replace(TEMPLATE_TITLE, TITLE)
    page_break = '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
    body = page_break + convert(markdown, images)
    section = re.search(r"<w:sectPr\b.*?</w:sectPr>", document, re.S).group()
    document = document.replace(section, body + section)
    parts["word/document.xml"] = document.encode()

    with zipfile.ZipFile(DOCX, "w", zipfile.ZIP_DEFLATED) as out:
        for name, data in parts.items():
            out.writestr(name, data)
    print(f"Wrote {DOCX.relative_to(ROOT)} ({DOCX.stat().st_size / 1024:.0f} KB, "
          f"{len(figures)} images, title page preserved)")


if __name__ == "__main__":
    main()
