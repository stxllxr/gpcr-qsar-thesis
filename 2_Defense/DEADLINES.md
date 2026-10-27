# Deadlines and open items — updated 18 September 2026

**Proclamation: 16 October 2026.** Not a guess any more — that is the official
date for Molecular and Medical Biotechnology LM-9 in the university's own
*Scadenziario*. Every letter and CV that says "available from 16 October" is
correct.

Source (the authoritative document, not a web page):

- Scadenziario, English: <https://cdn.docs.univr.it/documenti/Documento/allegati/allegati955336.pdf>
- Scadenzario, Italian: <https://cdn.docs.univr.it/documenti/Documento/allegati/allegati622176.pdf>
- Sessions page: <https://www.univr.it/it/i-nostri-servizi/gestione-carriere-studenti-scienze-e-ingegneria/sessioni-di-laurea-scienze-e-ingegneria->

---

## Hard dates

| Date | What | Status |
|---|---|---|
| 13 Jul – 27 Aug | Domanda di laurea window | ⚠️ **closed** — verify on ESSE3, see below |
| 27 Aug | Proposal of 2 controrelatori (LM-9) | ⚠️ past, tied to the domanda |
| 14 Sep | Thesis summary → carriere.scienze | ✅ sent |
| 16 Sep, 22:59 IT | Helsinki EpiTheraRx | ⬜ status unknown |
| **25 Sep** | **TagTIC** (Austria, 11 posts) | ⬜ 7 days — NOT yet verified |
| **30 Sep, 23:59** | **FINAL THESIS UPLOAD (PDF/A, signed)** | 🔴 **12 days — new, see below** |
| **30 Sep** | **ETH Zurich / Riniker** | ⬜ you write this one yourself (no AI) |
| **1 Oct** | **HARPNET** (DC8 + DC11) | ⬜ deadline confirmed |
| **1 Oct** | **DECODES** (15 posts, up to 3 choices) | ⬜ best eligibility fit |
| **5 Oct** | **POLARIS** (DC6 primary) | ⬜ blocked on Selent's answer |
| ~6 Oct | Everything registered in carriera | ⬜ 10 days before proclamation |
| **16 Oct** | **Proclamation** | — official |
| **1 Nov** | **AITHYRA, Vienna** — incl. referee letters | ⬜ strongest fit yet, see below |
| 9 Nov | Newcastle / Eli Lilly | ❌ ruled out — UK home fees only |
| none | Mainz / Czodrowski | ⬜ rolling; needs transcripts + referees |
| none | Gatsby Unit, UCL | ⚠️ long shot — see below |

---

## AITHYRA — Vienna, and worth taking seriously

Research Institute for Biomedical Artificial Intelligence, Austrian Academy of
Sciences. <https://phd.aithyra.at/> · phd@aithyra.at

**Why this one fits where the others don't.** Their admissions text says a
biological background is not required for AI applicants and a computational
background is not required for life-science applicants — and that they actively
value "interdisciplinary fields and non-traditional academic pathways." You are
not an edge case for them; you are the profile they describe. Medical Laboratory
Sciences into molecular biotechnology into applied ML is exactly the pathway.
Your thesis is representation learning on molecules, which is on their list of
methods alongside geometric deep learning and generative AI.

- **Fully funded, four years.** EUR 2,832.10 gross monthly, paid 14×/year, plus
  full insurance, research costs and travel.
- **All nationalities.** No mobility rule, no fee-status trap.
- Master's needed by **September 2027** — you will have had it eleven months.
- Degree awarded by TU Wien, MedUni Vienna, or Univ. Vienna depending on project.

**Timeline:** applications close 1 Nov 2026 · online panel interviews 30 Nov–1
Dec · onsite visit 27–29 Jan 2027 · **programme starts 1 Sept 2027**.

**The catch, and it is the important part:** the 1 November deadline applies to
*referees as well as applicants*. Giorgetti and Filippo have to have submitted by
then. That converts "ask them sometime" into a task for this week — they need
notice, and Giorgetti is about to disappear into your defence.

The LinkedIn post you saw was from a specific group leader working on virus-host
conflict, and asked applicants to name their group. Identify who posted it before
you write, because that sentence is free marks and you cannot write it without
the name. Research groups: <https://phd.aithyra.at/research-groups/>

