# Plain-language answers for the defense

Every entry: what the thing is, then **the sentence to say out loud** to a
biologist who has never trained a model. Analogies are yours to use freely.
Where there is a way to get it wrong, that is flagged as a **trap**.

---

## 1. The quantity being predicted

### Kᵢ and pKᵢ
Kᵢ is the concentration of compound at which half the receptors are occupied.
Lower Kᵢ means tighter binding. pKᵢ is minus the base-10 log of Kᵢ in molar.

> **Say:** "Kᵢ is the concentration you need to occupy half the receptors, so
> lower is better. We take the negative log so that bigger is better and the
> numbers stay small. pKᵢ 9 is 1 nanomolar, pKᵢ 7 is 100 nanomolar, pKᵢ 6 is
> 1 micromolar. Every whole unit is a tenfold change in potency."

**Trap:** do not say "affinity" and "potency" interchangeably if pushed. This is
binding affinity from a binding assay, not functional potency.

---

## 2. Turning a molecule into numbers

### Descriptor
One number computed from the structure, describing a property of the whole
molecule: weight, lipophilicity (LogP), polar surface area, ring count.

> **Say:** "A descriptor is a single number summarising one property of the
> whole molecule. It is like describing a person by height, weight and age.
> You lose the person, but you keep something you can compute with."

### Molecular fingerprint (ECFP4)
A fixed-length vector of on/off bits. Each bit records whether a particular
small substructure is present.

> **Say:** "Imagine a checklist of 2,048 possible chemical fragments. For each
> molecule we tick the boxes for the fragments it actually contains. The
> molecule becomes a barcode of 2,048 ones and zeros. Two molecules with
> similar barcodes are structurally similar."

The "4" in ECFP4 is the diameter: we look out to **two bonds** from each atom.

> **Say (if pushed on how it is built):** "For every atom we take its local
> neighbourhood out to two bonds. That neighbourhood is a small fragment. We
> hash each fragment into one of 2,048 slots and set that bit to one."

**Honest caveat if someone is sharp:** hashing means two different fragments can
land in the same bit. That is a known cost of folding to a fixed length, and it
is why fingerprint bits are interpreted as *indicative* rather than exact.

### Why a fixed length matters
> **Say:** "A model is a mathematical function. It needs the same number of
> inputs every time. Molecules come in all sizes, so the fingerprint is what
> makes a 15-atom molecule and a 50-atom molecule comparable to the model."

### The fused 2,248-dimensional vector
> **Say:** "2,048 yes/no fragment flags, plus about 200 numeric properties.
> Every molecule becomes a list of 2,248 numbers, and that list is literally
> everything the model knows about it. It never sees the drawing."

---

## 3. The models

### Decision tree
> **Say:** "A flowchart of yes/no questions. Is LogP above 3? Does it contain
> this ring? Follow the branches and you land on a predicted pKᵢ. A single tree
> is crude and memorises noise, which is why nobody uses one alone."

### Random Forest
> **Say:** "Grow hundreds of trees, each on a random subset of the compounds and
> a random subset of the features, then average their answers. Each tree is
> wrong in its own way, so averaging cancels the independent errors. It is the
> same reason a crowd guessing the weight of an ox beats almost every
> individual in the crowd."

### Gradient boosting (XGBoost, CatBoost)
> **Say:** "Trees built one at a time, in sequence. The first makes a rough
> prediction. The second is trained only on what the first got wrong. The third
> on what still remains. Like successive drafts of an essay, each one fixing the
> previous draft's mistakes."

### Why three models and not one
> **Say:** "To show the result is a property of the data and the representation,
> not of one lucky algorithm. All three land within 0.03 R² of each other, which
> is the point."

### Why not deep learning
> **Say:** "Neural networks need far more data than 5,000 compounds to beat tree
> ensembles on tabular chemistry. At this scale trees are competitive, more
> robust and much easier to interpret. That is the current consensus, not a
> shortcut."

---

## 4. Validation, the heart of the talk

### Training set and test set
> **Say:** "You fit the model on one part of the data and score it on a part it
> has never seen. Scoring it on the data it learnt from would be like giving
> students the exam questions in advance."

