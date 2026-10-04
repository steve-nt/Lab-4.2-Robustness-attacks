# Changelog

History of the changes made in this project, oldest first. Each entry says what changed, why,
and when. New entries are appended at the bottom.

## 2026-10-04 13:24 EEST: Task list and self-contained project setup

**What**
- `TASKLIST.md`: written (was empty). Glossary for readers with no background, starting point and
  differences between our data and the PDF, the parallel-work method (part notebooks, step markers,
  stand-ins, shared names), task overview, three work tracks with sync points, and detailed tasks
  T1–T7, A1–F3 and extras X1–X6
- `data/processed/clean.csv`: copied from Lab 1 (cleaned CICIDS2017, 446,641 rows, 68 features)
- `data/README.md`: created; where the data comes from, its SHA-256, how to rebuild it
- `lab1_pipeline/`: copied Lab 1's `config.py`, `explore.py`, `clean.py`, `prepare.py`, `metrics.py`
- `requirements.txt`: copied from Lab 4.1 (pinned versions), header changed to Lab 4.2
- `tools/assemble.py`: copied from Lab 4.1 (still has Lab 4.1's step order; task T2 adapts it)
- `report/build_report.py`, `report/build_docx.py`, `report/title_page_template.docx`,
  `report/fonts/`: copied from Lab 4.1 (task T5 adapts them)
- `parts/`, `models/`, `results/figures/`, `results/tables/`, `data/raw/`: created with `.gitkeep`
- `.gitignore`: removed the phishing-data comment; ignores `data/processed/*.csv`, `data/raw/*.csv`
  and `models/*.joblib`

**Why**
The user asked for a step-by-step task list that people with no background can split between them,
and for the lab to work without `PreviousLabs/`. Only `clean.csv` was copied, not the 844 MB raw
files, because the Lab 1 split rebuilds exactly from it. The data files are git-ignored because
`clean.csv` (150 MB) is over GitHub's file-size limit.

**Verified**
Rebuilt the split from `clean.csv` with Lab 1's code: the row indices and values match Lab 1's
`splits.joblib` exactly (267,984 / 89,328 / 89,329 rows). Checked that the feature-group rules give
25 Free / 5 Costly / 38 Fixed features. Checked with shap 0.52 that the forest's SHAP values add up
to the probability, while gradient boosting's add up to log-odds.
