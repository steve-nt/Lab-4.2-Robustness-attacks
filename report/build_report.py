"""Build the lab report PDF from report/Lab4_2_Report.md.

The Markdown file is the report itself, readable in any Markdown viewer: ordinary headings, paragraphs,
lists, pipe tables, **bold**, *italic* and `code`, plus standard images. A figure is a line holding one
or more images, followed by its caption on the next line, which starts with "*Figure":

    ![SHAP ranking](../results/figures/D1_shap_bar.png) ![Deletion test](../results/figures/F1_deletion.png)
    *Figure 2. Left: ... Right: ...*

Image paths are relative to report/. A line "<!-- pagebreak -->" starts a new page (invisible in a
Markdown viewer). The code "screenshot" (report/figures/code_greedy_attack.png) is rendered from the
hand-in notebook by make_code_images(), so it always shows the code that produced the numbers.
The fonts are bundled in report/fonts/, so the PDF looks the same on every machine.

Run from the repository root (after the hand-in notebook has been run):
    .venv/bin/python report/build_report.py
"""
import re
import sys
from pathlib import Path

import markdown
import nbformat
import pandas as pd
from fpdf import FPDF, FontFace
from fpdf.fonts import TextStyle
from PIL import Image, ImageDraw, ImageFont
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "report" / "Lab4_2_Report.md"
OUTPUT = ROOT / "report" / "Lab4_2_Report.pdf"
TABLES = ROOT / "results" / "tables"
NOTEBOOK = ROOT / "lab4_2_robustness_attacks.ipynb"
FONTS = ROOT / "report" / "fonts"
CODE_IMAGES = ROOT / "report" / "figures"
REPORT_DIR = ROOT / "report"
# Code screenshots used by the report: image file -> (lab step, text that identifies the cell).
CODE_FIGURES = {"code_greedy_attack.png": ("C2", "def greedy_attack")}

BODY_PT, TABLE_PT, CAPTION_PT = 9.5, 8, 8.5
MARGIN = 15                                   # mm
GREY = (90, 90, 90)


# ---------------------------------------------------------------------------
# 1. Fill in numbers and tables from results/tables/*.csv
# ---------------------------------------------------------------------------
_csv_cache = {}


def load(name):
    if name not in _csv_cache:
        path = TABLES / f"{name}.csv"
        if not path.exists():
            sys.exit(f"ERROR: {path.relative_to(ROOT)} not found. Run the notebook first.")
        _csv_cache[name] = pd.read_csv(path, dtype=str, keep_default_na=False)
    return _csv_cache[name]


def fmt(raw, spec=None):
    """Format a CSV value: floats with 3 decimals, whole numbers without, or with a given spec."""
    try:
        value = float(raw)
    except ValueError:
        return raw
    if spec:
        return format(value, spec)
    if "." not in raw and value.is_integer():          # whole numbers stay whole: 5, 4,265
        return f"{int(value):,}"
    if abs(value) >= 100:                              # counts such as rule support: 1,106
        return f"{value:,.0f}"
    return f"{value:.3f}"


def lookup(name, row, column, spec=None):
    df = load(name)
    if row.startswith("#"):
        record = df.iloc[int(row[1:]) - 1]
    else:
        match = df[df.iloc[:, 0] == row]
        if len(match) != 1:
            sys.exit(f"ERROR: row {row!r} not found (or not unique) in {name}.csv")
        record = match.iloc[0]
    if column not in df.columns:
        sys.exit(f"ERROR: column {column!r} not in {name}.csv ({', '.join(df.columns)})")
    return fmt(record[column], spec)


def value_token(match):
    parts = match.group(1).split(":")
    if len(parts) not in (3, 4):
        sys.exit(f"ERROR: bad value token {{{{{match.group(1)}}}}}")
    return lookup(*[p.strip() for p in parts])


def table_directive(match):
    fields = [f.strip() for f in match.group(1).split("|")]
    name, columns, headers = fields[0], [c.strip() for c in fields[1].split(",")], \
        [h.strip() for h in fields[2].split(",")]
    options = dict(f.split("=", 1) for f in fields[3:] if "=" in f)
    df = load(name)
    if "rows" in options:
        df = df.head(int(options["rows"]))
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for _, record in df.iterrows():
        lines.append("| " + " | ".join(fmt(record[c]) for c in columns) + " |")
    return "\n".join(lines)


def expand(text):
    text = re.sub(r"\[\[table (.+?)\]\]", table_directive, text)
    text = re.sub(r"\{\{(.+?)\}\}", value_token, text)
    left = re.findall(r"\{\{.*?\}\}", text)
    if left:
        sys.exit(f"ERROR: unresolved tokens: {left}")
    return text


