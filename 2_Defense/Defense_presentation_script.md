# Defense presentation script — ~18–20 min

**How to use:** don't read it word-for-word — internalize the flow and land the **bold numbers**. Speak to the room, not the slides. Pause at each PART divider. If you blank, the bold figure per slide is enough to recover.

*(All numbers below are the final, full-data results.)*

---

**S1 · Title (~30s)**
"Good [morning/afternoon]. I'm Dagmawi Tarekegn Fikadu. I'll present my MSc thesis — the curation and cheminformatic characterisation of a clinical-stage GPCR ligand dataset, and its use for machine-learning prediction of binding affinity — supervised by Prof. Alejandro Giorgetti and Filippo Baldessari."

**S2 · Overview (~30s)**
"The talk has two parts. First I build and characterise a curated dataset of clinical-stage GPCR ligands — its chemical space, efficiency benchmarks, and halogenation. Then I use it to train and rigorously validate machine-learning models of binding affinity for two targets."

**S3 · GPCRs (~55s)**
"GPCRs are seven-transmembrane receptors that convert outside signals into cellular responses. They're the most productive drug-target class — about a third of approved drugs act through them — because their pockets fit small, drug-like molecules. The aminergic subfamily — serotonin, dopamine, adrenergic, muscarinic — is especially drug-rich, and its ligands are famously cross-reactive: a liability, but also an opening for repurposing."

**S4 · Motivation (~55s)**
"I focused on **clinical-stage** compounds because they've already cleared safety hurdles — their chemistry is what survives selection. And ChEMBL gives standardised affinity data across the whole GPCR literature. So a curated set of clinical-stage GPCR ligands is a natural starting point both for characterising successful chemistry and for modelling."

**S5 · Aims (~40s)**
"Four objectives: curate a clean, reproducible clinical-stage Kᵢ dataset; compute physicochemical and efficiency descriptors; characterise the chemical space — composition, halogenation, diversity; and develop rigorously-validated ML models of binding affinity."

**S6 · PART ONE (~10s)** — "Part one: the dataset and its chemistry."

**S7 · Curation pipeline (~55s)**
"The pipeline pulls human Kᵢ data from ChEMBL v36, then applies clinical-phase filtering, a molecular-weight cut, salt removal, peptide exclusion, and deduplication to the best value per molecule. The result: **3,011 records, 719 unique molecules, 47 targets, 18 families** — fully reproducible from the code."

**S8 · Aminergic map (~40s)**
"The dataset is strongly aminergic — five families hold about **86%** of records, serotonin alone a quarter. That's where clinical GPCR chemistry has concentrated."

**S9 · Counting-unit effect (~55s)**
"An important subtlety: whether the library looks 'approved-rich' depends on counting records or molecules. Late-stage drugs are promiscuous, so they're over-represented per record. Counted per unique molecule, **52%** are approved. I report per-molecule throughout to avoid that inflation."

**S10 · CNS-like profile (~40s)**
"The physicochemical profile — moderate weight, few H-bond donors, modest polar surface area — is exactly what you'd expect for orally-available, brain-penetrant molecules, matching the neuropsychiatric character of the panel."

**S11 · Efficiency benchmarks (~40s)**
"From the data I derived GPCR-specific ligand-efficiency benchmarks: a typical **LE ≈ 0.40**, a soft limit near **0.65**, with efficiency declining steeply as molecules grow — realistic targets for lead optimisation."

**S12 · Dimensionality + diversity (~45s)**
"Two points: the descriptor space is low-dimensional — two components capture **65%** of variance — but the chemistry is diverse: **511 scaffolds** across 719 molecules, most appearing once. That diversity is what makes the modelling test honest later."

**S13 · Halogenation properties (~40s)**
"About **39%** of records are halogenated. Those compounds sit in a distinct property region — heavier, more lipophilic, less soluble — but with essentially unchanged binding affinity."

**S14 · σ-hole (~50s)**
"I split fluorine from the heavier halogens because they differ electronically: chlorine, bromine, iodine carry a **σ-hole** — a positive patch enabling halogen bonding — while fluorine doesn't. Fluorine also keeps more sp³ character, reflecting its use at aliphatic positions."

**S15 · No clinical link (~30s)**
"Despite those property shifts, halogenation shows **no** association with clinical phase — χ², p = 0.34 — so it's a property-tuning tool, not a progression signal."

**S16 · PART TWO (~10s)** — "Part two: machine-learning prediction of binding affinity."

**S17 · Task + models (~45s)**
"The task: predict pKᵢ from structure, for two data-rich aminergic targets — serotonin **5-HT₂A** and dopamine **D₃**. I use two tree ensembles — Random Forest and XGBoost — robust, interpretable, and right for this data scale, where deep learning needs far more."

**S18 · Validation (~55s)**
"Validation is deliberately strict. Instead of a random split — which leaks near-identical analogues across train and test — I use a **Bemis–Murcko scaffold split**, holding out whole scaffolds so the model must predict novel chemistry. I report 10-fold CV alongside to show the leakage gap, plus two controls: y-randomisation and a nearest-neighbour read-across."

**S19 · More data (~55s)**
"Performance here is limited chiefly by training-set size, so I extended each target with preclinical compounds. That took 5-HT₂A from 172 clinical molecules to **4,620**, and D₃ from 173 to **5,488** — a large expansion, with the scaffold split still guaranteeing unseen test chemistry."

**S20 · Results (~55s)**
"The best model — fused fingerprints plus descriptors with XGBoost — reaches a scaffold-split **R² of 0.56 for 5-HT₂A and 0.64 for D₃**, RMSE around **0.7** log units, roughly 1.5× the experimental noise floor. Random Forest is close behind — so performance is set by the data and representation, not the learner."

**S21 · The gain is real (~55s)**
"Three checks. The **learning curve** climbs from about 0.3 to 0.6 as data grows, then flattens — genuinely data-driven, approaching the single-target ceiling. **Y-randomisation**: permuted models never approach the true R², p = 0.0099. And the models beat a **read-across** baseline by about 0.2 — so they learn real structure–activity relationships, not a disguised similarity lookup."

**S22 · Contributions (~50s)**
"Four contributions: a curated, reproducible clinical-stage GPCR dataset; dataset-derived efficiency benchmarks; a characterisation of halogenation including the σ-hole; and a defensible, leakage-controlled ML template reaching **R² 0.56–0.64** with full chance and baseline controls."

**S23 · Future + thanks (~40s)**
"Going forward: extend across every subtype per family; integrate 3D structure and docking; and move to multitask or pretrained models to push beyond the single-target ceiling. Thank you to Prof. Giorgetti, to my supervisor Filippo Baldessari, to the professors of the programme, and to my family. I'm happy to take questions."

---

### Delivery notes
- **Total ≈ 18–19 min** — leaves buffer in a 20-min slot.
- Three ideas the committee will remember, so hit them clearly: **per-molecule counting**, the **σ-hole**, and the **leakage-safe scaffold split with controls**.
- If asked *how you verified the dataset / why the numbers are what they are* — that's the data-correction story; it's in `Filippo_meeting_brief.md`. You don't need to volunteer it in the talk.
- Breathe at the two PART dividers. Land the bold numbers slowly; glide over the rest.
