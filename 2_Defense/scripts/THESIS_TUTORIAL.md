# How my thesis works — a walkthrough

*Curation and Cheminformatic Characterization of a Clinical-Stage GPCR Ligand Dataset for Machine-Learning-Based Binding Prediction*

Written to be read start to finish in about twenty minutes. It explains **what** was done, **why** each choice was made, and **what the numbers mean** — because at a defense the "why" is what gets asked, not the "what".

---

## 0. The whole thesis in one paragraph

GPCRs are the most productive drug-target class we have, but we still can't reliably say *which molecular features* make a compound bind tightly. So: I built a clean dataset of GPCR ligands that had reached clinical trials, measured their chemistry systematically, and then used that dataset to train models that predict binding affinity from structure alone. The models work — R² of 0.56 and 0.64 on chemistry they have never seen — and, more importantly, I ran the controls needed to show that number is real rather than an artefact of how the data was split.

**The one-sentence version:** *not just a model that predicts well, but a model validated carefully enough to be believed.*

---

## 1. Why the problem is hard

Predicting binding affinity looks like ordinary regression: molecule in, number out. Three things make it harder than it looks.

1. **Molecules aren't numbers.** A model is a mathematical function. It cannot read a chemical drawing, so the molecule must first be translated into a fixed-length vector. How you translate determines what the model can possibly learn.
2. **The labels are noisy.** Kᵢ values come from many labs and assays. Inter-laboratory reproducibility for pooled ChEMBL Kᵢ is only about **0.5 log units**. That's a floor: no model can be more accurate than the data it learns from.
3. **It's easy to fool yourself.** Similar molecules have similar fingerprints. Split your data randomly and a molecule's near-twin ends up in training — the model "predicts" something it has effectively already seen, and your score looks great and means nothing. **This is the trap the whole thesis is built to avoid.**

---

## 2. Part One — building and understanding the dataset

### 2.1 Why curate by clinical stage?

Most QSAR datasets are assembled by potency: take everything measured against a target. I did something different — selected compounds that reached **clinical Phases I–IV**. Why:

- That chemistry has already survived safety and developability selection. It's what real drug discovery produces, not what's easy to measure.
- It makes the dataset informative for **repurposing**: these are molecules already in humans.

The cost, which I state openly: selecting on clinical status means the set is small and biased toward things that worked.

### 2.2 The pipeline

Human Kᵢ from ChEMBL → Phases I–IV → below 700 Da → strip salts → remove peptides → drop compounds with >10 rotatable bonds → keep the highest pKᵢ per molecule.

**Result: 3,011 compound–target records · 719 unique molecules · 47 targets · 18 receptor families.**

Two filters worth being able to justify:
- **700 Da** — beyond this you leave small-molecule drug space.
- **≤10 rotatable bonds** (Veber) — 2D descriptors describe topology, not shape. A very flexible molecule has one 2D graph but many real conformations, so 2D features describe it poorly. Excluding them removes noise from *both* halves of the thesis.

### 2.3 What's in it

- **Strongly aminergic**: serotonin 25.3%, adrenergic 21.1%, dopamine 17.2%, muscarinic 15.3%, opiate 7.5% — about **86%** of records.
- **Approved-drug rich**: **52.4%** of unique molecules reached Phase IV.

> **The records-vs-molecules trap.** At record level 69.8% look like Phase IV. But approved drugs are promiscuous, so they get assayed against many targets and are *over-counted*. Per unique molecule it's 52.4%. Always say which you're counting. This is the kind of detail a controrelatore probes.

### 2.4 Polypharmacology

Mean **4.19** targets per molecule (median 2, max 31); **64.7%** hit more than one target; 1.89 receptor families on average.

This isn't a flaw, it's a direct consequence of curating by clinical status. It matters twice: it's the basis of the repurposing argument, and it's why I later remove promiscuous compounds and retrain, to prove the models aren't just memorising a handful of famous polypharmacological drugs.

### 2.5 The descriptor panel — the bridge to Part Two

Fifteen descriptors per molecule, computed with RDKit:

| Group | Descriptors |
|---|---|
| Physicochemical & structural (11) | MW, LogP, LogS, TPSA, HBA, HBD, RotB, HAC, RingCount, Fsp³, HalogenCount |
| Efficiency metrics (4) | QED, LE, LLE, LELP |

The four efficiency metrics are *derived* — they combine the descriptors with the measured affinity, so potency is judged relative to size and lipophilicity rather than on its own:

- **LE** = 1.37 × pKᵢ / heavy atoms — binding energy per atom
- **LLE** = pKᵢ − LogP — potency that isn't just greasiness
- **LELP** = LogP / LE — lipophilicity per unit efficiency (lower is better)
- **QED** — a 0–1 drug-likeness desirability score

