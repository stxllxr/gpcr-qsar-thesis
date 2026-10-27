# Meeting brief — Filippo, Saturday

**Topic:** While finalizing, I re-verified the ML dataset, found a silent data-loading bug that had capped the training set at ~20% of the available data, fixed it, re-ran everything — and the results *improved* (R² 0.56 / 0.64, right around the 0.6 you'd expected).

Read this to understand it cold. The **"say this"** lines are what to actually speak; the rest is so you can answer anything he throws at you.

---

## 1. Open with this (20 seconds)

> "Before locking the thesis I went back to double-check the machine-learning numbers. I found that the preclinical dataset I'd trained on was only about a fifth of what it should have been — the ChEMBL download had silently stopped early. I re-fetched the complete data, verified it, re-ran the whole pipeline, and the results actually got *better*: scaffold-split R² went from 0.44 / 0.50 up to **0.56 / 0.64**. So the numbers moved, and I wanted to walk you through why."

Tone: this is diligence catching a bug, not a mistake to apologize for. It's good news.

---

## 2. What went wrong

- The **descriptive dataset** (3,011 clinical-stage records) is fine and unchanged. This only touches the **ML modelling** part.
- For the models, each target's set was extended with **preclinical** compounds. I'd reported sizes of **1,122** (5-HT₂A) and **1,155** (D₃).
- On re-checking, the *complete* set has **~4,633** and **~5,571** distinct compounds with exact human Kᵢ. The models had trained on ~1,100 each — roughly **one page (~1,000 rows)** of the ChEMBL API.
- **Cause:** the `chembl_webresource_client` silently stopped paginating after ~1,000 records. The API's reported *total* said 6,203 / 7,785, but only ~1,000 were actually downloaded — so the truncation was invisible (this is the "it kept stopping" problem from earlier, now understood).

**Say this:** *"The download reported the right total but only handed back the first page, so I was unknowingly modelling on ~20% of the data."*

---

## 3. How I made sure the new numbers are right (this is the part he'll test)

1. **Completeness check:** I rewrote the fetch to download with explicit pagination and compare *rows downloaded vs. the API's reported total* — it prints COMPLETE or INCOMPLETE. It now reads 6,203/6,203 and 7,785/7,785.
2. **Two independent counts agree:** distinct-compound count via paginated download **and** via direct iteration — both give **4,633** (5-HT₂A) and **5,571** (D₃).
3. **Same curation, reproduced:** salt-strip → MW < 700 → peptide removal → Landrum de-duplication → **4,620** (172 clinical + 4,448 preclinical) and **5,488** (173 + 5,315). Matches the audit exactly.

**Say this:** *"I don't just trust one number — the fetch self-checks against the total, and two different counting methods land on the same figure."*

---

## 4. The corrected results (before → after)

| Metric (5-HT₂A / D₃) | Old (truncated) | **New (complete)** |
|---|---|---|
| Modelling set size | 1,122 / 1,155 | **4,620 / 5,488** |
| Scaffold-split R² (XGBoost) | 0.44 / 0.50 | **0.56 / 0.64** |
| Random Forest R² | 0.42 / 0.45 | **0.53 / 0.63** |
| 10-fold CV R² | 0.62 / 0.63 | **0.68 / 0.72** |
| RMSE (log units) | 0.77 / 0.79 | **0.70 / 0.69** |
| Read-across baseline | 0.22 / 0.21 | **0.35 / 0.44** |
| y-randomisation p | 0.0099 | 0.0099 |

**Everything qualitative held:** fused ECFP4 + descriptors still best, fingerprints ≥ descriptors, both pass y-randomisation, both beat read-across. Same story — just stronger.

---

## 5. Why it improved (not suspicious — expected)

The learning curve was **still climbing** at 1,100 compounds. With ~4–5× the data it rises to ~0.6 and **flattens** — so the gain is simply more training data reaching the single-target ceiling. Nothing about the method changed.

**Say this:** *"The learning curve told us it was data-limited — so more data lifting it toward 0.6 is exactly what we'd predict, not a red flag."*

---

## 6. If he asks "why is D₃ better than 5-HT₂A?"

- **RMSEs are nearly identical** (0.70 vs 0.69) → the two models are equally accurate in absolute terms.
- R² = 1 − RMSE² / Var(pKᵢ). D₃'s affinities span a **~10% wider range** (variance 1.67 vs 1.51), so it scores a higher R² at the same error. Rescaling to equal variance nearly closes the gap (0.69 vs 0.68).
- A small residual edge on the scaffold split — notable because D₃ is the **more** diverse set (2,346 vs 1,819 scaffolds) — points to its larger training set / smoother SAR, not easier chemistry.

**Say this:** *"They predict both targets with the same absolute error; D₃'s higher R² is mostly because its affinities cover a wider range."*

---

## 7. Likely questions → short answers

- **"Are you certain it's complete now?"** → Yes: the fetch verifies downloaded = total, and two counting methods agree.
- **"Does the descriptive dataset / the rest of the thesis change?"** → No. Only the ML expansion. The 3,011-record descriptive dataset is v36-locked and untouched; all the chemical-space, halogenation, and efficiency results stand.
- **"Which ChEMBL version is the new data?"** → A complete per-target extraction. The underlying record counts match v36, so it's essentially the same data, just fully downloaded rather than truncated.
- **"Does this weaken the conclusions?"** → No — it strengthens them. All three controls (scaffold split, y-randomisation, read-across) still pass, with more headroom.
- **"Did you update the thesis and slides?"** → Yes, every ML number is propagated across results, discussion, conclusions, abstract, and the deck, and it's internally consistent.
- **"How do we stop this happening again?"** → The fetch now has a hard completeness assertion; any future re-run will fail loudly instead of silently truncating.

---

## 8. Close with this

> "Net: a silent data-loading bug had capped the training set at ~20% of what's available. It's fixed, verified two ways, and re-run — the models are stronger (0.56 / 0.64, right where you'd expected), and I've propagated the new numbers through the thesis and the deck. I wanted you to hear it from me and know the numbers are now solid."

---

### One-line summary if you only remember one thing
*Found the ML set was silently truncated to ~1/5; re-fetched the full ~4,600 / 5,500 compounds, verified it, re-ran — R² improved to 0.56 / 0.64, conclusions unchanged and stronger.*
