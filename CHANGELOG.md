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

## 2026-10-04 13:48 EEST: T2, environment and assembly script

**What**
- `.venv/`: created with Python 3.13.7 and `requirements.txt` installed (scikit-learn 1.6.1,
  shap 0.52.0, lime 0.2.0.1, numpy 2.5.3, pandas 3.0.6, scipy 1.18.1, Jupyter, nbformat, nbconvert)
- `tools/assemble.py`: output file is now `lab4_2_robustness_attacks.ipynb`; step order is
  A0, A1, A2, B1, B2, C1-C3, D1, D2, E1, E2, F1-F3, then X1-X6; Lab 4.2 title cell; error and
  help messages name steps A0-F3
- `TASKLIST.md`: T2 checkboxes ticked; overview row marked done for this machine

**Why**
Task T2: everyone needs the same library versions, and the assembly script must sort this lab's
steps. The title keeps the Lab 4.1 group members; this has not been confirmed for this lab.

**Verified**
All libraries import with the pinned versions. `clean.csv` matches the SHA-256 in
`data/README.md`. On two throwaway notebooks in a temporary folder, the script put the cells in
lab order (A0, C2, F1), dropped the STANDIN cell, listed the missing steps, and ran the result top
to bottom. The test folder was then deleted, so `parts/` holds only `.gitkeep`.

## 2026-10-04 14:25 EEST: T3, setup notebook (step A0)

**What**
- `parts/00_setup.ipynb`: created, 14 cells, all marked `STEP A0`, saved with the outputs of a
  cached run. It installs shap/lime only if missing, loads `data/processed/clean.csv`, rebuilds
  Lab 1's 60/20/20 split (with asserts on the sizes), and builds the shared names: `FEATURES`,
  `CONT_COLS` (58), `FLAG_COLS` (10), `TRAIN_STD`, `TRAIN_MEDIAN`, `CORR`, `report()` (adds
  PR-AUC and FAR), `tree`, `logreg` (scaler inside a Pipeline), `rf` (300 trees, depth 20),
  `MODELS`, `ATTACK_IDX`, `EXPLAIN_IDX`, `rf_proba_test` and `type_train/val/test`
- `models/tree.joblib`, `models/logreg.joblib`, `models/forest.joblib`: trained and saved (not in
  git); the notebook loads them when they match the features, otherwise it retrains
- `TASKLIST.md`: added `type_*` and `rf_proba_test` to the shared names (section 2.3); T3 ticked
  apart from the merge, with run times, the clean scores and the `ATTACK_IDX` observation

**Why**
Task T3: every part notebook starts with `%run 00_setup.ipynb`. Three choices made while testing:
- One warning is silenced: scikit-learn 1.6.1 passes an option ("iprint") that newer scipy no
  longer knows, and the warning is harmless.
- The correlation table uses `np.corrcoef` (42 s down to 6 s, same numbers).
- The model scoring table moved to step A2, saving about 40 s per run.

**Verified**
- First run trained all three models in about 22 minutes. Forest macro-F1 0.9968 on the test set,
  identical to Lab 1.
- A run with the saved models takes 92 s with no warnings or errors.
- A test notebook that ran `%run 00_setup.ipynb` from `parts/` got every shared name; the test
  notebook was then deleted.
- All 50 `ATTACK_IDX` flows have forest probability 1.000.

## 2026-10-04 14:42 EEST: T4, feature glossary

**What**
- `tools/feature_glossary.py`: created. Holds a plain-language meaning and unit for each of the 68
  features. It measures direction, distinct values, min/median/max, negative values and twin groups
  (|corr| > 0.95, chained) on the training split. It also proposes Free/Costly/Fixed groups with the
  C1 name rules
- `results/tables/T4_feature_glossary.csv` and `results/tables/T4_feature_glossary.md`: generated by
  the script
- `TASKLIST.md`: T4 ticked, with its result. Notes added to C1 (twins move together in real
  traffic), D1 (Fixed features with changeable twins) and F1 (where to find the twin groups). The
  PDF's four-`Fwd Packet Length`-twins example was corrected to what our data shows

**Why**
Task T4: the team has no networking background, and every result in the lab is a list of feature
names. The twin groups are measured rather than guessed, because E2 and F1 depend on them. Two of
the 14 groups mix features the attacker controls with features they do not, which affects how C1,
D1 and F1 should be read.

**Verified**
The script asserts the split size (267,984 training rows) and that every data column has a meaning
(68 of 68). The proposed groups give 25 Free / 5 Costly / 38 Fixed, the same as the check on
2026-10-04 13:24. The 10 flag columns have exactly 2 distinct values.