### Overfitting
> **Say:** "When a model memorises the training data instead of learning the
> pattern. It looks excellent on what it has seen and fails on anything new.
> With 2,248 features and about 5,000 compounds, that is the main risk in my
> work, and it is why so much of this talk is validation rather than results."

### Data leakage
> **Say:** "Leakage is when information from the test set quietly reaches the
> model during training. The score then looks good for the wrong reason."

### Scaffold (Bemis-Murcko)
> **Say:** "The core skeleton of the molecule. Strip off every side chain and
> keep the ring systems plus the linkers between them. It is the family surname
> of the molecule: a whole series of analogues from one medicinal chemistry
> programme will share one scaffold."

### Scaffold split (the key idea)
> **Say:** "Instead of splitting compounds at random, I split by family. Every
> member of a scaffold family goes to the same side. So the test set contains
> chemistry the model has genuinely never seen, not close cousins of what it
> learnt."

> **The analogy that lands:** "A random split is like testing a student on the
> same exam questions with the numbers changed. A scaffold split is testing them
> on a topic they have not been taught. The second score is lower, and it is the
> one that tells you whether they understood."

**If asked whether it is similarity-based:** no, and be precise. Molecules are
grouped by their exact Murcko scaffold string, and whole groups go to one side.
It is not Butina or Tanimoto clustering. Two chemically similar but formally
different scaffolds could in principle sit on opposite sides. That is exactly
why I also report the nearest-neighbour read-across baseline, which is the
strategy that would exploit any leftover similarity, and the model beats it.

### Cross-validation
> **Say:** "Cut the data into ten parts, train on nine, test on the tenth, then
> rotate so every part gets used as the test once, and average. It uses the data
> efficiently. But standard cross-validation splits at random, which is why I
> report it alongside the scaffold number rather than instead of it."

### Why 12 splits
> **Say:** "One split is one draw of the luck. I repeat the scaffold split over
> 12 randomised partitions and report the mean with a confidence interval, so
> the number is not an accident of which families happened to be held out."

---

## 5. Reading the scores

### R²
> **Say:** "R² asks how much of the variation in the real affinities the model
> explains. One is perfect. Zero means you would do just as well always guessing
> the dataset average. My 0.56 means the model explains 56 percent of the spread
> in binding affinity, across compounds it has never seen."

**Trap:** never say "56 percent accurate." R² is variance explained, not accuracy.

### RMSE
> **Say:** "The typical size of the error, in the same units as the answer. Mine
> is about 0.7 pKᵢ units. So a typical prediction is off by 0.7 log units, which
> is about a fivefold error in concentration."

### The noise floor
> **Say:** "If you measure the same compound against the same receptor in two
> different laboratories, the answers differ by roughly 0.5 log units. That is
> irreducible: no model can beat it, because the labels themselves disagree by
> that much. My 0.7 is about one and a half times that floor. A large part of my
> remaining error is noise in the data, not weakness in the model."

### Regression to the mean (why the predictions are compressed)
> **Say:** "The model is cautious at the extremes. Predicting near the average is
> the safest way to minimise average error, so it rarely commits to the very
> highest or very lowest affinities. The predicted spread is about three
> quarters of the real spread. That is a known and expected behaviour, and it is
> the honest limitation of the model for finding the most potent compounds."

### Learning curve
> **Say:** "Train on 10 percent of the data, then 20, then 40, and plot the
> score against how much data you used. If it is still climbing you are limited
> by data. If it is flat, more data will not help. Mine climbs from about 0.3 to
> about 0.6 and then flattens, which tells me the gain came from data and that I
> am near the ceiling for a single-target model."

---

## 6. The controls

### Y-randomisation (permutation test)
> **Say:** "I shuffled the affinity labels at random, so each molecule was paired
> with someone else's answer, and retrained 100 times. If the model were merely
> fitting noise with 2,248 features, it would score about the same. Instead R²
> collapsed to roughly minus 0.08. That is direct evidence the signal is real."

> **Analogy:** "It is how you test whether a stock picker has skill: give them
> scrambled price data and see if they still look good."

