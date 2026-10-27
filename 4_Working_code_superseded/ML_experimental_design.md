# ML experimental design — GPCR binding-affinity prediction (revised)

Blueprint for the revised machine-learning chapter. Drives both `06_expanded_models.ipynb` and the
ML methods/results sections. Incorporates the meeting decisions (preclinical + Phase I–IV, two targets,
ECFP4 + DescriptaStorus fusion, XGBoost, scaffold **and** LOO, Landrum curation).

---

## 1. Objective & research questions
**Aim:** determine how well classical ML predicts Kᵢ binding affinity from 2D structure for
clinically-relevant aminergic GPCR targets, under honest validation.

- **Q1 — Data & features:** does the expanded (preclinical-included, Landrum-curated) set with a
  **fused ECFP4 + DescriptaStorus** representation and **XGBoost** improve on the original single-target
  ECFP4–RF (R² = 0.355)?
- **Q2 — Validation regime:** how does performance differ between the honest **scaffold split**
  (novel-chemotype) and the standard **leave-one-out** (LOO)?
- **Q3 — Transferability:** does the protocol behave consistently across **two** targets
  (5-HT₂A and D₃)?

## 2. Targets — two parallel case studies
- **Serotonin 5-HT₂A** and **Dopamine D₃** — both aminergic, data-rich, and similar in size
  (~172 / ~173 clinical-stage molecules before preclinical is added), so they are directly comparable.
- **One model per target** (independent single-task models, not multi-task).

## 3. Dataset construction (ML only — descriptive set untouched)
- **Source:** ChEMBL, human, `standard_type = Ki`, binding assays (`assay_type = B`), valid pChEMBL.
- **Phases:** **all** — preclinical + Phase I–IV (the "more data" decision).
- **Curation (uniform):** salt-strip → parent · MW < 700 · peptide/biologic removal ·
  **Landrum 2024 artefact filter** (drop exact-duplicate copies and Δ = 3.0-log unit errors) ·
  **highest-pKᵢ** aggregation per molecule.
- **Report per target:** total n, **preclinical vs Phase I–IV split**, distinct Bemis–Murcko scaffolds,
  pKᵢ range/SD (this last one matters for interpreting R² — see §8).

## 4. Molecular representations — three, compared head-to-head
1. **ECFP4** — 2048-bit Morgan fingerprint, radius 2 (stereo-blind).
2. **DescriptaStorus** — RDKit2DNormalized (~200 physicochemical/topological descriptors).
3. **Fused** — ECFP4 ⊕ DescriptaStorus (concatenated).

Reporting all three shows *whether the fusion earns its place* (on current data: 0.27 / 0.20 → **0.34**).

## 5. Models
- **XGBoost** — primary (the new model Filippo asked for).
- **Random Forest** — retained for continuity with the original thesis result.
- **Baselines (context / rigor):**
  - **1-NN Tanimoto read-across** — trivial similarity baseline (must be beaten).
  - **Cross-validated Ridge** — a properly-regularised linear reference.

## 6. Validation — both, reported side by side
- **Repeated Bemis–Murcko scaffold split** — 25 random seeds, 80/20, whole scaffolds kept train-or-test.
  → mean R² + 95% CI. **The honest, prospective (novel-chemotype) number.** Report **train and test n.**
- **Leave-one-out (LOO)** — one model per compound; pooled predictions. **The standard small-data number
  Filippo asked for; usually higher** because it is not leakage-controlled.
- Both reported together, with one sentence explaining *why LOO ≥ scaffold* (analogues leak into the LOO
  training set) so the two numbers never look contradictory.

## 7. Controls & rigor (keep the thesis's honest-validation ethos)
- **y-randomisation** (100 label permutations) — chance-correlation control (p-value).
- **Applicability domain** — median nearest-neighbour Tanimoto (test → train), to show the model is
  predicting genuinely novel chemistry.
- **Learning curve** *(recommended)* — R² vs training-set size; if it is still rising at full n, it
  demonstrates directly that **adding the preclinical data helps**, which is the whole rationale.

## 8. Metrics — all reported, each defined in a short "metrics" subsection
Filippo flagged that only 2 were explained and that "good RMSE + bad R²" was confusing. So:
- **R²** — fraction of pKᵢ variance explained. *Depends on the spread of the labels.*
- **RMSE, MAE** — average prediction error, in log units (interpretable, dataset-independent).
- **Spearman ρ** — rank correlation (does the model order compounds correctly).
- **Explicit note:** a **narrow pKᵢ range** gives a **low R² even when RMSE is good**, because R²
  measures variance explained relative to the label spread — this resolves his "weird" comment and turns
  it into a teaching point.

## 9. Hyperparameters  *(decision point — see below)*
- **Recommended:** fixed, reported sensible defaults (XGB: ~400 trees, depth 4, lr 0.05, subsample 0.8;
  RF: 400 trees) — simple and fully reproducible. Optional light nested-CV tuning for XGB if Filippo
  wants it, at the cost of compute and a more complex protocol.

## 10. Experimental matrix
**2 targets × 3 representations × 2 models × 2 validation schemes**, plus the 2 baselines and the
y-randomisation / applicability-domain / learning-curve controls. Primary deliverable:

| target | representation | model | scaffold R² [CI] | LOO R² | RMSE | MAE | ρ |
|--------|---------------|-------|------------------|--------|------|-----|---|
| 5-HT₂A | fused | XGB | … | … | … | … | … |
| … | … | … | | | | | |

Plus, per target: predicted-vs-observed scatter, feature-importance, y-randomisation histogram,
learning curve.

## 11. Open decisions (need your / Filippo's call)
1. **Hyperparameters:** fixed defaults (recommended) or nested-CV tuning?
2. **The 7-target generalisation panel** (original thesis Fig.) — Filippo wrote "we will remove this
   part" (p51). Is *that* the panel? If so we drop it; if not, tell me what p51 was.
3. **Learning curve:** include it? (I recommend yes — it directly justifies adding preclinical data.)
4. **Baselines:** keep read-across + CV-Ridge for context, or report only XGB/RF?
5. **Representations:** report all three (ECFP4 / DescriptaStorus / fused), or fused only?
   (I recommend all three — it shows the fusion is justified.)

## 12. What each part feeds
- **Notebook 6** implements §3–§7 and emits the §10 table + figures.
- **ML methods section** describes §1–§9 (with the §3 justification paragraph already drafted).
- **ML results section** presents the §10 table and figures, with the §8 metric explanations.
