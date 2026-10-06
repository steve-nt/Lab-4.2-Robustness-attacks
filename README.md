# Lab 4.2: Robustness, Attacks and Honest Explanations

AI for Cybersecurity (D7084E / D7041E), Group 6: Kirill Silchenko (kirsil-5@student.ltu.se) and
Stefanos Ntentopoulos (stente-5@student.ltu.se).

We test network-flow intrusion detectors (decision tree, logistic regression, random forest) on the
CICIDS2017 data from Lab 1. We measure how their scores survive measurement noise and missing fields,
and how many attacks a greedy evasion attack can hide, both within what a real attacker controls and
with no limits. We then compare SHAP's important features with what the attacker changed, and try two
defences: an ensemble, and finding which feature groups carry the real information. Finally we test
whether SHAP and LIME explanations are stable and faithful.

- **Notebook to hand in:** `lab4_2_robustness_attacks.ipynb`. It runs from top to bottom and holds
  lab steps A0–F3 in order (A0 is the setup), plus a few extra checks at the end.
- **Report:** Lab 4.2 _Robustness_Attacks_and_Honest_Explanations.pdf

## Dataset

The cleaned CICIDS2017 table from Lab 1 (`data/processed/clean.csv`): 446,641 flows, 68 numeric
features and the label, all eight day-files, 20% stratified sample. It is **not in git** (150 MB, over
GitHub's file limit). `data/README.md` says where it comes from, gives its SHA-256 hash, and explains
how to rebuild it from the raw CICIDS2017 files with `lab1_pipeline/clean.py`.

Source: Canadian Institute for Cybersecurity, CICIDS2017,
https://www.unb.ca/cic/datasets/ids-2017.html (Sharafaldin, Lashkari & Ghorbani, ICISSP 2018).

## Setup

```bash
uv venv --python 3.13 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
sha256sum data/processed/clean.csv      # must match the hash in data/README.md
```

Python 3.13 (3.11–3.13 should work). Pinned versions: scikit-learn 1.6.1, shap 0.52.0, lime 0.2.0.1,
numpy 2.5.3, pandas 3.0.6, scipy 1.18.1, matplotlib 3.11.2, plus Jupyter, nbformat and nbconvert.
fpdf2 and markdown are only needed to build the report PDF. No `uv`? Install it with
`curl -LsSf https://astral.sh/uv/install.sh | sh`.

## How to run

Run every command from the repository root, with the environment active.

| What | Command | Time (8 cores) |
|---|---|---|
| Run the hand-in notebook, top to bottom | `jupyter nbconvert --to notebook --execute --inplace lab4_2_robustness_attacks.ipynb` (or *Run All* in Jupyter) | about 61 min (first run) |
| Rebuild the hand-in notebook from the part notebooks, and run it | `python tools/assemble.py --strict` | about 61 min (first run) |
| Check that the report's numbers match the last run | `python tools/check_report_numbers.py` | seconds |

**Run time.** The first run trains four models and saves them in `models/` (not in git). Later runs
load them. A full run from scratch (all models retrained) took about 61 minutes (3,666 s) on an 8-core machine with 9 GB RAM. With the models already saved it should take roughly half an hour (estimated from the run times of the part notebooks, not measured as one run). The slowest parts are
training the forest and gradient boosting, SHAP on 500 flows (step D1), and the 88 retrained forests of
step E2. Delete `models/*.joblib` to force retraining. `random_state=42` is used everywhere, so a rerun
gives the same numbers.

**Google Colab:** upload the notebook and `clean.csv` and run all cells; the first cell installs shap
and lime if they are missing, and the notebook uses `clean.csv` next to it when `data/processed/` does
not exist.

## How the code is organised

We worked in separate part notebooks, so that nobody edits the same file. Each cell starts with the
lab step it belongs to (`# STEP C2`). Cells that only stand in for another notebook's step during
development are marked `# STANDIN`. `tools/assemble.py` collects the `STEP` cells from all part
notebooks, puts them in lab order, drops the stand-ins, and writes and runs the hand-in notebook.

| Path | Contents |
|---|---|
| `parts/00_setup.ipynb` | Setup (step A0): data, split, the three models, shared helpers and samples |
| `parts/10_baseline_noise.ipynb` | Part A (baseline) and Part B (noise, missing values) |
| `parts/20_attack.ipynb` | Part C (evasion attack), step D1 (SHAP vs attacker), step E1 (ensemble) |
| `parts/30_explanations.ipynb` | Step D2 (SHAP stability), step E2 (feature removal), Part F (explanation checks) |
| `tools/assemble.py` | Builds and runs the hand-in notebook from the part notebooks |
| `tools/feature_glossary.py` | Plain-language meaning, unit and twin group of all 68 features |
| `tools/check_report_numbers.py` | Compares the numbers in the report with the CSV files of the last run |
| `lab1_pipeline/` | Lab 1's loading, cleaning and splitting code (reference; rebuilds `clean.csv`) |
| `results/tables/`, `results/figures/` | Every table and figure, named after the lab step that made it |
| `models/` | Saved models (created by the first run, not in git) |
