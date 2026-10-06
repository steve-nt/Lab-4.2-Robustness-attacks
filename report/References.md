# References for the Lab 4.2 report

What each reference is, where it applies in our work (lab step and notebook), and which sentence of
`report/Lab4_2_Report.md` it supports. The "Status" line says how sure we are of the citation details.

The report currently has no references section. Suggested place: under the code figure on the appendix
page, so the report itself stays at 3 pages.

---

## Quick map: report section → references

| Report section | Paragraph | References |
|---|---|---|
| 2. Setup | Data | [2], [3], [10] |
| 2. Setup | Models | [7], [8], [9] |
| 2. Setup | Feature groups for the attack | [1], [14] |
| 3. Results | Baseline | [11], [12] |
| 3. Results | Noise and missing values | [10] |
| 3. Results | Evasion attack | [13], [14] |
| 3. Results | SHAP versus the attacker | [4], [5] |
| 3. Results | Do the explanations hold up? | [4], [5], [6], [15] |
| 3. Results | Feature removal with retraining | [15] |
| 4. Discussion | How much of the score is real? | [10], [11], [12] |
| 4. Discussion | How much robustness comes from the network? | [12], [13], [14] |
| 4. Discussion | Are the explanations stable and faithful? | [5], [6], [15] |
| 5. Use of AI | AI-use statement | [16] |

---

## Core: the methods and data we used directly

### [1] The lab assignment and course material

Lab 4.2: Robustness, Attacks and Honest Explanations (assignment text), and the course material in
Canvas, AI for Cybersecurity (D7084E / D7041E).

- **What it is:** the instructions we followed: the steps A1–F3, the definitions of noise, missing
  values, the Free / Costly / Fixed feature groups, the greedy attack, the deletion test, and the
  0.90 stability and 0.70 LIME-fit thresholds.
- **Where we use it:** the whole notebook. The feature groups (step C1), the attack budget (half a
  standard deviation, five changes) and the stability threshold (step D2) come straight from it.
- **In the report:** Setup ("Feature groups for the attack", Table 1); Results wherever a threshold
  is compared (0.90 in "SHAP versus the attacker", 0.70 in "Do the explanations hold up?").
- **Status:** our course document; no external details to check.

### [2] Sharafaldin, Lashkari & Ghorbani (2018): the CICIDS2017 paper

Sharafaldin, I., Lashkari, A. H., & Ghorbani, A. A. (2018). Toward generating a new intrusion
detection dataset and intrusion traffic characterization. *Proceedings of the 4th International
Conference on Information Systems Security and Privacy (ICISSP 2018)*, 108–116.

- **What it is:** the paper that created the CICIDS2017 dataset: how the traffic was recorded, which
  attacks were run, and how the 80-odd flow features were computed with the CICFlowMeter tool.
