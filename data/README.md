# Data

`processed/clean.csv` is the cleaned CICIDS2017 table from Lab 1, copied unchanged from
`Lab1_Building_Your_First_Intrusion_Detector/collab/data/processed/clean.csv`.

- 446,641 flows, 68 numeric features plus `Label` (attack type, `BENIGN` = normal)
- all eight CICIDS2017 day-files, ID columns dropped (including `Destination Port` and `Protocol`),
  infinities/NaN rows dropped, duplicates dropped, constant columns dropped, 20% stratified sample,
  seed 42
- SHA-256 `70befd29488c54f9bfa7b24aa286dfad493b7be35e5691585920bf126d2988d7`

It is not in git (150 MB). Get it from a teammate or the shared folder, or rebuild it:
put the eight CICIDS2017 `MachineLearningCSV` day-files (https://www.unb.ca/cic/datasets/ids-2017.html)
in `raw/`, then run `python lab1_pipeline/clean.py`.

The 60/20/20 split (`lab1_pipeline/prepare.py` logic, stratified on the attack type, seed 42)
reproduces Lab 1's split exactly: train 267,984 / val 89,328 / test 89,329 rows (checked 2026-10-04).