## 2026-10-04 15:01 EEST: A1 and A2, data health and baseline

**What**
- `parts/10_baseline_noise.ipynb`: created (Track 1 notebook), saved with outputs. Cell 1 is
  `# STANDIN A0` (`%run 00_setup.ipynb`). A1 prints shapes, the attack share and the finite check
  for all three parts (with the median-fill fix ready if ever needed), counts continuous and flag
  columns, and lists negative and heavy-tailed columns. A2 scores `DummyClassifier(constant=0)`,
  tree, logreg and forest with `report()`, asserts the always-benign accuracy is `1 - y_test.mean()`,
  and answers the two "Check yourself" questions with the numbers
- `results/tables/A1_data_health.csv`, `results/tables/A2_baseline.csv`: written by the notebook
- `TASKLIST.md`: A1 and A2 ticked, with results

**Why**
Lab steps A1 and A2. The always-benign model is a `DummyClassifier` so it goes through the same
`report()` as the real models. The negative and heavy-tail check was added because B1 must decide
whether to clip noise at zero.

**Verified**
Notebook ran top to bottom in 174 s with no errors. The scores match the T3 run. All
cells have step markers. `tools/assemble.py --no-execute` places A0, A1, A2 in order. The generated
notebook was deleted afterwards because it is only built at sync 3.

## 2026-10-04 15:38 EEST: B1, B2 (and extras X1, X2), noise and missing values

**What**
- `parts/10_baseline_noise.ipynb`: added steps B1, B2, X1 and X2 (now 27 cells, saved with outputs)
  - B1: `add_noise(X, X_ref, level, seed=SEED, clip=True)`. The std comes from the reference
    (training) set; flags are left alone; columns that are never negative in training are clipped
    at zero. All three models are scored at 0/5/10/20/50% noise, with the figure. A diagnostic cell
    shows why the tree models collapse (outlier-inflated std), and the "Check yourself" answers
    are written up
  - X2: the same run without clipping, side by side
  - B2: `add_missing(X, frac, seed=SEED)` puts training medians into 7 of 68 random features per row.
    It is scored at 10% and compared with clean data and 5% noise
  - X1: whole groups missing (all 17 backward features, all 4 idle timers), compared with random
    missing values of the same size
- `results/tables/B1_noise.csv`, `B2_missing.csv`, `X1_group_missing.csv`,
  `X2_clip_vs_noclip.csv`, `results/figures/B1_noise_curves.png`: written by the notebook
- `TASKLIST.md`: B1, B2, X1, X2 ticked with results, plus a note for D2 and E1 (both reuse 5% noise)

**Why**
Lab steps B1 and B2. X1 and X2 were added because the "Check yourself" questions of B2 and B1 ask
exactly what they measure. The figure follows the dataviz palette: fixed colour per model, plus
marker shape and direct labels, because the aqua line is below 3:1 contrast. The result goes against
the lab text (the forest collapses at 5% noise). It was traced to the heavy tails rather than
explained away. Diagnosis:
- noise on one column at a time costs < 0.01 recall each;
- recall falls steadily as more columns get noise;
- even a level of 0.0005 drops the forest to 0.86 recall;
- noise scaled by the IQR leaves it about 0.75.

**Verified**
Notebook ran top to bottom without errors or warnings (449 s). Assertions pass: flags untouched,
level 0 is a no-op, clipped columns are never negative, at most 7 changes per row in `add_missing`.
The figure was checked by eye after moving the legend off the lines.

## 2026-10-04 15:38 EEST: Correction, TASKLIST.md had duplicated sections

**What**
- `TASKLIST.md`: rebuilt from the clean version in commit 4cff7c5. The A1, A2, B1, B2, X1, X2 edits
  were re-applied with a helper that looks for headings only inside "## 3. Tasks in detail" and
  checks each one occurs exactly once

**Why**
The entry "A1 and A2, data health and baseline" above was wrong about `TASKLIST.md`. The edit cut
the file at the first "### Part B: break the data by accident", which is in the task overview, not
in section 3. As a result, the overview through A1 was duplicated (≈ 294 extra lines) and the A2
result text was lost. That version was committed as 9f3dee2. This turn's first B1/B2 edit repeated
the mistake with the Part C heading, and was replaced by the rebuild.

**Verified**
The diff against 4cff7c5 contains only the intended ticks and result notes (70 lines added,
23 changed). Each of "## Task overview", "## 3. Tasks in detail" and the A1, A2, B1, B2, C1, T7
headings now occurs exactly once (1,042 lines).
