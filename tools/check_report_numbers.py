"""Check that the numbers written in report/Lab4_2_Report.md match the last notebook run.

The report states its numbers in plain text, so it stays readable as Markdown. This script holds every
number the report uses, where it comes from, and how it is rounded in the text, and compares them with:
  - the CSV files the hand-in notebook writes to results/tables/ (most numbers), and
  - the printed output of the executed hand-in notebook (a few numbers that are only printed).
It also checks that each expected number really appears in the report text.

Run from the repository root after running lab4_2_robustness_attacks.ipynb:
    .venv/bin/python tools/check_report_numbers.py
"""
import sys
from pathlib import Path

import nbformat
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "results" / "tables"
REPORT = ROOT / "report" / "Lab4_2_Report.md"
NOTEBOOK = ROOT / "lab4_2_robustness_attacks.ipynb"


def csv(name, **kw):
    return pd.read_csv(TABLES / f"{name}.csv", **kw)


def row(df, **where):
    mask = pd.Series(True, index=df.index)
    for column, value in where.items():
        mask &= df[column] == value
    assert mask.sum() == 1, f"{where} matches {mask.sum()} rows"
    return df[mask].iloc[0]


a2 = csv("A2_baseline").set_index("model")
b1 = csv("B1_noise")
b2 = csv("B2_missing").set_index("model")
x1 = csv("X1_group_missing")
c2 = csv("C2_attack_comparison").set_index("run")
e1 = csv("E1_ensemble", index_col=0)
e1_attack = csv("E1_ensemble_attack_per_flow")
d2 = csv("D2_stability_by_level").set_index("noise level")
d2_split = csv("D2_stability_split").set_index("noise level")
f1 = csv("F1_deletion", index_col=[0, 1])
f1_flow = csv("F1_deletion_per_flow")
f3 = csv("F3_lime_fit")
e2_single = csv("E2_single_removal").set_index("feature")
e2_group = csv("E2_group_removal")
e2_block = csv("E2_block_removal").set_index("removed")
c3 = csv("C3_attack_counts").set_index("feature")
per_flow = csv("C2_attack_per_flow")

noise5 = lambda model, metric: row(b1, clip=True, level=0.05, model=model)[metric]
twins = f1_flow[f1_flow["group_size"] > 1]
rand = f3[f3["group"] == "random"]
evaded = per_flow[(per_flow["run"] == "constrained") & per_flow["evaded"]]

