# Defence script — final

**For `Slide_FINAL.pptx`, 27 slides. This is the only script.** The same spoken text is in the deck's speaker notes, so presenter view and this page say the same thing.

Every number below was checked against the thesis or against your locked dataset on 12 and 13 October.

---

## Before you start

- **No animations in this deck.** Every click moves to the next slide. Ignore any old note that says "BUILD: three clicks" — it would have skipped you three slides ahead.
- **The number printed in each slide's corner is wrong on most slides** (leftover from an older deck). To jump during questions, type the **position** shown in the headings below and press Enter. The corner number is given in brackets so you can recognise the slide.
- **The deck has 27 slides.** The old calibration slide was removed.
- **Length:** about 2,770 spoken words, roughly 21 minutes at a calm pace. If you run long, see "Cut first" at the end.

## The story in one breath

Clinical-stage drugs are the cheapest route to new therapies, because they are already safe in humans. Finding new uses for them needs a record of what they bind and a model you can trust to predict binding where nobody measured it. Part One builds the record and finds the drugs are promiscuous: that is the opportunity. To predict binding, I chose learning from measured affinities over docking, because docking scores are a weak guide to binding strength and I had thousands of real measurements. But the data are thin, and a model on clinical compounds alone reaches only R² 0.35. Is that the method or the data? Expanding two receptors shows it was the data: 0.56 and 0.64 on chemistry the model has never seen, behind four controls. As a screen, MCC 0.63 at 98% of the enrichment ceiling. The learning curve shows the single-target ceiling, so the next step is a multitask model across the panel, which turns the Part One dataset into a repurposing screen.

---

## 1 · Title
*no corner number · ~25 s*

> Good morning. I'm Dagmawi Tarekegn Fikadu, and this is my thesis, supervised by Professor Giorgetti and Filippo Baldessari. It asks whether we can predict how strongly clinical-stage drugs bind their receptors, and whether that prediction can be trusted. That second half is the thread through the whole talk.

---

## 2 · Roadmap — the repurposing question
*corner shows 1 · ~75 s*

> The thesis starts from drug repurposing: finding new uses for drugs we already have. It has a real track record. Propranolol, a heart drug, was found by chance to shrink infant haemangiomas, and is now the first-line treatment. And in 2020, dexamethasone, a decades-old steroid, became the first drug shown to reduce deaths in severe COVID-19.
>
> It works because these drugs have already been through safety testing in humans, so a new use reaches patients faster and more cheaply than a new molecule. But many of these discoveries were luck. If a drug binds a receptor nobody tested it on, I would like to find that systematically.
>
> That needs two things. A clean record of what these drugs bind: that is Part One, where I curate and characterise a clinical-stage GPCR dataset. And a model that predicts binding where nobody has measured it: Part Two, which asks whether that prediction can be trusted.

**Hold:** sources, if asked: propranolol, Léauté-Labrèze et al., NEJM 2008; dexamethasone, the RECOVERY trial, NEJM 2021; sildenafil, the classic case, went from angina to erectile dysfunction to pulmonary hypertension (Ghofrani et al., Nature Reviews Drug Discovery 2006). All three are in the thesis introduction. · Don't use thalidomide as an example: your revision notes flagged it as teratogenic, the wrong fit for a "safe drugs" argument.

---

## 3 · Background — GPCRs and binding affinity
*corner shows 2 · ~30 s*

> First, the targets. G-protein-coupled receptors are the most productive drug-target class we have: about a third of approved drugs act through them. The aminergic family, serotonin, dopamine, adrenergic and muscarinic receptors, is especially rich in drugs. What I measure is binding affinity, Ki, on a log scale as pKi. Only one thing to remember: higher pKi means tighter binding.

---

## 4 · Part One — what was curated
*corner shows 3 · ~55 s*

> Part One. From ChEMBL I took human binding data for every compound that reached clinical phases one to four. Under 700 daltons, salts removed, peptides excluded, very flexible molecules filtered out, duplicates collapsed to the highest affinity. That gives 3,011 records: 719 unique molecules against 47 targets, in 18 receptor families. I curated by clinical stage, not by potency, on purpose. This is chemistry that has already survived selection.
>
> And it's diverse: those 719 molecules sit on 511 different scaffolds, and 83 per cent of the scaffolds appear only once. So this is a broad sample of aminergic chemistry, not a few analogue series, and that is why, in Part Two, the models are tested on whole scaffolds they have never seen.

