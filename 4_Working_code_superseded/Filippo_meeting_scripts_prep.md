# Scripts prep — Filippo meeting (Saturday, 16:00 Italian time)

Filippo asked you to "be prepared with the scripts." He'll want the *code* behind the correction and the new numbers. Have these four files open, **in this order** — it follows the story. You already have all of them in this folder.

---

## Have open, in order

### 1. `06_expanded_models_eqKi.ipynb` — the original pipeline (where it went wrong)
- This is how the modelling set was first built.
- **Point to Cell 4** (`fetch_activities`): the paginated ChEMBL fetch. The client silently stopped after roughly one page, so only ~1,000 of ~6,200 records came back — the *reported* total looked right, so the truncation was invisible.
- Say: *"This is the fetch that quietly truncated; everything downstream was built on ~20% of the data."*

### 2. `07_verify_fetch.ipynb` — how you caught and PROVED it (your strongest script)
- **Point to the completeness check**: it paginates explicitly and asserts `downloaded == total` (prints COMPLETE / INCOMPLETE), and counts distinct compounds **two independent ways** — both land on **4,633 (5-HT₂A) / 5,571 (D₃)**.
- Say: *"This self-verifies against the API's own total and cross-checks two ways, so the complete count isn't a guess."*
- **Tip: be ready to run this live** if he asks — it's the single most convincing thing you have.

### 3. `08_full_model.ipynb` — the full-data re-model (produced the new numbers)
- **Cell 4 — curation:** salt-strip → MW < 700 → peptide removal → Landrum dedup (highest pKᵢ, drop exact-duplicate and Δ = 3-log artefacts) → **4,620 / 5,488** molecules.
- **Cell 5 — featurisation:** ECFP4 (Morgan radius 2, 2048-bit) + DescriptaStorus (~200 normalised descriptors) = fused, 2,248-dim.
- **Cell A — models:** XGBoost & RF under the Bemis–Murcko scaffold split (12 seeds) + 10-fold CV → scaffold R² **0.56 / 0.64**, RMSE ≈ 0.70 / 0.69.
- **Cell B — controls:** representation comparison, y-randomisation (100 permutations → p = 0.0099), learning curve, read-across baseline.

### 4. `audit_expanded_counts.py` — the per-step funnel (backup)
- Prints records → unique molecules at every filtering step, both targets. Good if he asks "where exactly did the numbers change."

---

## Likely code questions → where to point

- **"Show me where it truncated."** → 06, Cell 4 pagination; 07 shows `downloaded < total` when it stops early.
- **"How do you know it's complete now?"** → 07: the `downloaded == total` assertion + the two counting methods agreeing.
- **"What's the curation, exactly?"** → 08, Cell 4 (salt / MW<700 / peptide SMARTS / Landrum dedup).
- **"How is the scaffold split done?"** → 08, `scaffold_split()`: groups compounds by Bemis–Murcko scaffold, holds out *whole* scaffolds, repeated over 12 random seeds.
- **"Why does the model improve with more data?"** → the learning curve (§3.5.5): R² was still climbing at ~1,100 compounds; at ~4,600–5,500 it flattens near ~0.6.
- **"Why is D₃ higher than 5-HT₂A?"** → identical RMSE (0.70 vs 0.69); D₃'s ~10% wider affinity spread inflates R² at the same error (§4.6).
- **"Which ChEMBL version?"** → complete per-target extraction; record counts match v36, so it's essentially the same data, just fully downloaded.

---

## The one framing to hold
It's **diligence catching a bug** — the result got *better* and landed on the ~0.6 you'd expected. Lead with the **verification script (07)**: it turns "trust me" into "here's the proof." Everything else follows from that.