# (what the report says, the value from the run, decimals used in the report text)
CHECKS = [
    ("always-benign accuracy", a2.loc["always benign", "accuracy"], 3),
    ("always-benign macro-F1", a2.loc["always benign", "macro_f1"], 3),
    ("always-benign PR-AUC", a2.loc["always benign", "pr_auc"], 3),
    ("tree accuracy", a2.loc["tree", "accuracy"], 3),
    ("tree macro-F1", a2.loc["tree", "macro_f1"], 3),
    ("tree recall", a2.loc["tree", "recall"], 3),
    ("tree ROC-AUC", a2.loc["tree", "roc_auc"], 3),
    ("tree PR-AUC", a2.loc["tree", "pr_auc"], 3),
    ("logreg accuracy", a2.loc["logreg", "accuracy"], 3),
    ("logreg macro-F1", a2.loc["logreg", "macro_f1"], 3),
    ("logreg recall", a2.loc["logreg", "recall"], 3),
    ("logreg ROC-AUC", a2.loc["logreg", "roc_auc"], 3),
    ("logreg PR-AUC", a2.loc["logreg", "pr_auc"], 3),
    ("forest accuracy", a2.loc["forest", "accuracy"], 3),
    ("forest macro-F1", a2.loc["forest", "macro_f1"], 3),
    ("forest recall", a2.loc["forest", "recall"], 3),
    ("forest ROC-AUC", a2.loc["forest", "roc_auc"], 3),
    ("forest PR-AUC", a2.loc["forest", "pr_auc"], 3),
    ("forest accuracy margin over always-benign", a2.loc["forest", "accuracy"] - a2.loc["always benign", "accuracy"], 3),
    ("forest recall at 5% noise", noise5("forest", "recall"), 3),
    ("tree recall at 5% noise", noise5("tree", "recall"), 3),
    ("logreg recall at 5% noise", noise5("logreg", "recall"), 3),
    ("logreg macro-F1 loss at 5% noise", a2.loc["logreg", "macro_f1"] - noise5("logreg", "macro_f1"), 3),
    ("forest macro-F1 at 10% missing", b2.loc["forest", "macro_f1"], 3),
    ("forest recall at 10% missing", b2.loc["forest", "recall"], 3),
    ("tree macro-F1 at 10% missing", b2.loc["tree", "macro_f1"], 3),
    ("logreg macro-F1 at 10% missing", b2.loc["logreg", "macro_f1"], 3),
    ("logreg recall at 10% missing", b2.loc["logreg", "recall"], 3),
    ("forest recall, all backward missing", row(x1, scenario="all backward (17)", model="forest")["recall"], 3),
    ("forest recall, 17 random missing", row(x1, scenario="random 17 per row", model="forest")["recall"], 3),
    ("constrained evaded", c2.loc["constrained", "evaded (of 50)"], 0),
    ("constrained mean p after", c2.loc["constrained", "mean p after"], 3),
    ("constrained mean features changed", c2.loc["constrained", "mean features changed"], 2),
    ("unconstrained evaded", c2.loc["unconstrained", "evaded (of 50)"], 0),
    ("unconstrained mean p after", c2.loc["unconstrained", "mean p after"], 3),
    ("unconstrained mean features changed", c2.loc["unconstrained", "mean features changed"], 2),
    ("ensemble evaded", int(e1_attack["evaded"].sum()), 0),
    ("ensemble mean p after", e1_attack["p_after"].mean(), 3),
    ("ensemble mean features changed", e1_attack["n_features_changed"].mean(), 2),
    ("constrained DDoS evaded", int((evaded["attack_type"] == "DDoS").sum()), 0),
    ("lowest evaded probability", evaded["p_after"].min(), 2),
    ("highest evaded probability", evaded["p_after"].max(), 2),
    ("timing steps in evasions", int(c3.loc[[f for f in c3.index if any(k in f for k in ("IAT", "Idle", "Active", "Duration"))], "steps_in_evaded"].sum()), 0),
    ("all steps in evasions", int(c3["steps_in_evaded"].sum()), 0),
    ("ensemble clean macro-F1", e1.loc["ensemble", "clean macro-F1"], 3),
    ("ensemble 5% noise macro-F1", e1.loc["ensemble", "5% noise macro-F1"], 3),
    ("forest 5% noise macro-F1", e1.loc["forest", "5% noise macro-F1"], 3),
    ("ensemble 10% missing macro-F1", e1.loc["ensemble", "10% missing macro-F1"], 3),
    ("SHAP Spearman clean vs 5%", d2.loc[0.05, "spearman"], 3),
    ("SHAP Spearman top-20 at 5%", d2_split.loc[0.05, "all 200 flows, clean top-20 features"], 3),
    ("deletion top-1", f1.loc[("top-k vs random-k", "1"), "mean drop, SHAP top-k"], 3),
    ("deletion top-3", f1.loc[("top-k vs random-k", "3"), "mean drop, SHAP top-k"], 3),
    ("deletion top-5", f1.loc[("top-k vs random-k", "5"), "mean drop, SHAP top-k"], 3),
    ("deletion random-1", f1.loc[("top-k vs random-k", "1"), "mean drop, random-k"], 3),
    ("deletion random-3", f1.loc[("top-k vs random-k", "3"), "mean drop, random-k"], 3),
    ("deletion random-5", f1.loc[("top-k vs random-k", "5"), "mean drop, random-k"], 3),
    ("deletion below 0.5, k=5", f1.loc[("top-k vs random-k", "5"), "flows below 0.5 after top-k"], 0),
    ("flows whose top feature has twins", len(twins), 0),
    ("twins: drop alone", twins["drop_single"].mean(), 2),
    ("twins: drop with direct twins", twins["drop_group"].mean(), 2),
    ("twins: drop with chained family", twins["drop_family"].mean(), 2),
    ("twins: below 0.5 with family", int((twins["drop_family"] > 0.5).sum()), 0),
    ("LIME min R2", rand["lime_r2"].min(), 3),
    ("LIME max R2", rand["lime_r2"].max(), 3),
    ("LIME mean R2", rand["lime_r2"].mean(), 3),
    ("E2 largest single drop", e2_single["macro_f1_drop"].max(), 4),
    ("E2 singles above noise band", int(e2_single["outside_noise_band"].sum()), 0),
    ("E2 largest group drop", e2_group["macro_f1_drop"].max(), 4),
    ("E2 number of groups", len(e2_group), 0),
    ("E2 all backward", e2_block.loc["all backward features", "macro_f1_drop"], 4),
    ("E2 all forward", e2_block.loc["all forward features", "macro_f1_drop"], 4),
    ("E2 all timing", e2_block.loc["all timing features", "macro_f1_drop"], 4),
]

# Numbers that are only printed by the notebook: the exact text must appear in its output.
PRINTED = [
    ("forest recall at noise level 0.001", "level 0.001   forest 0.794"),
    ("tree recall at noise level 0.001", "tree 0.500"),
    ("noise band of the retrained forests", "(band 0.0008)"),
    ("SHAP rank of Fwd IAT Min", "Fwd IAT Min                    Free             7                7         41"),
    ("SHAP rank of Flow IAT Min", "Flow IAT Min                   Free             7                7         58"),
    ("share of SHAP weight on Fixed features", "'Fixed': 0.774"),
    ("additivity difference", "Largest difference: 4.44e-16"),
    ("unconstrained steps on Fixed features", "87% of them on Fixed features"),
]


def rounded(value, decimals):
    return f"{value:.{decimals}f}" if decimals else f"{int(round(value))}"


def main():
    report = REPORT.read_text(encoding="utf-8")
    problems = []
    for label, value, decimals in CHECKS:
        text = rounded(float(value), decimals)
        # Accept the report's rounding of a value stored with 4 decimals (e.g. 0.9985 -> 0.998 or 0.999).
        alternatives = {text, rounded(float(value) + 0.5 * 10 ** -(decimals + 1), decimals),
                        rounded(float(value) - 0.5 * 10 ** -(decimals + 1), decimals)} if decimals else {text}
        if not any(t in report for t in alternatives):
            problems.append(f"{label}: run gives {value!r} -> expected '{text}' in the report, not found")
    outputs = ""
    for cell in nbformat.read(NOTEBOOK, as_version=4).cells:
        if cell.cell_type == "code":
            for out in cell.get("outputs", []):
                outputs += out.get("text", "") + str(out.get("data", {}).get("text/plain", ""))
    for label, text in PRINTED:
        if text not in outputs:
            problems.append(f"{label}: '{text}' not found in the notebook output")
    print(f"Checked {len(CHECKS)} values from results/tables/ and {len(PRINTED)} printed values.")
    if problems:
        print("MISMATCHES:\n  " + "\n  ".join(problems))
        sys.exit(1)
    print("All numbers in the report match the last run.")


if __name__ == "__main__":
    main()