**Hold:** a scaffold is the ring system plus the links between rings (Bemis–Murcko), side chains stripped off. · Clinical set: about 1.4 molecules per scaffold. The Part Two sets are less diverse — 1,936 scaffolds for 4,620 compounds and 2,607 for 5,488, about 2.4 and 2.1 per scaffold — because preclinical chemistry comes in analogue series: see question 3b.

---

## 5 · Part One — composition
*corner shows 4 · ~25 s*

> The set is strongly aminergic. Serotonin, adrenergic, dopamine, muscarinic and opioid receptors make up about 86 per cent of the records. And just over half of the drugs, 52 per cent, are approved. The rest reached phases one to three of clinical trials.

**Hold:** if someone quotes 70% from the thesis table, that is counted per row: approved drugs have more rows because they've been measured against more receptors. Per drug, it is 52%.

---

## 6 · Part One — polypharmacology
*corner shows 5 · ~40 s*

> And this is the property that matters most for repurposing. These drugs are promiscuous. On average each molecule acts on 4.19 different targets, and 64.7 per cent act on more than one. Tamoxifen alone hits 31. It crosses families too: 38 per cent act on more than one receptor family.
>
> That matters twice. It is the opportunity repurposing exploits. And it is why, later, I remove the most promiscuous drugs and retrain, to check the models do not depend on them.

---

## 7 · Part One — descriptors
*corner shows 6 · ~80 s*

> To characterise this chemistry I computed fifteen descriptors for every compound. Eleven describe the molecule itself: size, lipophilicity, solubility, polarity, flexibility and shape, the properties that decide whether a drug can be taken orally and reach the brain.
>
> The other four are composite scores. QED rolls eight properties into one drug-likeness score, from zero to one. The other three set potency against what it cost. Ligand efficiency is potency per heavy atom. Lipophilic ligand efficiency is potency minus LogP: the binding you get beyond what greasiness alone would give. And LELP is LogP divided by ligand efficiency, where lower is better.
>
> Together they tell a clear story. The set is drug-like, median QED 0.69, and size-efficient: three quarters clear the usual ligand-efficiency threshold of 0.3. But only 23 per cent reach the lipophilic-efficiency target of five. Many of these compounds lean heavily on lipophilicity to bind, a known weakness of aminergic drugs.
>
> Hold on to the number fifteen: in Part Two it scales to about two hundred.

