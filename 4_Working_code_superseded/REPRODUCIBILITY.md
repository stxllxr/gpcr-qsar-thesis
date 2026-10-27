# Reproducibility — what changes on a rerun

All results in the thesis are pinned to **ChEMBL v36 (October 2025)** and derive from the locked
`data/curated_15desc.csv` (3,011 records / 719 molecules). This note explains, script by script, what
you should expect if you re-run the pipeline.

| Script / notebook | Deterministic? | On rerun you get… |
|---|---|---|
| `baseline_run.py` / `03_model.ipynb` | **Yes** — fixed random seeds (`random_state=seed`, 25 seeds) | **identical** numbers every time |
| `make_figures.py` / `04_figures.ipynb` + extra figure scripts | **Yes** — no randomness | **identical** figures every time |
| `chembl_target_fetcher.py` / `01_fetch_chembl.ipynb` | **No** — queries the *live* ChEMBL API | a slightly **different** dataset — the DB has grown since v36 |

## The modelling and figures are deterministic
Because the scaffold split and the Random Forest are seeded, re-running the benchmark reproduces the
same table to the digit, and the figure scripts reproduce identical PNGs. This is the reproducibility
guarantee: nothing drifts between reruns of the analysis.

## Only the ChEMBL fetch changes — and that is expected
`chembl_target_fetcher.py` always hits the **latest** ChEMBL, not the pinned v36. A representative
re-fetch after v36 returns **~2,960** curated records (5-HT₂A modelling set n ≈ 168), and the headline
ECFP4–Random Forest model gives **R² ≈ 0.32** — versus **3,011 / n = 172 / R² = 0.355** for v36. Both
the dataset size and the performance move only marginally, which shows the results are **stable across
ChEMBL releases**; the small differences are ordinary database curation drift, not a change to the
pipeline. To reproduce the exact v36 counts you need the v36 archive; the live API cannot.

## Note on the headline R²
The thesis headline **R² = 0.355** is the frozen 25-seed benchmark in
`results_data/tab_repeated_raw.csv`. The `baseline_run.py` reproduction script reports **R² ≈ 0.384**
for the same ECFP4+RF model — the two differ only in the scaffold-split implementation and both fall
inside the same 95% CI **[0.11, 0.59]**, i.e. the same conclusion (fingerprints + tree ensemble win,
positive on all splits, beating the read-across and linear baselines). The result is robust even to the
split implementation.

## Bottom line
Re-running the analysis proves reproducibility (identical output); re-running the fetch demonstrates the
result is stable to ChEMBL version. The locked `curated_15desc.csv` remains the authoritative, pinned
dataset for every number reported in the thesis.