**Remember the number 15.** In Part Two the same idea scales to ~200 descriptors plus a 2,048-bit fingerprint. That's the hinge between the halves of the thesis.

### 2.6 What the chemistry says

- Drug-like and size-efficient: **mean QED 0.64**, **mean LE 0.40**, 95th-percentile "soft limit" **0.65**, max 1.11. These are *dataset-derived benchmarks* for GPCR optimisation — a contribution in their own right.
- Efficiency falls steeply with size (**Spearman ρ = −0.77**): small compounds reach the highest efficiencies; larger ones get pulled to the mean. Expected — binding contributions aren't perfectly additive.
- **Halogenation (39.1%)**: heavier, more lipophilic, markedly less soluble (LogS −5.17 vs −4.07), lower saturation — but **affinity essentially unchanged**, and **no association with clinical phase** (χ² = 3.34, p = 0.342). A real property signature, not a marker of success.

---

## 3. Part Two — the modelling

### 3.1 The honest bit up front

Two data-rich targets: **serotonin 5-HT₂A** and **dopamine D₃**. But the clinical set only gives **172 and 173** compounds for them — far too few to train on *and* validate honestly.

So each was extended ~**27-fold** with preclinical ChEMBL compounds under the same curation: **4,620** and **5,488** molecules.

**Say this before you're asked.** The title says clinical-stage; the models train on an extended set. It's defensible — the scaffold split still guarantees unseen test chemistry — but only if you volunteer it.

### 3.2 Turning molecules into numbers

**ECFP4 fingerprint (2,048 bits).** For each atom, look at its neighbourhood out to two bonds, hash that substructure into one of 2,048 slots. Each bit answers "is this fragment present?". Always 2,048 bits regardless of molecule size; similar structures give similar barcodes.

**Descriptors (~200).** Whole-molecule properties, normalised (DescriptaStorus RDKit2D).

**Fused = 2,248 features.** Concatenated. This is the only thing the model ever sees.

Fingerprints say *what the molecule contains*; descriptors say *what the molecule is like overall*. Different information — hence the fusion.

### 3.3 The models

