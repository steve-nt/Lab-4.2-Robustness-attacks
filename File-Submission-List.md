# Files for submission

The lab asks for two uploads on Canvas: **the report as a PDF** and **the code** (a zip or a repository
link). The code must be one notebook that runs from top to bottom, plus a short README (libraries,
dataset, how to run), with `random_state=42`.

The committed project is 74 files; a zip of it is about 3.9 MB (measured 2026-10-05). The `.venv`,
`PreviousLabs/`, `models/` and the dataset CSV are not in git and stay out unless noted below.

## 1. The report (upload as PDF)

| File | What to do |
|---|---|
| `report/Lab4_2_Report.pdf` | **Upload this.** 4 pages: 3 pages of report + a 1-page code appendix (the required code screenshot) |
| `report/Lab4_2_Report.docx` | The same report in Word, with our title page. Upload it only if a Word file is wanted; it also ships in the code zip |
| `report/Lab4_2_Report.md` | The same report in Markdown: the file both of the above are built from |

If you edit the text, change `report/Lab4_2_Report.md`, then rebuild and re-check:

```bash
.venv/bin/python report/build_report.py
.venv/bin/python report/build_docx.py
.venv/bin/python tools/check_report_numbers.py
```

## 2. The code (zip these, or submit the repository link)

| Path | Why it is needed |
|---|---|
| `lab4_2_robustness_attacks.ipynb` | **The notebook the lab asks for**: steps A0–F3 in order plus a few extra checks at the end. It runs top to bottom (about 61 min from scratch) and is stored with its outputs |
| `README.md` | Libraries and versions, dataset, how to run (locally and in Colab), run time, seed |
| `requirements.txt` | Pinned versions (scikit-learn 1.6.1, shap 0.52.0, lime 0.2.0.1, …) |
| `data/README.md` | Where the dataset comes from, its SHA-256 hash, and how to rebuild it |
| `lab1_pipeline/` | Lab 1's cleaning and splitting code, which produced the dataset |
| `results/tables/`, `results/figures/` | Every table and figure the notebook writes and the report cites |
| `parts/` (4 notebooks), `tools/assemble.py` | How the hand-in notebook is built: the part notebooks and the script that joins them in lab order |
| `tools/check_report_numbers.py` | Shows that every number in the report matches the notebook run |
| `tools/feature_glossary.py` | Plain-language meaning of all 68 features (used to read the results) |
| `report/` (the three report files above, `build_report.py`, `build_docx.py`, `title_page_template.docx`, `fonts/`, `figures/`) | The report and how the PDF and Word files are generated from it |
| `.gitignore` | Keeps the environment, data, models and previous labs out of the repository |

**The dataset.** `data/processed/clean.csv` (150 MB, 50 MB zipped) is **not in git** and therefore not
in a zip made with `git archive`. Without it nobody can rerun the notebook (the stored outputs can still
be read). Two options:

- **Leave it out** (default): `data/README.md` explains where to get it and how to rebuild it.
- **Add it** to the zip if Canvas accepts about 54 MB in total (see section 5).

Optional, not required by the lab but useful to a reader:

| Path | What it is |
|---|---|
| `CHANGELOG.md` | The history of every change, with dates and reasons |
| `TASKLIST.md` | The plan we worked to |

## 3. Do not submit

| Path | Reason |
|---|---|
| `.venv/` | Local Python environment; `requirements.txt` replaces it |
| `PreviousLabs/` | Copies of earlier labs, already submitted with those labs; git-ignored |
| `models/` | Saved models (about 28 MB); the notebook retrains them; git-ignored |
| `.git/` | Only needed if you submit the repository link instead of a zip |
| `Robustness attacks.pdf`, `Robustness attacks.txt` | The assignment instructions, not our work |
| `File-Submission-List.md` | This checklist |
| `__pycache__/`, `.ipynb_checkpoints/` | Caches; git-ignored |

## 4. Before zipping

- [ ] **Fill in section 5 "Who did what"** in `report/Lab4_2_Report.md`: it is still a placeholder.
      Then rebuild the PDF and the Word file (section 1).
- [ ] Read the report PDF once more, including the AI-use statement.
- [ ] Commit and push everything, so that the zip and the repository link match.
- [ ] Merge `stente-5` into `main`, so that the repository link shows the final version.

Already done (2026-10-05): the hand-in notebook was built and run from scratch with all models
retrained, without errors (3,666 s). `tools/check_report_numbers.py` confirms all 80 numbers in the
report against that run.

## 5. Making the zip

From the repository root, after committing, this packs exactly the committed files. The environment,
previous labs, models, dataset, caches and `.git` stay out automatically:

```bash
git archive --format=zip --prefix=Lab4_2_Group6/ -o ../Lab4_2_Group6_code.zip HEAD
```

To remove the files listed in section 3 as "do not submit" (the instructions and this checklist):

```bash
zip -d ../Lab4_2_Group6_code.zip \
  "Lab4_2_Group6/Robustness attacks.pdf" \
  "Lab4_2_Group6/Robustness attacks.txt" \
  "Lab4_2_Group6/File-Submission-List.md"
```

Optional, to include the dataset so that the zip runs without a download (adds about 50 MB):

```bash
mkdir -p /tmp/zipdata/Lab4_2_Group6/data/processed
cp data/processed/clean.csv /tmp/zipdata/Lab4_2_Group6/data/processed/
(cd /tmp/zipdata && zip -r -9 "$OLDPWD/../Lab4_2_Group6_code.zip" Lab4_2_Group6)
```

Then upload `../Lab4_2_Group6_code.zip` and `report/Lab4_2_Report.pdf` to Canvas.
