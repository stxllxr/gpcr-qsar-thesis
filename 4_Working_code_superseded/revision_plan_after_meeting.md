# Revision plan — Filippo's meeting comments + notes

Two buckets: **(A) model/data changes** (the "regenerate the models" work Filippo told the Prof about —
next week's priority) and **(B) thesis text/figure/formatting edits** (his 42 PDF margin notes).

---

## A. MODEL & DATA CHANGES  (the big one — do first)

### A1. Add preclinical + Phase I compounds to the ML set (more data → better R²)
- **ML modelling:** include **preclinical + Phase I** compounds (bigger training set → the current
  R² ≈ 0.355 is what he flagged as "a very bad R²"; more data is the fix).
- **Descriptive / data-analysis part:** keep to compounds that **passed Phase I** (safe compounds).
  → Filippo p20 "talk about Phase I", p21 "included Phase I molecules for the data-analysis part but
  only compounds that passed Phase I were included since we want safe compounds."
- *(Confirm: your note "P1 can be ruled out for d…" — ruled out for the **data-analysis** part? i.e.
  data analysis = passed-Phase-I only; ML = pre + P1.)*

### A2. Build TWO separate models — Serotonin and Dopamine (one each)
- Your note: *"…preclinical data for serotonin only … and dopamine for both, one model for each …"*
- So: a **5-HT2A model** and a **Dopamine model** (confirm which subtype — D2? D3? "both"?), each
  trained separately.

### A3. Combine both representations + XGBoost
- Your note: *"Using both fingerprints and DescriptaStorus with XGB…"*
- → Feature set = **ECFP4 fingerprints + DescriptaStorus descriptors together**, model = **XGBoost**
  (and/or RF). Currently they were compared separately; now fuse them.

### A4. Apply the Landrum et al. 2024 curation
- Filippo p21: *"apply a different type of curation: from Landrum et al. 2024
  (doi:10.1021/acs.jcim.4c00049)."*
- Your note: *"apply curation of paper, recalculate … then add preclinical data … then re-curate
  again using the paper."* → Order: curate (paper) → add pre/P1 data → re-curate (paper).
- Cheap wins from the paper: drop exact-duplicate values and Δ=3.0-log unit-error artefacts;
  prefer metadata-matched assays. (Notebook 5 already computes the noise; extend it to curation.)

### A5. Validation tweak — leave-one-out
- Your note: *"Try leave one out."* → add **LOO-CV** (sensible for the small-n regime), alongside the
  scaffold split.

### A6. Extra halogen filter
- Your note: *"iodide, bromic acid can be also applied to be filtered."* → confirm exactly what he
  wants filtered (iodine/bromine-containing? a specific salt like bromic acid?).

---

## B. THESIS EDITS  (Filippo's 42 PDF notes, by theme)

### B1. Front matter
- **p1 (title page):** roles are — **Principal Investigator: Alejandro Giorgetti · Supervisor: Filippo
  Baldessari.** Fix these.
- **p2:** spacing — too much space at top, too little at bottom (fix vertical centering).
- **p5 (acknowledgements):** may add family/friends and master-course professors (some may be opponents).

### B2. Introduction
- **p17:** replace **thalidomide** as an example — it's toxic/teratogenic, wrong fit for a "safe
  compounds" thesis; use another, less clichéd example.
- **p17:** add a **brief, non-technical explanation of the ML models** you use, with **pros & cons**.

### B3. ML section (writeup)
- **p45:** wording — you are **"developing a machine-learning model,"** not "modelling."
- **p45:** add a **section that explains each metric** (R², RMSE, MAE, Spearman…) — you only did 2, briefly.
- **p45–47:** he flags the **R² as "very bad"** and the **"good RMSE + bad R²" as weird and unexplained**
  → (a) the new data (A1) should lift R²; (b) **explain** the RMSE-vs-R² point in text (low pKi variance
  → low R² even with a decent RMSE).
- **p50:** report the **test-set n** as well.
- **p51:** **remove this part.**  **p56:** **rework this.**

### B4. Halogenation — science + softening
- **p23 / p39:** the F-vs-heavy-halogen difference is the **σ-hole (electron density), not sterics** —
  explain and **reference** it. Fluorine → multipolar interactions on amide π (protein backbones);
  chlorine/heavy → halogen···π / halogen bonds; **chlorine also aids metabolic stabilisation.**
  (Matches your notes: *"Fl vs Cl is the kind of interaction… not steric"*, *"it's fluoride not fluorine"* —
  confirm the fluoride/fluorine wording he wants.)
- **p40:** **soften the overclaim** — "this **could** indicate that halogenation…," not "indicating."
- **p44:** *"very nice this section — insert into the presentation"* (a win); but clarify **"these
  percentages are regarding what?"**

### B5. Figures & tables (recurring)
- **Font sizes too small** on many figures — p29, p31, p32, p34, p38, p39 (make axis text bigger/bold).
- **Figures in the wrong section** — p31 (should be under MW), p36, p41 → move to correct sections;
  p31 also: add a sentence **introducing** the figure before it.
- **p29:** *"these numbers look wrong"* → **verify the numbers** on that figure.
- **p33:** replace with a **proper stats table** (mean, SD, median, min, max); explain **why p95 for only
  one metric**, and **where the high/low ranges came from.**
- **p34:** split into 2 figures; state the **heavy-atom↔weight** correlation and the
  **solubility↔lipophilicity trade-off** are **expected.**
- **p38:** better representation + bigger font.

### B6. Conclusions / misc
- **p61:** rephrase in line with the other comments.
- **p70:** redundant — already in the text; your note *"this is dumpable — don't need the other
  receptor-family number."*
- **More references** throughout (your note), esp. σ-hole and the ML-model discussion.

### B7. Limitations
- Your note: strengthen **Deep Learning** limitation — low-data regime, DL needs large data, so it's
  inappropriate here (you already have a version; align it with the "more data would help" framing).

---

## Items to confirm with Filippo / yourself before building
1. **Dopamine subtype(s)** for the second model — D2, D3, or "both"?
2. **P1 exclusion** — is data-analysis "passed-Phase-I only" and ML "pre + P1"? (decode of "P1 ruled out for d…")
3. **The halogen filter** — what exactly (iodine/bromine compounds? bromic-acid salt?).
4. **Fluoride vs fluorine** wording preference.

## Suggested order of work
1. Confirm the 4 items above.
2. Rebuild the dataset: Landrum curation → add pre/P1 → re-curate (A4, A1).
3. Retrain: 5-HT2A + Dopamine, ECFP4+DescriptaStorus + XGB, scaffold split **and** LOO (A2, A3, A5).
4. Update the ML section text (B3) with the new numbers + metric explanations.
5. Work through the figure/formatting/science comments (B4, B5) + front matter (B1).
6. Recompile → send back to Filippo & the Prof.
7. Then: build the presentation (p44 section is a highlight to feature).