# ---------------------------------------------------------------------------
# 2. Code "screenshots": code cells of the hand-in notebook rendered as images
# ---------------------------------------------------------------------------
def code_image(step, path, lines=None, font_px=26, pad=24, max_chars=100, contains=None):
    """Render the code of one lab step (or lines first-last of it) as a PNG, like a screenshot.
    With `contains`, only the code cell of that step containing this text is used."""
    nb = nbformat.read(NOTEBOOK, as_version=4)
    cells = [c.source for c in nb.cells
             if c.cell_type == "code" and c.source.startswith(f"# STEP {step}\n")
             and (contains is None or contains in c.source)]
    if not cells:
        sys.exit(f"ERROR: no code cell for step {step} in {NOTEBOOK.name}")
    source = "\n\n".join(cells)
    if lines:
        first, last = lines
        all_lines = source.splitlines()
        source = "\n".join(all_lines[first - 1:last])
        if last < len(all_lines):
            source += f"\n# ... lines {last + 1}-{len(all_lines)} of this cell not shown"
    font = ImageFont.truetype(str(FONTS / "DejaVuSansMono.ttf"), font_px)
    style = get_style_by_name("default")
    char_w = font.getbbox("M")[2]
    line_h = int(font_px * 1.35)
    lines = source.splitlines()
    width = pad * 2 + char_w * max_chars              # fixed width: every code image has the same scale
    height = pad * 2 + line_h * len(lines)
    image = Image.new("RGB", (width, height), (248, 248, 248))
    draw = ImageDraw.Draw(image)
    x, y = pad, pad
    for token, text in PythonLexer().get_tokens(source):
        colour = style.style_for_token(token)["color"] or "000000"
        for i, piece in enumerate(text.split("\n")):
            if i:
                x, y = pad, y + line_h
            if piece:
                draw.text((x, y), piece, font=font, fill="#" + colour)
                x += char_w * len(piece)
    image.save(path)
    return path


def make_code_images():
    """Render every code screenshot the report uses (CODE_FIGURES) from the hand-in notebook."""
    CODE_IMAGES.mkdir(exist_ok=True)
    return [code_image(step, CODE_IMAGES / name, contains=text) for name, (step, text) in CODE_FIGURES.items()]


def code_images(spec):
    """'A8 1-27 ; D3' -> PNG paths; each part is a lab step and an optional line range."""
    CODE_IMAGES.mkdir(exist_ok=True)
    paths = []
    for part in spec.split(";"):
        step, *rest = part.split()
        lines = tuple(int(n) for n in rest[0].split("-")) if rest else None
        paths.append(code_image(step, CODE_IMAGES / f"code_{step}.png", lines))
    return paths


# ---------------------------------------------------------------------------
# 3. PDF rendering
# ---------------------------------------------------------------------------
class Report(FPDF):
    def footer(self):
        self.set_y(-10)
        self.set_font("Sans", "", 8)
        self.set_text_color(*GREY)
        self.cell(0, 5, f"{self.page_no()}", align="C")
        self.set_text_color(0)


def inline_for_table(text):
    """Table cells use fpdf2's own markdown: **bold**, __italic__; `code` becomes plain text."""
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"__\1__", text)


def render_table(pdf, lines):
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in lines
            if not re.fullmatch(r"\|?\s*:?-{3,}.*", line.strip())]
    def text_width(cell, bold):
        pdf.set_font("Sans", "B" if bold else "", TABLE_PT)
        return pdf.get_string_width(inline_for_table(cell).replace("**", "").replace("__", "")) + 3.5

    natural = [max(text_width(r[i], n == 0) for n, r in enumerate(rows)) for i in range(len(rows[0]))]
    # Water-filling: narrow columns keep their natural width, the widest ones share what is left.
    widths, left, order = list(natural), pdf.epw, sorted(range(len(natural)), key=lambda i: natural[i])
    for rank, i in enumerate(order):
        share = left / (len(order) - rank)
        widths[i] = min(natural[i], share)
        left -= widths[i]
    pdf.set_font("Sans", "", TABLE_PT)
    table_width = sum(widths)
    with pdf.table(col_widths=widths, width=table_width, align="LEFT", markdown=True,
                   line_height=TABLE_PT * 0.45, padding=(0.6, 1.2),
                   borders_layout="HORIZONTAL_LINES", first_row_as_headings=True,
                   headings_style=FontFace(emphasis="BOLD", fill_color=(235, 235, 235)),
                   text_align="LEFT") as table:
        for r in rows:
            row = table.row()
            for cell in r:
                row.cell(inline_for_table(cell))
    pdf.ln(2.5)