### Read-across / 1-nearest-neighbour baseline
> **Say:** "The most deflating explanation for a good QSAR score is that the
> model has just memorised which training compound each test compound resembles.
> So I built exactly that strategy as a baseline: for each test compound, find
> its single most similar training compound and copy its affinity. No learning
> at all. My model beats it by about 0.2 R², which means it is learning
> aggregate structure-activity, not doing lookup."

### Tanimoto similarity
> **Say:** "A number from zero to one for how much two fingerprints overlap:
> the bits they share divided by the bits either one uses. One means the same
> fragments, zero means nothing in common."

### Promiscuity ablation
> **Say:** "A fair worry is that the performance rests on a handful of famous
> multi-target drugs. So I removed every compound hitting five or more targets
> and retrained. Performance did not drop, it rose slightly. The result does not
> depend on those compounds."

---

## 7. The virtual screening view

### Regression vs classification
> **Say:** "Regression predicts a number, the pKᵢ. Classification predicts a
> category: active or not, at a 100 nanomolar cut-off. Screening campaigns
> actually work as classification and ranking, so I report both."

### MCC (Matthews correlation coefficient)
> **Say:** "Accuracy is misleading when one class dominates. If 90 percent of
> your library is active, a model that says 'active' every single time is 90
> percent accurate and completely useless. MCC uses all four cells of the
> confusion matrix, so it only scores high when both actives and inactives are
> called correctly. Plus one is perfect, zero is chance."

### Enrichment factor
> **Say:** "Rank the library by predicted affinity, take the top one percent,
> and ask how much richer in true actives that slice is than the library as a
> whole. One means random ranking. Mine is 1.67."

**Important nuance, worth volunteering:** the ceiling on enrichment is one
divided by the active fraction. In a majority-active library the ceiling is low,
so 1.67 is close to the maximum achievable rather than a modest result.

### Why ROC-AUC was dropped
> **Say:** "Every compound in my set is a measured binder, so at the 100
> nanomolar cut-off the library is majority active. ROC-AUC and accuracy both
> flatter a model on such a library. MCC and enrichment do not. This was a
> deliberate choice, and the AUC numbers are in the backup table for
> completeness."

### What the screen does and does not show
> **Say, unprompted:** "I want to be clear that this ranks potent binders above
> weaker binders. It is not a binder-versus-decoy screen, because every compound
> in my set is a measured binder. A true screen would need inactive data my
> dataset does not contain."

---

## 8. Interpretation

### SHAP
> **Say:** "For one prediction, SHAP splits the predicted value into
> contributions from each input: this descriptor pushed the prediction up by
> 0.3, that one pulled it down by 0.1. Average the sizes of those contributions
> over many compounds and you see which property families the model actually
> relies on. It comes from game theory, where the same maths divides a payout
> fairly among players."

### What SHAP found, in one sentence
> **Say:** "The two receptors rely on different property families. 5-HT₂A is
> driven by charge and electrostatics, dopamine D₃ by molecular shape and
> topology. That is chemically sensible and it is not something I put in by
> hand."

**Trap:** SHAP shows what the *model* uses, not what the *receptor* uses. If
someone presses, concede that immediately: it is a statement about the model's
reasoning that happens to agree with known pharmacology, which is reassuring but
not a structural claim.

### Applicability domain
> **Say:** "The region of chemical space where the model has enough neighbours to
> be trusted. A prediction on something far outside the training chemistry is
> extrapolation, and I would not act on it."

---

## 9. Three sentences to have ready

**"What is new here?"**
> "A curated clinical-stage GPCR ligand dataset that did not exist in this form,
> characterised across fifteen descriptors, and a leakage-controlled modelling
> template on top of it. The contribution is not a record score, it is a result
> that survives a scaffold split, a permutation test, a nearest-neighbour
> baseline and a promiscuity ablation."

**"Is 0.56 good?"**
> "For a scaffold split on a single target, yes. Benchmarking of single-assay
> models on genuinely novel held-out compounds reports a median R² near 0.12.
> Values around 0.55 are usually reached only by multitask models pooling
> thousands of assays. And my error is within about one and a half times the
> experimental noise floor."

**"What would you do next?"**
> "Extend across the receptor panel to test whether the pipeline transfers,
> move from 2D to 3D or structure-aware representations, and add inactive data
> so a genuine binder-versus-decoy screen becomes possible."