The September 2027 start is the one real drawback — it is eleven months after
you graduate. The poster mentioned flexibility for an earlier start, which is
worth asking about directly.

---

## The other two from Filippo

**Newcastle / Eli Lilly — ruled out, and not on ability.** The advert says it is
open only to candidates qualifying for **UK home fees**. That requires UK or
Irish nationality, or settled status plus ordinary residence. You would be
assessed as international, so you are ineligible regardless of merit. Separately,
it is high-throughput synthetic chemistry and direct-to-biology screening — bench
chemistry, which is the same reason HARPNET DC12 was ruled out.

**Gatsby Unit, UCL — a long shot, and expensive to attempt.** Funding is open to
all nationalities, which is good. But they ask for "a relevant first degree, for
example in Mathematics, Statistics, Computer Science, Engineering, Physics,
Neuroscience or Cognitive Psychology" — neither of your degrees is on that list.
Gatsby is a theory unit: the work is measure-theoretic probability, variational
inference, theoretical neuroscience. Your ML is applied and well done, but it is
gradient-boosted trees and SHAP, not the mathematical foundations they select on.
Not impossible, but it would cost you a week you do not have, at long odds,
during the same window as AITHYRA, which you are genuinely competitive for.

---

## 30 September, 23:59 — the thesis upload

This was on none of our earlier lists. Three conditions, verbatim from the
Scadenziario: **PDF/A**, **signed by the student on the frontespizio**, and
**"the thesis must not contain University of Verona's logo."**

Where the current build stands:

- ✅ **No logo.** `main.tex` line 51 already omits it. Compliant.
- ❌ **Not PDF/A.** The current `main.pdf` has no `pdfaid` marker and no
  OutputIntent — it is ordinary pdfTeX output. A file that is not PDF/A can be
  rejected at upload.
- ❌ **No signature on the title page.** The signature line sits on the
  *Declaration* page, not the frontespizio, which is what the rule names.

Both are fixable in the preamble (`pdfx` is available on Overleaf, which keeps
the internal links) or, as a fallback, by a Ghostscript conversion — tested, it
produces a valid PDF/A-2b at 91 pages but strips the hyperlinks.

Note the ordering problem: Filippo asked that nothing go to the portal until the
professor approves both documents, and the professor has not yet fixed the
defence date. The approval has to happen inside the next twelve days.

---

## Domanda di laurea — probably fine, worth thirty seconds

The window was **13 July – 27 August 2026** and it is shut: *"Applications will
not be accepted after August 27th."* You were emailed the thesis summary deadline
off this same table and met it on 14 September, so you are evidently registered
for the October session.

The part that can be silently incomplete is the money: *"the application is
considered completed with the payment of the stamp duty (ESSE3)"* — the €16
virtual marca da bollo. An unpaid bollo means an unperfected domanda. Log into
ESSE3 and confirm the domanda shows as paid.

Also required, no later than ~6 October: **all** exams, stage, tirocini (status
"VIS") and language certifications registered in your carriera. Only the final
exam is exempt. Your English C1 certification counts here.

Office: carriere.scienze@ateneo.univr.it, +39 045 8027011, Mon/Wed 10:00–14:00,
Fri 10:00–13:00.

---

## DECODES — new, and worth prioritising

MSCA Doctoral Network, *Deciphering the Splicing Code in Human Disease*.
Coordinated by University of Santiago de Compostela. 15 funded posts.
Grant agreement 101312753.

**Why it matters more than it looks:** the eligibility text says only that you must
not hold a doctorate *at the time of recruitment*, and start is "during 2027".
There is no Master's-in-hand-at-deadline clause, which is the thing that may
disqualify you from POLARIS. Your MSc in Biotechnology is explicitly on their
accepted list. English B2 required, you have certified C1.

**Money:** €4,010/month living + €710 mobility. Materially above the Helsinki post.

**Mechanics:** one email, one PDF, **1 to 3 positions ranked by preference**.
Send to mscadn.decodes@usc.gal with subject
`DECODES_<DC numbers in order>_FikaduDagmawi` (e.g. `DECODES_15,1,2_FikaduDagmawi`).
Needs CV, motivation letter, **BSc and MSc transcripts**, proof of English.

**The three that fit you:**

- **DC15 — Santiago de Compostela.** Pharmacological targeting of splicing in
  malignant peripheral nerve sheath tumours: *discovery and evaluation of small
  molecules*. This is compound discovery. Closest to what you have actually done.