Three tree ensembles: **Random Forest** (many trees on random subsets, averaged, so errors cancel), **XGBoost** and **CatBoost** (boosting — trees added in sequence, each fixing the last one's mistakes).

Why not deep learning: at a few thousand compounds, tree ensembles are competitive, cheaper and interpretable. Deep models need far more data to pay off. CatBoost exists here purely to show the result isn't an artefact of one library.

Hyperparameters were **fixed sensible defaults**, not tuned per fold — an honest limitation. Nested CV would be the rigorous protocol.

### 3.4 The scaffold split — the core of the thesis

Group molecules by their **Bemis–Murcko scaffold** (the core ring system), then assign *whole scaffold families* to either training or test. No scaffold appears on both sides, so every test compound is structurally novel.

Repeated over **12 randomised 80/20 partitions**; report the mean R² with a 95% CI.

This is the difference between simulating a real prospective task and grading your own homework.

---

## 4. The results, and what they mean

| | 5-HT₂A | D₃ |
|---|---|---|
| Scaffold-split R² | **0.562** | **0.644** |
| 10-fold CV R² | 0.679 | 0.717 |
| RMSE (log units) | 0.70 | 0.69 |

**Reading the gap.** Cross-validation gives 0.68 and 0.72; the scaffold split gives 0.56 and 0.64. That gap *is* the leakage effect, made visible on purpose. The honest number is the lower one.

**Is 0.56 good?** Yes, in context:
- RMSE ≈ 0.70 against a **~0.5-log noise floor** — the models operate within about 1.5× irreducible experimental error.
- Large-scale benchmarking of single-assay models on realistically novel compounds reports a **median R² near 0.12**; R² ≈ 0.55 is normally reached only by multitask models pooling thousands of assays.

**Why is D₃ higher?** RMSE is almost identical. D₃ just has a wider affinity spread, and R² = 1 − RMSE²/Var — same error, wider variance, higher R².

**The distribution result.** Predicted pKᵢ has SD 0.92 vs 1.23 observed (5-HT₂A) and 0.98 vs 1.28 (D₃): about **74% and 76% of the spread retained**. The models get the centre right and compress both tails. That's regression to the mean under a leakage-controlled split — expected, not a bug. Consequence: they **rank** compounds reliably but under-call the extremes, so absolute predictions are conservative at the potent end.

---

## 5. Why the result is believable — the three probes

This is the part that makes it a thesis rather than a demo.

**1. Representation.** Fused beats the alternatives on 5-HT₂A (0.562 vs 0.544 fingerprint, 0.521 descriptors) and ties on D₃ (0.644 vs 0.639). Measured, not assumed. Note descriptors alone are weakest on both — substructure carries more signal than bulk properties.

**2. Y-randomisation.** Shuffle the training labels 100 times and refit. If the model were fitting noise, shuffling wouldn't hurt it. Instead R² collapses to a null centred below zero (mean −0.08 and −0.07, best 0.02), far from the true values. **p = 0.0099.** So the signal is real.

**3. Read-across baseline.** Assign each test compound the pKᵢ of its most Tanimoto-similar training compound — no learning at all. That reaches **0.347 and 0.435**; the models reach 0.562 and 0.644. Beating a nearest-neighbour lookup by ~0.2 R² is what shows the model learns aggregate structure–activity, not a disguised similarity search.

Plus two more:
- **Learning curve** — R² climbs from ~0.3 to ~0.6 and flattens, so the gain is data-driven and we're near the single-target ceiling. More of the same data won't help much.
- **Promiscuity ablation** — remove every compound hitting ≥5 targets (136 and 117) and retrain: 0.562 → 0.575, 0.644 → 0.672. Performance holds. *Regression models only* — the classifiers were not retrained under this.

---

## 6. The screening view

Recast as a classifier at a **100 nM** cut-off (pKᵢ ≥ 7), which splits the data near-evenly (59% and 67% active).

- **MCC 0.61–0.64** — balance-robust, well above the 0.4 "solid classifier" mark
- **Top-1% enrichment 1.67 and 1.46** — essentially at the ceiling, which is 1/(active fraction) ≈ 1.69 and 1.49
- ROC-AUC is ~0.90 but **not the headline**: on a diverse, majority-active library AUC stays high and flatters the result. It's reported in the thesis table for completeness.

**The caveat you must state:** every compound in the set is a *measured binder*. So this separates **potent binders from weaker binders**, not binders from non-binders. A true binder-vs-decoy screen would need inactive data the set doesn't contain.

---

## 7. What the models actually use

**SHAP (descriptor level).** The two targets rely on different chemistry: 5-HT₂A on **charge and electrostatics** (PEOE_VSA terms, partial-charge extremes, LogP), D₃ on **shape and topology** (Balaban J, Kappa1, Chi indices). Chemically sensible — it mirrors the different binding pockets.

**Fingerprint importance (substructure level).** The top ECFP4 bits are recognisable aminergic pharmacophores — benzisothiazole/benzisoxazole–piperazine, arylpiperazine motifs.

Both analyses agree, at two different resolutions. The models aren't black boxes.

---

## 8. Limitations — own them

1. **Pooled Kᵢ labels** across assays and labs; ~0.5-log reproducibility floors achievable error.
2. **Two targets only**, chosen for data density. The pipeline is general; the numbers aren't yet shown to transfer.
3. **2D representation** — no conformation, no protein structure, so binding-mode effects are invisible.
4. **No external test set** — validation is internal, leakage-controlled and repeated, but not prospective.
5. **Binder-only library** — potency ranking, not binder/non-binder discrimination.
6. **Default hyperparameters**, and the promiscuity ablation covers regression only.

Each of these is a concrete next step, which is exactly how to present them.

---

## 9. If you remember only five things

1. **The scaffold split is the point.** Everything else supports it. 0.56 honest vs 0.68 optimistic — the gap is shown on purpose.
2. **0.56–0.64, and why that's good**: ~1.5× the noise floor, against a literature median near 0.12 for this kind of task.
3. **Three probes**: y-randomisation (p = 0.0099), read-across (+0.2 R²), representation comparison.
4. **Potent vs weaker binders**, not binders vs non-binders. Say it before you're asked.
5. **15 descriptors → ~200 + fingerprint** — the thread linking Part One to Part Two.

---

## 10. Glossary

| Term | Plain meaning |
|---|---|
| **Kᵢ / pKᵢ** | Binding constant; pKᵢ = 9 − log₁₀(Kᵢ in nM). Higher = tighter. |
| **ECFP4** | Fingerprint: a 2,048-bit on/off barcode of which substructures are present. |
| **Descriptor** | A single computed property of the whole molecule (weight, LogP…). |
| **Bemis–Murcko scaffold** | The core ring framework left when side chains are stripped. |
| **Scaffold split** | Train/test split by scaffold family, so test chemistry is unseen. |
| **Data leakage** | Test information reaching the model, inflating the score. |
| **R²** | Fraction of variance explained. 1 = perfect, 0 = no better than the mean. |
| **RMSE** | Typical error size, in pKᵢ log units. |
| **y-randomisation** | Shuffle labels; a real model must fail on nonsense. |
| **Read-across** | Predict by copying the most similar known compound. |
| **MCC** | Correlation-like classification score, robust to class imbalance. |
| **Enrichment factor** | How many more actives the top of a ranked list holds vs random. |
| **SHAP** | Attributes each prediction back to the input features. |
| **LE / LLE / LELP** | Potency per atom / minus lipophilicity / lipophilicity per efficiency. |
| **QED** | 0–1 drug-likeness desirability score. |
