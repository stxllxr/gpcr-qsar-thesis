# Curation & QSAR modelling of clinical-stage GPCR ligands

Code and data for the MSc thesis *"Curation and Cheminformatic Characterisation of a
Clinical-Stage GPCR Ligand Dataset for Machine-Learning-Based Binding-Affinity Prediction"*
(University of Verona, 2025-2026).

A reproducible pipeline that (1) curates a dataset of clinical-stage GPCR ligands from ChEMBL,
(2) characterises its chemical space, and (3) builds and honestly validates a binding-affinity
model for the serotonin 5-HT2A receptor.

## Dataset at a glance
- **3,011** compound-target records, **719** unique molecules, **47** targets, **18** receptor families
- Source: **ChEMBL v36** (October 2025), human Ki binding data, clinical Phase I-IV, < 700 Da
- Headline model: **ECFP4 + Random Forest**, 5-HT2A -- mean held-out R2 = **0.355** (95% CI [0.11, 0.60])
  under a repeated Bemis-Murcko scaffold split, passing y-randomisation (p = 0.0099) and beating a
  nearest-neighbour read-across baseline.

## Repository structure
```
curated_15desc.csv        the locked dataset (719 molecules x 15 descriptors + SMILES + pKi)
results_data/             benchmark outputs
  tab_repeated_raw.csv        per-split 5-HT2A benchmark
  baseline_comparison.csv     read-across / PLS / Ridge baselines
  panel_results.csv           seven-target generalisation panel
  panel_yrand2.csv            panel y-randomisation p-values
scripts/
  chembl_target_fetcher.py    curation: query + filter ChEMBL v36
  baseline_run.py             QSAR benchmark + baselines (5-HT2A)
  make_figures.py             regenerate every thesis figure
```

## Reproduce
Run the scripts **from the repository root** (they read `curated_15desc.csv` and
`results_data/` by relative path):
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# (optional) re-curate the dataset from ChEMBL v36
python scripts/chembl_target_fetcher.py

# QSAR benchmark + baselines  -> writes results_data/baseline_comparison.csv
python scripts/baseline_run.py

# regenerate all figures       -> writes figures/*.png
python scripts/make_figures.py
```
All analyses were run on **Python 3.10.19**; exact package versions are pinned in `requirements.txt`.

## Data availability
The curated dataset (`curated_15desc.csv`) is derived from the open
[ChEMBL v36](https://www.ebi.ac.uk/chembl/) database. Raw ChEMBL bulk data are not redistributed here;
`scripts/chembl_target_fetcher.py` reproduces the dataset from the public source.

## Citation
> Fikadu, D. T. (2026). Curation and Cheminformatic Characterisation of a Clinical-Stage GPCR Ligand
> Dataset for Machine-Learning-Based Binding-Affinity Prediction. MSc thesis, University of Verona.

## License
Code released under the [MIT License](LICENSE). Bioactivity data (c) the ChEMBL/EMBL-EBI database under
its own terms.