- **DC1 — Southampton.** Multi-omics for rare disease diagnosis, integrating
  long-read DNA-seq, RNA-seq and methylation with AI/ML. Your WES workflow and
  Python are the relevant assets.
- **DC2 — Basel.** Computational discovery of disease-related RNA isoforms from
  large transcriptomic datasets. Method development, which is your thesis in a
  different domain.

Timeline: interviews 10–31 Oct, notification 15 Nov, start during 2027.

---

## Today

**1. Send the eligibility email to Dr Jana Selent** (jana.selent@upf.edu).
POLARIS requires the Master's *at the deadline*; you graduate 11 days late. This
decides whether the POLARIS application happens at all. Everything else about
POLARIS is wasted effort until she answers.

**2. Find the HARPNET deadline.** It is not on the DC8 or DC11 project pages.
Check harpnet.eu/recruitment or the application portal. POLARIS's 5 October does
not necessarily apply, and HARPNET is the application you are *definitely*
eligible for — so if its deadline is sooner, it jumps the queue.

**3. Check the domanda di conseguimento titolo** is actually submitted. Recorded
as outstanding, independent of everyone else, and no one will chase you for it.

---

## Applications

### HARPNET — eligibility clean ("MSc by October 2026" covers you)

- [ ] Confirm deadline
- [ ] Decide the third project, or submit with two. **DC12 is ruled out** —
      it requires practical synthetic chemistry. DC14 and DC7 are the only
      remaining plausible options; read them before deciding, and two well-fitting
      choices beat three with a bad one.
- [ ] Compile CV with `\HARPNETtrue`
- [ ] Compile `letter_harpnet_dc8.tex`
- [ ] Check whether your thesis satisfies "completed a research internship with
      relevant expertise" — you have a 50-hour placement on the CV, which should
      cover it, but they may mean something separate

### POLARIS — blocked on eligibility

- [ ] Selent's answer
- [ ] Compile CV with `\HARPNETfalse`
- [ ] Compile `letter_polaris_dc6.tex`
- [ ] **Delete `letter_polaris_dc5.tex`** — superseded, and the only remaining
      file with em-dashes in it

### Both

- [ ] Compile everything on Overleaf and check page counts: CV must stay at 2
      pages (the coursework block is the risk), letters at 1 page each
- [ ] Ask the segreteria how long `@studenti.univr.it` stays live after
      graduation. Interviews run into 2027; if it expires mid-process you miss
      the invitation
- [ ] Tell Filippo you switched POLARIS from DC5 to DC6, and why. He pointed you
      at DC5 and may know something about the groups

---

## Thesis and defence

- [ ] Open the deck in PowerPoint, click through all 32 slides. The figures are
      inserted images and cannot be verified from here
- [ ] Delete `GPCR_ML_defense [Autosaved].pptx`
- [ ] Rehearse against `DEFENSE_PREP.md`, timed. Target 20–22 min
- [ ] Deck needs one rebuild to pick up two corrected speaker notes (stale
      confusion matrix on slide 27, old representation MCCs on slide 30).
      Source is fixed; needs my shell, which is down. **Until then use
      DEFENSE_PREP.md, not the speaker notes**
- [ ] Optional citations: Matthews 1975 / Chicco & Jurman 2020 for MCC;
      Lundberg 2020 for TreeSHAP (currently cites the 2017 general paper);
      Truchon & Bayly 2007 for enrichment factor

---

## Blocked, nothing to do

- Mock presentation — waiting on the professor
- Defence date — waiting on the professor
- Portal upload — only after he approves both documents

---

## Done since the last list

- ✅ Thesis summary submitted before the deadline
- ✅ CV: R² corrected 0.60/0.66 → 0.562/0.644; 46 → 47 targets; thesis title
      matched to the real one; student email; coursework and English C1 added
- ✅ CV made monochrome, inline bold cut from nine to two, em-dashes removed
- ✅ One CV source with a `\HARPNETtrue/false` switch, so corrections can't drift
      between the two versions
- ✅ POLARIS letter rebuilt for DC6 (Selent/Estévez) after reading the real advert
- ✅ HARPNET DC8 letter written (Martine Smit, not Leurs)
- ✅ Eligibility problem found and stated openly in both letters