def render_markdown(pdf, text):
    html = markdown.markdown(text, extensions=["sane_lists"])
    html = html.replace("<em>", "<i>").replace("</em>", "</i>")
    html = html.replace("<strong>", "<b>").replace("</strong>", "</b>")
    pdf.write_html(
        html, font_family="Sans", li_prefix_color=(0, 0, 0),
        tag_styles={
            "p": TextStyle(font_size_pt=BODY_PT, t_margin=0, b_margin=1.6),
            "li": TextStyle(font_size_pt=BODY_PT, t_margin=0, b_margin=0.4, l_margin=4),
            "h1": TextStyle(font_family="Sans", font_style="B", font_size_pt=15, t_margin=0,
                            b_margin=1.5, color=(0, 0, 0)),
            "h2": TextStyle(font_family="Sans", font_style="B", font_size_pt=11.5, t_margin=2.5,
                            b_margin=1.2, color=(0, 0, 0)),
            "h3": TextStyle(font_family="Sans", font_style="B", font_size_pt=BODY_PT + 0.5,
                            t_margin=1.5, b_margin=0.8, color=(0, 0, 0)),
            "code": TextStyle(font_family="Mono", font_size_pt=BODY_PT - 1, color=(0, 0, 0)),
        })


def render_figures(pdf, paths, caption, height_limit=50):
    paths = [ROOT / p.strip() for p in paths]
    gap = 4
    width = (pdf.epw - gap * (len(paths) - 1)) / len(paths)
    sizes = []
    for p in paths:
        w_px, h_px = Image.open(p).size
        w = width
        h = w * h_px / w_px
        if h > height_limit:                          # keep tall images within the limit
            h, w = height_limit, height_limit * w_px / h_px
        sizes.append((w, h))
    row_h = max(h for _, h in sizes)
    caption = re.sub(r"`([^`]+)`", r"\1", caption)
    pdf.set_font("Sans", "I", CAPTION_PT)
    caption_h = pdf.multi_cell(pdf.epw, CAPTION_PT * 0.42, caption, dry_run=True, output="HEIGHT")
    if pdf.get_y() + row_h + caption_h + 2 > pdf.page_break_trigger:
        pdf.add_page()
    y = pdf.get_y()
    x = pdf.l_margin
    for p, (w, h) in zip(paths, sizes):
        pdf.image(str(p), x=x + (width - w) / 2, y=y + (row_h - h) / 2, w=w, h=h)
        x += width + gap
    pdf.set_y(y + row_h + 1)
    pdf.set_text_color(*GREY)
    pdf.multi_cell(pdf.epw, CAPTION_PT * 0.42, caption, markdown=True)
    pdf.set_text_color(0)
    pdf.ln(2.5)


IMAGE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def image_line(line):
    """Image paths (relative to the repository root) if the line holds only images, else None."""
    stripped = line.strip()
    if not stripped.startswith("![") or IMAGE.sub("", stripped).strip():
        return None
    return [str((REPORT_DIR / p).resolve().relative_to(ROOT)) for p in IMAGE.findall(stripped)]


def main():
    text = expand(SOURCE.read_text(encoding="utf-8"))
    make_code_images()

    pdf = Report(format="A4")
    pdf.set_margins(MARGIN, MARGIN, MARGIN)
    pdf.set_auto_page_break(True, margin=14)
    pdf.add_font("Sans", "", str(FONTS / "LiberationSans-Regular.ttf"))
    pdf.add_font("Sans", "B", str(FONTS / "LiberationSans-Bold.ttf"))
    pdf.add_font("Sans", "I", str(FONTS / "LiberationSans-Italic.ttf"))
    pdf.add_font("Sans", "BI", str(FONTS / "LiberationSans-BoldItalic.ttf"))
    for style in ("", "B", "I", "BI"):                 # code inside bold/italic text: same mono font
        pdf.add_font("Mono", style, str(FONTS / "DejaVuSansMono.ttf"))
    pdf.set_title("Lab 4.2: Robustness, Attacks and Honest Explanations")
    pdf.add_page()

    pending, table = [], []
    page_breaks = []

    def flush():
        if pending:
            render_markdown(pdf, "\n".join(pending))
            pending.clear()

    lines = text.splitlines() + [""]
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if table and not line.lstrip().startswith("|"):
            render_table(pdf, table)
            table.clear()
        if line.lstrip().startswith("|"):
            flush()
            table.append(line)
        elif line.strip() == "<!-- pagebreak -->":
            flush()
            page_breaks.append(pdf.page_no())
            pdf.add_page()
        elif (paths := image_line(line)) is not None:
            flush()
            caption = ""
            if index < len(lines) and lines[index].strip().startswith("*Figure"):
                caption = lines[index].strip().strip("*")
                index += 1
            tall = any("code_" in p for p in paths)
            render_figures(pdf, paths, caption, height_limit=250 if tall else 62)
        else:
            pending.append(line)
    flush()

    pdf.output(str(OUTPUT))
    main_pages = page_breaks[0] if page_breaks else pdf.page_no()
    print(f"Wrote {OUTPUT.relative_to(ROOT)}: {pdf.page_no()} pages "
          f"({main_pages} before the appendix)")


if __name__ == "__main__":
    main()