**Hold:** QED is computed from structure alone; only LE, LLE and LELP use the measured pKi (the slide's subtitle groups all four loosely). · Formulas: LE = 1.37 × pKi ÷ heavy atoms; LLE = pKi − LogP; LELP = LogP ÷ LE. · Thresholds and sources: QED ≥ 0.67 high (Bickerton 2012); LE ≥ 0.3 (Hopkins 2004); LLE ≥ 5 (Leeson & Springthorpe 2007); LELP ≤ 7.5 optimal, > 10 poor (Keserű & Makara 2009). · 46.9% of records have poor LELP above 10. · The 1.37 converts pKi into kcal/mol of binding energy at room temperature.

---

## 8 · Part One — is the potency earned?
*corner shows 7 · ~55 s*

> That was lipophilicity. The other way to buy potency is size: add atoms, and affinity goes up. So is the potency in this dataset earned, or bought with size?
>
> Ligand efficiency answers that. On the right, efficiency falls steeply with size, Spearman minus 0.77. And the number that makes it concrete: compare the smallest compounds, twenty heavy atoms or fewer, with the largest, thirty-five or more. Median efficiency halves, from 0.52 to 0.24. Median affinity barely moves: 6.66 against 6.51. The extra size bought almost no potency. That is why efficiency, not raw potency, is the thing to optimise.

**Hold:** "≤20 heavy atoms" is roughly the smallest fifth (627 records), "≥35" the largest tenth (265). · Not cherry-picked: at ≤18/≥38, ≤22/≥33 or quartiles, LE always roughly halves and median pKi stays 6.5–7.0. · "LE has size in the denominator, so it must fall" — see question 7d. · These medians are per record; per molecule see question 7. · The efficiency axis is clipped at the 95th percentile, 0.65; every compound is still in the analysis.

---

## 9 · Part Two — the pivot
*corner shows 9 · ~100 s · the pivot: opportunity, choice, obstacle*

> So Part One leaves me with an opportunity, a choice, and an obstacle.
>
> The opportunity: nearly two-thirds of these drugs act on more than one receptor, exactly what repurposing exploits. To use it, I need to predict binding where nobody has measured it.
>
> The choice: how to predict it. One route is docking: fit each molecule into a 3D structure of the receptor and score the fit. Docking is very good at showing how a molecule sits in the pocket, but its scores are a weak guide to how strongly it binds. The other route is to learn from measured affinities, and I had just curated thousands of them. For a question about binding strength, learning was the better fit. The two are complementary, and combining them is a natural next step.
>
> The obstacle: learning needs data. My first model, on the clinical compounds alone, reached an R-squared of only about 0.35. Was that the method, my curation, or simply too few compounds? To test it, I took the two richest receptors, serotonin 5-HT2A and dopamine D3, shown here with their natural ligands, and extended each with preclinical ChEMBL compounds under the same curation rules: from 172 and 173 compounds to 4,620 and 5,488.
>
> Adding data raises an obvious worry about leakage. Answering it is the heart of this work.

**Hold:** why not docking — see question 1b. · The initial ~0.35 is in the thesis Discussion, opening of the modelling section. · Roughly 27-fold and 32-fold expansion.

---

## 10 · The task
*corner shows 10 · ~30 s*

> Part Two. The task in one line: a molecule goes in, a predicted pKi comes out. But a model is just a mathematical function. It takes numbers in and gives a number out. It cannot read a chemical drawing. So the first real step is translating each molecule into numbers, in two ways.

---

## 11 · Features I — ECFP4 fingerprints
*corner shows 11 · ~55 s · point at each circle as you name it*

> The first is a fingerprint, ECFP4, shown here on tyrosine, the natural precursor of dopamine. Take each atom and look at its neighbourhood out to two bonds. On the left, that captures the carboxylic acid. In the middle, the carbon carrying the amine. On the right, the phenol: the OH on the ring. Each fragment is hashed into one of 2,048 slots and switches it on: present is one, absent is zero. The picture shows three, but every atom is read at three sizes, so tyrosine actually switches on 24 bits. Two things matter. The length is always 2,048, whatever the size of the molecule. And molecules that share fragments share bits.

**Hold:** 13 heavy atoms → 24 bits. Each atom is read at radius 0 (itself), 1 (plus neighbours) and 2 (plus neighbours' neighbours); the "4" in ECFP4 is the diameter, four bonds. · Occasionally two different fragments land in the same slot, a collision: the price of a fixed length. · Similarity, by Tanimoto: tyrosine vs L-DOPA (one extra ring OH) 0.65; vs phenylalanine (one fewer OH) 0.70; vs dopamine only 0.25, because dopamine has lost the acid *and* gained an OH, and in a molecule this small two changes rewrite most local environments. · The fingerprint is stereo-blind: see question 7e.

---

## 12 · Features II — descriptors and the fused vector
*corner shows 12 · ~30 s*

> The second is descriptors: the fifteen from Part One, scaled up to about two hundred whole-molecule properties, like weight, lipophilicity, polar surface and charge. I join fingerprint and descriptors into one vector of 2,248 numbers. That is the only view of each molecule the model ever sees. Whether joining them actually helps, I tested rather than assumed.

**Hold:** DescriptaStorus is an open-source library built on RDKit (by Brian Kelley) that computes a standard panel of exactly 200 2D descriptors in one call; it is the same panel the Chemprop deep-learning package uses. · "Normalised" means each value is replaced by its percentile against a large reference set of molecules, so everything sits between 0 and 1. Tyrosine's molecular weight, 181, becomes 0.01: lighter than 99% of the reference. · Those reference distributions ship with the library, so normalisation uses nothing from my data and cannot leak test-set information. · Why normalise for trees: question 7g.

---

## 13 · The models
*corner shows 13 · ~35 s*

> The models are tree ensembles. Random Forest builds hundreds of decision trees on random subsets and averages them, so their errors cancel. XGBoost adds trees one after another, each correcting the mistakes of the last. I also ran a third, CatBoost, only to check the result does not depend on one method. At this data size, tree ensembles are competitive, robust, and much easier to interpret than deep learning.

---

## 14 · Validation — the scaffold split
*corner shows 14 · ~80 s · slow down here*

> This is the part I care most about, so I will slow down.
>
> The obvious test is a random split: hide twenty per cent of the compounds and train on the rest. On this kind of data it is misleading. Medicinal chemistry is full of analogue series, dozens of small variations on one core. A random split puts near-identical analogues on both sides, so the model just recognises what it has already seen. The score looks excellent, and it is inflated.
>
> The fix is to split by family. A scaffold is the core skeleton of a molecule: strip off the side chains, keep the rings and the links between them. Whole scaffold families go to one side together, so every test compound is chemistry the model has genuinely never seen. I repeat this twelve times with different random splits and report the mean.
>
> The score drops. And that drop is the point. It is the honest number.

**Hold:** grouping is by the exact Bemis–Murcko scaffold, not by similarity. For the stricter similarity-based split, see question 2 below. This is the most likely technical question of the day.

---

## 15 · Results — regression performance
*corner shows 15 · ~60 s · chart: fingerprint alone, descriptors alone, fused*

> So, the results. With fused features and XGBoost, the scaffold-split R-squared is 0.56 for 5-HT2A and 0.64 for D3, up from about 0.35 on the clinical compounds alone. So most of that ceiling was the data, and the learning curve in a moment shows exactly how.
>
> The other bars are the test I promised: was fusing worth it? For 5-HT2A, yes, modestly: together beats either part alone. For D3 the fingerprint already carries nearly everything, so fusion ties. The typical error, the RMSE, is 0.81 and 0.76 log units, about one and a half times the disagreement between laboratories. And Random Forest and CatBoost land in the same place, so performance is set by the data, not by the learner.

**Hold:** bar values: fingerprint alone 0.544 and 0.639, descriptors alone 0.521 and 0.598, fused 0.562 and 0.644. Descriptors alone are weakest on both targets: whole-molecule properties matter, but substructure matters more. · Inter-laboratory noise is about 0.5 log units, so 0.81 and 0.76 are 1.6 and 1.5 times that floor.

---

## 16 · Results — predicted versus experimental
*corner shows 16 · ~50 s*

> Here are the actual predictions on held-out compounds, both targets on the same axes. One thing first: the R-squared in the titles, 0.60 and 0.63, is for this single split. The twelve-split means are the 0.56 and 0.64 you just saw.
>
> The message is the slope: 0.58 and 0.61, not one. Look at the red bars. At the weak end the model over-predicts by about one log unit; at the potent end it under-predicts by one to one and a half. It pulls the extremes toward the middle, which is what a model minimising average error does. So the ranking is reliable, but absolute values are conservative at the potent end.

**Hold:** the predicted spread is about three quarters of the measured spread (SD 0.92 vs 1.24, and 0.98 vs 1.28).

---

## 17 · The gain is real — learning curve
*corner shows 18 · ~55 s*

> This is how we know the gain came from data. I trained on growing subsets and measured R-squared on held-out compounds each time, five scaffold splits per point.
>
> R-squared climbs steeply, then flattens. For 5-HT2A it goes from 0.25 with 200 training compounds to 0.56 with the full set. But the first thousand compounds deliver most of that; the last seventeen hundred add less than 0.01.
>
> That flat tail is the important part. The model is near the ceiling you can reach from one target's data with this representation. More of the same data will not help. To go further you have to share information across targets, and that is where this thesis ends up.

**Hold:** the x-axis stops at 3,696 and 4,390 because that is the 80% training pool; the other 924 and 1,098 compounds are the test set. · D3 sits above 5-HT2A at every matched training size, so its relationship is easier to learn, not just better supplied.

---

## 18 · Validation — what random folds would have claimed
*corner shows 19 · ~35 s · chart: scaffold split vs 10-fold cross-validation*

> One more look at what the scaffold split costs. Standard ten-fold cross-validation lets close analogues fall on both sides of every split. It would report 0.68 and 0.72. The scaffold split reports 0.56 and 0.64. That gap of about 0.1 is exactly the inflation the scaffold split removes. Both numbers are in the thesis so the gap is explicit, and the lower one is the number I stand behind.

**Hold:** cross-validation RMSE is 0.70 and 0.69, against 0.81 and 0.76 on the scaffold split.

---

## 19 · Controls — chance, and the similarity lookup
*corner shows 21 · ~60 s*

> Two controls stand behind these numbers.
>
> First, chance. I shuffled the affinity labels and retrained a hundred times. R-squared collapsed every time, and no shuffled model reached the real one: p equals 0.0099, the floor for a hundred permutations.
>
> Second, the harder one. The most deflating explanation for a good score is that the model has simply memorised which training compound each test compound looks like. So I built exactly that as a baseline: give each test compound the affinity of its most similar training compound. No learning at all. That reaches 0.35 and 0.44. The models reach 0.56 and 0.64, about 0.2 higher. They are learning structure-activity relationships, not doing a disguised lookup.

**Hold:** the permutation test has its own section, 3.5.4, and figure in the thesis. Read-across exact values: 0.347 and 0.435.

---

## 20 · Robustness — the promiscuous drugs
*corner shows 22 · ~35 s*

> Remember the promiscuous drugs from Part One. A fair worry is that the models lean on a handful of famous multi-target compounds. So I removed every compound hitting five or more targets, 136 for 5-HT2A and 117 for D3, and retrained. R-squared did not drop. It rose slightly: 0.56 to 0.58, and 0.64 to 0.67. If anything, those compounds are harder to fit.

**Hold:** why removal helps: a molecule built to hit many targets sits where any single target's structure-activity relationship is weaker. · Classifier version: see question 11.

---

## 21 · Interpretation — what drives the regression
*corner shows 23 · ~30 s*

> Last question for the regression: what is the model actually using? SHAP traces each prediction back to the input features. The two receptors rely on different chemistry. 5-HT2A is driven mostly by charge and electrostatic descriptors. D3 leans on shape and branching, topological indices like Balaban J. That split is chemically sensible, and it means the models are not black boxes.

---

## 22 · Virtual screening — where the line falls
*corner shows 24 · ~60 s*

> Now the same models as a screening tool, which is closer to how they would actually be used, and back toward repurposing. First, the task itself. Every compound here is a measured binder, so I am not separating binders from non-binders. I am separating potent from weak. The cut is 100 nanomolar, the solid line. That splits the libraries 59 to 41 and 67 to 33: two real classes.
>
> Why not 1 micromolar, the usual screening cut-off? That is the dashed line. Almost everything here binds at least that well, so 85 and 87 per cent would be called active, and MCC, which I will define in a moment, falls from 0.63 to 0.35 and 0.43. The threshold is not tuned to flatter the result. It is where this library actually has two classes.

---

## 23 · Virtual screening — the classifier
*corner shows 25 · ~40 s*

> Here is the classifier itself, on one representative split: the one closest to the median, not the best. Read the top-left of each panel. For 5-HT2A, 444 of 534 true actives found, and 325 of 393 inactives correctly rejected: 68 false alarms, 90 misses. For D3, 637 of 731 actives found. Notice the balance: it is not just calling everything active. Every metric on the next slide can be recomputed from these four numbers.

**Hold:** this split is seed 10; its MCC is 0.654 and 0.639 against twelve-split means of 0.635 and 0.632. · Recall and specificity are both 0.83 for 5-HT2A; for D3, 0.87 and 0.77.

---

## 24 · Virtual screening — what the metrics measure
*corner shows 26 · ~70 s*

> Two metrics, and what they mean, because a number alone means nothing.
>
> MCC first. Accuracy lies when one class dominates. This library is 59 and 67 per cent active, so a model that always says "active" scores 59 per cent and is useless. The Matthews correlation coefficient uses all four cells you just saw, so it only rises when both classes are called correctly. Plus one is perfect, zero is chance. Ours is 0.635 and 0.632, across twelve scaffold splits.
>
> Enrichment second, and it asks a practical question: if you only test the compounds the model likes most, the top one per cent, how many are real actives? Here, almost all of them. On this library that scores 1.67, and the best any model could possibly score is 1.69.

**Hold:** ROC-AUC is about 0.90 for 5-HT2A and 0.92 for D3: see question 6. · All three learners give MCC 0.61–0.64. · If anyone asks you to compare MCC with R²: see question 6b. · The top 1% is about nine compounds per split, averaged over twelve splits: see question 6c. · Enrichment detail: 1 means random; the ceiling is 1 ÷ the active fraction (59% active gives 1.69). D3 scores 1.46 against a ceiling of 1.49. Both are about 98% of the best possible.

---

## 25 · Interpretation — what the classifier keys on
*corner shows 28 · ~40 s*

> Last result. Does the classifier rely on the same chemistry as the regression? I ran SHAP again. The rank agreement between the two is 0.90 for 5-HT2A and 0.87 for D3. Ask the model a different question, and it leans on the same features. Charge-related surface areas still lead for 5-HT2A; for D3, Balaban J alone carries 18 per cent of the attribution. So the interpretation is a property of the data, not of how I set up the model.

**Hold:** the axis is in log-odds, so ranks compare with the regression figure but magnitudes do not. · Salt bridge: see question 10.

---

## 26 · Limitations
*corner shows 30 · ~40 s*

> What this work does not establish. The labels are pooled from many laboratories, and laboratories agree only to about half a log unit, which puts a floor under the error. Only two targets, chosen because they had enough data. The representation is two-dimensional: no 3D shape, no protein structure, which is exactly what docking would add. Validation is internal: careful and repeated, but there is no external or prospective test set. And hyperparameters are sensible defaults rather than fully tuned. Each of these is a concrete next step, not something I am hiding.

---

## 27 · Conclusions — closing the loop
*corner shows 31 · ~85 s*

> To close the loop.
>
> Part One produced a curated dataset of clinical-stage GPCR drugs that did not exist in this form: 719 molecules and 3,011 records, with their chemistry and their promiscuity mapped.
>
> Part Two answered the question repurposing depends on. On these two receptors, binding can be predicted on chemistry the model has never seen: R-squared 0.56 to 0.64, and as a screen, MCC 0.63 with enrichment at 98 per cent of its ceiling. Those numbers survive a scaffold split, a permutation test, a similarity baseline and a promiscuity check.
>
> And the learning curve tells me where the next gain has to come from: not more single-target data, but sharing information across targets. A multitask model over the whole panel could score all 719 clinical molecules against receptors they were never tested on. That is the repurposing screen this work makes possible.
>
> Thank you to Professor Giorgetti, to Filippo, to the professors of the programme, and to my family. I am happy to take questions.

---

## Cut first, if you are running long

About a minute, without touching the story:

- **Slide 13:** drop the CatBoost sentence and the last sentence.
- **Slide 18:** "Random folds would claim 0.68 and 0.72; the scaffold split says 0.56 and 0.64. The lower number is the honest one."
- **Slide 16:** drop the "Look at the red bars…" sentence.
- **Slide 22:** second paragraph becomes "Why not 1 micromolar? Almost everything here binds that well, so there would be hardly any inactives left. 100 nanomolar is where this library actually has two classes."

Never cut slides 2, 9, 14, 17 or 27. They carry the story.

---

## Questions you are likely to get

**1. "Did you find any repurposing candidates?"**
No, and I'd rather say that plainly. This thesis answers the prior question: can binding be predicted reliably on unseen chemistry? Naming candidates needs a model that works across the whole panel. Nominating new targets from a model validated on two receptors would be exactly the overclaim the validation work was built to prevent.

**1b. "Why machine learning and not docking?"** *(likely, in this group)*
They answer different questions best. Docking is very good at pose: how a molecule sits in the pocket. But docking scores are a weak guide to binding strength — a well-known limitation; for example, Warren and colleagues' 2006 assessment in the Journal of Medicinal Chemistry found docking scores tracked measured affinity poorly. My question was binding strength, and I had thousands of measured affinities, so learning from them was the direct route. Structures exist for both receptors, and docking scores or 3D descriptors would add exactly what my 2D fingerprints lack: that is the second future direction in my conclusions, and the learning curve says it's the right moment, because 2D single-target data is near its ceiling.
*If pushed on free-energy methods (FEP, MM-GBSA):* they do much better on affinity, but they're far too expensive for thousands of diverse compounds. They're the right tool for a handful of close analogues, not a whole library.

**2. "Is the scaffold split strict enough? Two different scaffolds can still be near-identical."** *(most likely technical question)*
Fair point, and I tested it. The scaffold split groups by the exact Murcko scaffold, so two similar but formally different scaffolds can sit on opposite sides. That is why the read-across baseline matters: it is exactly the strategy that would exploit leftover similarity, and the models beat it by about 0.2. I also ran a stricter split, section 3.5.9: compounds grouped into connected components at Tanimoto 0.60, so no test compound has a close training neighbour by construction. I used connected components rather than Butina clustering because Butina clusters are not transitively closed, so they don't actually guarantee the separation. Under that split, MCC roughly halves, to 0.33 and 0.30. For D3 the model still beats read-across, 0.296 against 0.234, winning 11 of 12 splits, p = 0.016. For 5-HT2A it does not: 0.328 against 0.331, p = 0.73. I reported that rather than leaving it out.

**3. "Your title says clinical-stage, but you trained on preclinical compounds."**
Yes, and deliberately. On clinical compounds alone the data were too thin: 172 and 173 compounds per target, R² about 0.35. I extended with preclinical compounds under the same curation rules, and the scaffold split still holds out whole scaffold families, so every test compound remains new to the model. The clinical-stage dataset is Part One's contribution; the expansion was how to test whether the prediction step works.

**3b. "Your clinical set is diverse, but the preclinical compounds you added come in analogue series. Doesn't that change things?"**
Yes, the Part Two sets are less diverse: about 2.4 compounds per scaffold for 5-HT2A and 2.1 for D3, against 1.4 in the clinical set. That is exactly where a random split would leak close analogues into the test set, so it is where the scaffold split matters most. It's also why cross-validation scores 0.68 and 0.72 while the scaffold split gives 0.56 and 0.64.

**4. "The plot says R² 0.60 but your table says 0.56."**
The plot is one split; 0.56 and 0.64 are the means over twelve scaffold splits. Single splits scatter around the mean.

**5. "A slope of 0.58 — is the model biased?"**
It is regression toward the mean, the expected behaviour of a model minimising squared error on unseen chemistry. It compresses the extremes, so absolute predictions are conservative at the potent end, but the ranking holds. That is why the screening view, which depends on ranking, is the strongest result.

**6. "Why lead with MCC instead of ROC-AUC?"**
ROC-AUC averages over every possible threshold, including ones you would never use. MCC judges the model at the threshold it is actually used at, and it is only high if all four cells of the confusion matrix are good. ROC-AUC is about 0.90 and 0.92 here and it is in the thesis, so the two agree: the model ranks well. And unlike accuracy, MCC can't be gamed by always answering "active".

**6b. "Your MCC is 0.63 and your R² is 0.56 — so is the classifier the better model?"**
Not directly comparable. MCC is a correlation where chance is zero; R² is the share of variation explained. If you want MCC's closer cousin to R², it's MCC squared, about 0.40. The fair statement is that both are well above chance, and that the classifier is the more useful view for screening because it only has to get the side of the cut right, not the exact value.

**6c. "The top 1% of your test set is only about nine compounds. Isn't enrichment noisy?"**
On one split, yes, which is why it's averaged over twelve splits. And it agrees with the rest of the picture: ranking compounds by how confident the model is that they're active finds actives faster than random across the whole list, not just at the top, and MCC at the threshold is 0.63.

**7. "Is the ligand-efficiency comparison per record or per molecule?"**
Per record. Per molecule, using each molecule's best affinity, efficiency still halves, 0.62 to 0.30, but the largest molecules are somewhat more potent. The point about efficiency holds either way; the "potency barely moves" part is a record-level statement.

**7b. "Why is relying on lipophilicity a problem?"**
Greasy compounds tend to dissolve poorly, bind many things non-specifically, and carry more toxicity risk; that is the point of Leeson and Springthorpe's LLE target. For brain drugs there is a real trade-off, because some lipophilicity is needed to cross the blood–brain barrier, which is partly why aminergic drugs end up here.

**7c. "QED doesn't use affinity — why is it in the efficiency group?"**
Right, it doesn't. QED is a drug-likeness score from structure alone. The other three are the efficiency metrics; QED sits with them on the slide because all four are composite scores built from the eleven basic descriptors.

**7d. "LE has heavy atoms in the denominator, so of course it falls with size. Isn't that just arithmetic?"**
Yes, which is exactly why the slide shows the second number. If bigger molecules bound proportionally more tightly, affinity would rise with size and efficiency would stay flat. It doesn't: median pKi stays between about 6.2 and 6.9 in every size band, from under 15 heavy atoms to over 40. The finding is that affinity doesn't keep pace with size; ligand efficiency is just the clearest way to show it. And it doesn't depend on where I draw the lines: with other cut-offs or quartiles, efficiency always roughly halves while affinity stays in the same band.

**7e. "You drew the stereocentre on tyrosine — does the fingerprint see it?"**
No. I computed ECFP4 stereo-blind, so L- and D-tyrosine get identical fingerprints. That is the usual default for this kind of model, and it is part of the 2D limitation on slide 26: the fingerprint sees which atoms are connected, not how they are arranged in space. (The scaffold split, by contrast, does keep stereochemistry when grouping scaffolds.)

**7f. "Are tyrosine and dopamine similar to your fingerprint?"**
Less than you'd think: Tanimoto 0.25. Dopamine has lost the carboxylic acid and gained a second ring OH, and in a molecule this small those two changes rewrite most of the local environments. L-DOPA, the step in between, differs by one OH and is still 0.65.

**7g. "What is DescriptaStorus, and why normalise the descriptors if you use tree models?"**
It's an open-source library built on RDKit that computes a standard panel of 200 descriptors, the same panel Chemprop uses. Normalised means each value becomes its percentile against a large reference set of molecules. For tree models that makes essentially no difference, because a tree only cares about the order of values and a percentile keeps the order. Its useful property here is that the scaling comes from a fixed external reference, not from my data, so it can't leak test-set information. It would matter more if the next step were a neural network.

**8. "Why not deep learning or graph neural networks?"**
At a few thousand compounds per target, tree ensembles are competitive and far easier to interpret. Where deep learning makes sense is the next step: a multitask model across the whole receptor panel, which is exactly the way past the single-target ceiling.

**9. "Why only two targets?"**
They were the only two with enough data to train and validate honestly at the same time. The pipeline is general; showing the numbers transfer across the panel is future work, and it is listed as a limitation.

**10. "Does SHAP show the model learned the salt bridge to the aspartate?"**
The two largest charge terms run in the expected direction, but across all the charge bins there is no clean monotonic trend, so I would not claim the model recovered the mechanism. It learned something more specific than "positive charge binds better".

**11. "Your Methods say the promiscuity test covers classification too, but the Results show only regression."**
I ran it on the classifier as well, and it gives the same answer: MCC 0.632 to 0.662 for 5-HT2A and 0.633 to 0.635 for D3. Only the regression version made it into the Results section, which I should have included.

**12. "Why does the learning curve stop at 3,696?"**
That is the training pool, 80 per cent of the 4,620. The other 924 compounds are the test set every point is measured on.

---

## Numbers to know cold

| | 5-HT2A | D3 |
|---|---|---|
| Clinical compounds → modelling set | 172 → 4,620 | 173 → 5,488 |
| Clinical-only R² (before expansion) | ≈ 0.35 | |
| Scaffold R² (12 splits) | **0.562** | **0.644** |
| Scaffold RMSE | 0.81 | 0.76 |
| Read-across R² | 0.347 | 0.435 |
| Parity slope | 0.58 | 0.61 |
| MCC (12 splits) | **0.635** | **0.632** |
| Enrichment @1% (ceiling) | 1.67 (1.69) | 1.46 (1.49) |
| Confusion, seed 10: TP / FP / FN / TN | 444 / 68 / 90 / 325 | 637 / 85 / 94 / 286 |
| SHAP agreement, regression vs classifier | 0.90 | 0.87 |
| Stricter cluster split, MCC | 0.33 | 0.30 |

Dataset: **3,011** records · **719** molecules · **47** targets · **18** families · **4.19** targets per molecule · **64.7%** multi-target · **52%** of drugs approved · permutation **p = 0.0099**.

Part One metrics: median QED **0.69** · **75.7%** with LE ≥ 0.3 · only **23%** with LLE ≥ 5 · **46.9%** with poor LELP > 10.

---

## Metrics in plain words

| Metric | The question it answers | Scale | Yours |
|---|---|---|---|
| **pKi** | How tightly does it bind? | +1 = ten times tighter; 7 = 100 nM | — |
| **R²** | How much of the real spread does the model explain, compared with always guessing the average? | 0 = no better than the average · 1 = perfect · can go negative | 0.56 / 0.64 |
| **RMSE** | How big is a typical miss? | in pKi units, lower is better | 0.81 / 0.76 = a factor of ~6 in Ki (labs disagree by ~3) |
| **Parity slope** | Do the predictions spread as widely as reality does? | 1 = full spread | 0.58 / 0.61: squeezed toward the middle |
| **Tanimoto** | How much do two fingerprints overlap? | shared bits ÷ bits in either; 0 to 1 | used to find the nearest neighbour |
| **Permutation p** | Could shuffled labels do this well by luck? | small = no | 0.0099: none of 100 shuffles reached it |
| **Recall** | Of the real actives, how many were found? | 0 to 1 | 0.83 / 0.87 |
| **Specificity** | Of the real inactives, how many were rejected? | 0 to 1 | 0.83 / 0.77 |
| **Accuracy** | How many calls were right? | 0 to 1 | 0.83, but "always active" scores 0.58 doing nothing |
| **MCC** | Do the calls correlate with the truth, using all four boxes? | −1 to +1, 0 = chance | 0.635 / 0.632 |
| **EF @ 1%** | How much richer in actives is the top 1% than the whole list? | 1 = random; maximum = 1 ÷ active fraction | 1.67 / 1.46, maximum 1.69 / 1.49 |
| **ROC-AUC** | Is a random active ranked above a random inactive? | 0.5 = random, 1 = perfect | about 0.90 / 0.92 |
| **SHAP** | How much did each feature push this prediction up or down? | per feature, per compound | charge (5-HT2A), shape (D3) |
| **Spearman ρ** | Do two rankings agree? | −1 to +1 | −0.77 size vs LE; 0.90 / 0.87 the two SHAP rankings |

**The two pairs people mix up.** *R² vs slope:* R² is how tightly the points hug a line; the slope is the line's tilt. 0.60 and 0.58 on slide 16 are different measurements that happen to be close. *Accuracy vs MCC:* accuracy counts right answers and can be gamed by always saying "active"; MCC is only high if both classes are called well.