- **Where we use it:** all of our data (Lab 1's cleaned table, setup step A0). It also explains what
  the feature names mean (forward / backward, inter-arrival times, idle and active timers).
- **In the report:** Setup, "Data" ("The cleaned CICIDS2017 table from Lab 1 …").
- **Status:** well known; details as given.

### [3] CICIDS2017 dataset web page

Canadian Institute for Cybersecurity. Intrusion Detection Evaluation Dataset (CIC-IDS2017).
https://www.unb.ca/cic/datasets/ids-2017.html

- **What it is:** the download page for the raw CSV files we cleaned in Lab 1.
- **Where we use it:** `data/README.md` and the README point to it for rebuilding `clean.csv`.
- **In the report:** Setup, "Data", next to [2].
- **Status:** URL checked when the project was set up.

### [4] Lundberg & Lee (2017): SHAP

Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *Advances
in Neural Information Processing Systems 30 (NeurIPS 2017)*.

- **What it is:** the SHAP method: a model's output is split into one contribution per feature, and
  base value + contributions = the output.
- **Where we use it:** steps D1 (SHAP ranking of the forest), D2 (stability of that ranking), F1
  (deletion test on SHAP's top features) and F2 (additivity check).
- **In the report:** Results, "SHAP versus the attacker" and "Do the explanations hold up?";
  Discussion, "Are the explanations stable and faithful?".
- **Status:** well known; details as given.

### [5] Lundberg et al. (2020): TreeSHAP

Lundberg, S. M., Erion, G., Chen, H., DeGrave, A., Prutkin, J. M., Nair, B., Katz, R., Himmelfarb, J.,
Bansal, N., & Lee, S.-I. (2020). From local explanations to global understanding with explainable AI
for trees. *Nature Machine Intelligence*, 2, 56–67.

- **What it is:** TreeSHAP, the exact and fast SHAP algorithm for tree models (`shap.TreeExplainer`).
  It explains the model's own output, which for a scikit-learn forest is a probability and for
  gradient boosting is log-odds.
- **Where we use it:** every SHAP computation (steps D1, D2, F1, F2). It backs our F2 finding that
  for the forest base value + SHAP values equal the probability *without* a sigmoid, while for
  gradient boosting the sigmoid is needed. This corrects the lab text's hint.
- **In the report:** Results, "Do the explanations hold up?" ("… for a scikit-learn forest TreeSHAP
  explains the probability itself, not log-odds …").
- **Status:** well known; details as given.

### [6] Ribeiro, Singh & Guestrin (2016): LIME

Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). "Why should I trust you?": Explaining the predictions
of any classifier. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery
and Data Mining (KDD '16)*, 1135–1144.

- **What it is:** LIME: it explains one prediction by fitting a weighted straight line to the model's
  answers on perturbed copies of the input; the line's R² is the fit score.
- **Where we use it:** step F3 (LIME's fit score on 20 random and 10 borderline flows).
- **In the report:** Results, "Do the explanations hold up?" (R² 0.075–0.300); Discussion ("LIME is
  neither …").
- **Status:** well known; details as given.

### [7] Breiman (2001): random forests

Breiman, L. (2001). Random forests. *Machine Learning*, 45(1), 5–32.

- **What it is:** the random forest: many decision trees on bootstrap samples and random feature
  subsets, which vote.
- **Where we use it:** the main detector (300 trees, setup step A0), the 100-tree forests of step E2,
  and the forest inside the ensemble (step E1).
- **In the report:** Setup, "Models"; Discussion (why one tree breaks earlier than 300 voting trees).
- **Status:** well known; details as given.

### [8] Friedman (2001): gradient boosting

Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. *Annals of
Statistics*, 29(5), 1189–1232.

- **What it is:** gradient boosting: small trees built one after another, each correcting the
  previous ones, adding up in log-odds.
- **Where we use it:** the gradient boosting member of the ensemble (step E1); the log-odds additivity
  check for gradient boosting (step F2).
- **In the report:** Setup, "Models"; Results, "Evasion attack" (ensemble row of Table 3).
- **Status:** well known; details as given.

### [9] Pedregosa et al. (2011): scikit-learn

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M.,
Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M.,
Perrot, M., & Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine
Learning Research*, 12, 2825–2830.

- **What it is:** the library behind all models, the split and the metrics (macro-F1, recall,
  ROC-AUC, PR-AUC).
- **Where we use it:** every step.
- **In the report:** Setup, "Models"; the "Use of AI" paragraph lists the libraries.
- **Status:** well known; details as given.

---

## Supporting specific claims in the report

### [10] Engelen, Rimmer & Joosen (2021): flaws in CICIDS2017

Engelen, G., Rimmer, V., & Joosen, W. (2021). Troubleshooting an intrusion detection dataset: the
CICIDS2017 case study. *2021 IEEE Security and Privacy Workshops (SPW)*, 7–12.

- **What it is:** a study of errors in CICIDS2017: mislabelled attacks and problems in the traffic
  capture and in how the CICFlowMeter tool built the flows (packet misorder, duplication).
- **Where we use it:** step A1 (11 features with impossible negative values, extreme outliers) and the
  explanation of why the trees collapse under noise in step B1 (outliers inflate the standard
  deviation, so "5% of the std" is huge for an ordinary flow).
- **In the report:** Setup, "Data"; Discussion, "How much of the score is real?" ("Outliers inflate
  the standard deviation of the timing features …").
- **Note:** the paper supports the general point that CICIDS2017 contains recording and tool errors.
  The specific bugs we saw (negative header lengths, −1 values) are our own observation in step A1,
  so cite it as "known data-quality problems", not as the source of those exact values.
- **Status:** checked on 2026-10-07: IEEE SPW 2021, pages 7–12.

### [11] Saito & Rehmsmeier (2015): PR-AUC on imbalanced data

Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot
when evaluating binary classifiers on imbalanced datasets. *PLoS ONE*, 10(3), e0118432.

- **What it is:** shows that ROC curves can look excellent on imbalanced data while precision-recall
  curves reveal the real performance.
- **Where we use it:** step A2 (PR-AUC added to `report()`; PR-AUC separated the models almost four
  times more than ROC-AUC).
- **In the report:** Results, "Baseline" (Table 2); Discussion, "How much of the score is real?"
  ("PR-AUC separated the models almost four times more than ROC-AUC …").
- **Status:** well known; details as given.

### [12] Arp et al. (2022): pitfalls of machine learning in security

Arp, D., Quiring, E., Pendlebury, F., Warnecke, A., Pierazzi, F., Wressnegger, C., Cavallaro, L., &
Rieck, K. (2022). Dos and don'ts of machine learning in computer security. *31st USENIX Security
Symposium (USENIX Security 22)*.

- **What it is:** a survey of common mistakes in security ML, including the base-rate fallacy
  (ignoring how rare attacks are), inappropriate performance measures and unrealistic threat models.
- **Where we use it:** step A2 (the always-benign baseline) and the constrained-vs-unconstrained
  comparison of step C2 (why an attack that may change everything overstates the risk).
- **In the report:** Results, "Baseline"; Discussion, "How much of the score is real?" and "How much
  robustness comes from the network?".
- **Status:** well known; details as given.

### [13] Biggio & Roli (2018): adversarial machine learning

Biggio, B., & Roli, F. (2018). Wild patterns: Ten years after the rise of adversarial machine learning.
*Pattern Recognition*, 84, 317–331.

- **What it is:** the standard overview of evasion attacks (changing inputs at test time to fool a
  trained model) and of how to model an attacker's goal, knowledge and capability.
- **Where we use it:** step C2 (the greedy evasion attack) and step E1 (the attacker probes the
  deployed ensemble).
- **In the report:** Problem (definition of an evasion attack); Results, "Evasion attack"; Discussion,
  "How much robustness comes from the network?".
- **Status:** well known; details as given.

### [14] Apruzzese et al.: realistic attacks on network intrusion detectors

Apruzzese, G., Andreolini, M., Ferretti, L., Marchetti, M., & Colajanni, M. Modeling realistic
adversarial attacks against network intrusion detection systems. *Digital Threats: Research and
Practice* (ACM). Preprint: arXiv:2106.09380.

- **What it is:** argues that attacks on network intrusion detectors must respect what an attacker can
  really change in network traffic ("problem-space" constraints), and models attackers by their
  capabilities, visibility and constraints.
- **Where we use it:** step C1 (the Free / Costly / Fixed groups: the attacker controls only their own
  forward traffic) and step C2 (why the unconstrained attack's 50 of 50 overstates the risk).
- **In the report:** Setup, "Feature groups for the attack"; Results, "Evasion attack"; Discussion,
  "How much robustness comes from the network?".
- **Status: confirm the volume, issue and year before citing.** Checked on 2026-10-07: the paper,
  authors and journal are correct, but sources disagree on the publication date (2021 vs 2022). Copy
  the final details from the journal's own page (ACM Digital Library).

### [15] Aas, Jullum & Løland (2021): SHAP with correlated features

Aas, K., Jullum, M., & Løland, A. (2021). Explaining individual predictions when features are
dependent: More accurate approximations to Shapley values. *Artificial Intelligence*, 298, 103502.

- **What it is:** shows that standard SHAP assumes features are independent, and that with correlated
  features the credit is split between them in ways that can mislead.
- **Where we use it:** step F1 (the top feature alone vs. with its correlated "twins") and step E2
  (removing one feature vs. a whole correlated group), the lab's section 3.6 on twins.
- **In the report:** Results, "Do the explanations hold up?" and "Feature removal with retraining";
  Discussion, "Are the explanations stable and faithful?" ("the information sits in a family of
  twins …").
- **Status:** checked on 2026-10-07: *Artificial Intelligence*, 298 (2021), article 103502.

---

## Tools and AI use

### [16] Claude (Anthropic)

Anthropic. Claude, AI assistant. https://www.anthropic.com/claude

- **What it is:** the AI assistant used to help write the code, run the experiments and draft the
  report.
- **Where we use it:** throughout the project, as the lab's honesty rule requires us to state.
- **In the report:** section 5, "Use of AI" (already in the report).
- **Status:** add the model version if the course asks for it.

### Software (optional, if the course wants tools listed)

SHAP 0.52.0, LIME 0.2.0.1, scikit-learn 1.6.1, pandas 3.0.6, NumPy 2.5.3, SciPy 1.18.1,
matplotlib 3.11.2 (versions as pinned in `requirements.txt`).
