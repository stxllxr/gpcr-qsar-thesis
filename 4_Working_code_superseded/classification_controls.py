# =====================================================================
#  CLASSIFICATION CONTROLS -- the three analyses the regression models
#  already have, run for the 100 nM classifier so the two halves match.
#
#  Paste as a new cell in 10_additions.ipynb where feat, scaffold_split
#  and bclf() are in memory. Run AFTER scaffold_predictions_classification.py.
#
#  Mirrors Cell B of 08_full_model.ipynb:
#     1. representation ablation   ECFP4 vs descriptors vs fused
#     2. y-randomisation           100 label permutations
#     3. read-across baseline      1-NN Tanimoto, majority label copied
#
#  RUNTIME WARNING: step 2 fits 100 classifiers per target. If that is
#  too slow before the deadline, set NPERM = 30. The p-value floor
#  becomes 1/(NPERM+1) instead of 0.0099, which is still conclusive.
# =====================================================================
import numpy as np, time, sys
from sklearn.metrics import matthews_corrcoef

# FAST = True  -> ~4x quicker, still conclusive. Use it if Friday is close.
FAST = False
NSEED, NPERM = (6, 30) if FAST else (12, 100)
THRESH, SPLIT_SEED, FP_BITS = 7.0, 0, 2048

_t0 = time.time()
def tick(msg):
    print(f'   [{time.time()-_t0:6.0f}s] {msg}', flush=True)

print('CLASSIFICATION CONTROLS at %.0f pKi (100 nM), scaffold split' % THRESH)
print(f'FAST={FAST}  NSEED={NSEED}  NPERM={NPERM}   '
      f'(~{NSEED*3*2 + NPERM*2 + NSEED*2} model fits)\n', flush=True)

# ============================================ 1. REPRESENTATION ABLATION
print('1) REPRESENTATION  (MCC, mean over %d scaffold splits)' % NSEED)
for t in feat:
    X, y, scaf = feat[t]
    yb = (y >= THRESH).astype(int)
    views = {'ECFP4': X[:, :FP_BITS],
             'DescriptaStorus': X[:, FP_BITS:],
             'Fused': X}
    for vname, Xv in views.items():
        ms = []
        for s in range(NSEED):
            tr, te = scaffold_split(scaf, len(y), s)
            p = bclf().fit(Xv[tr], yb[tr]).predict(Xv[te])
            ms.append(matthews_corrcoef(yb[te], p))
        tick(f'{t:14s} {vname:16s} {np.mean(ms):.3f} +/- {np.std(ms):.3f}')

# =============================================== 2. Y-RANDOMISATION
print('\n2) Y-RANDOMISATION  (%d label permutations, scaffold split seed %d)'
      % (NPERM, SPLIT_SEED))
for t in feat:
    X, y, scaf = feat[t]
    yb = (y >= THRESH).astype(int)
    tr, te = scaffold_split(scaf, len(y), SPLIT_SEED)
    true = matthews_corrcoef(yb[te], bclf().fit(X[tr], yb[tr]).predict(X[te]))
    rng = np.random.RandomState(0)
    null = []
    for k in range(NPERM):
        null.append(matthews_corrcoef(
            yb[te], bclf().fit(X[tr], rng.permutation(yb[tr])).predict(X[te])))
        if (k + 1) % 10 == 0:
            tick(f'{t:14s} permutation {k+1}/{NPERM}')
    null = np.asarray(null)
    p = (1 + (null >= true).sum()) / (NPERM + 1)
    print(f'   {t:14s} true MCC={true:.3f}  null_mean={null.mean():+.3f}  '
          f'null_max={null.max():+.3f}  p={p:.4f}')

# ================================================= 3. READ-ACROSS BASELINE
print('\n3) READ-ACROSS  (1-NN Tanimoto on ECFP4, label copied, mean over %d)'
      % NSEED)


def tanimoto_1nn_labels(Xtr_fp, ytr, Xte_fp, block=256):
    """Label of the single most Tanimoto-similar training compound."""
    a = (Xtr_fp > 0).astype(np.float32)
    pop_a = a.sum(1)
    out = np.empty(len(Xte_fp), dtype=int)
    for i in range(0, len(Xte_fp), block):
        b = (Xte_fp[i:i + block] > 0).astype(np.float32)
        inter = b @ a.T
        union = pop_a[None, :] + b.sum(1)[:, None] - inter
        out[i:i + block] = ytr[np.argmax(inter / np.maximum(union, 1e-9), axis=1)]
    return out


for t in feat:
    X, y, scaf = feat[t]
    yb = (y >= THRESH).astype(int)
    ms = []
    for s in range(NSEED):
        tr, te = scaffold_split(scaf, len(y), s)
        pred = tanimoto_1nn_labels(X[tr, :FP_BITS], yb[tr], X[te, :FP_BITS])
        ms.append(matthews_corrcoef(yb[te], pred))
    tick(f'{t:14s} read-across MCC = {np.mean(ms):.3f} +/- {np.std(ms):.3f}')

print(f'\nTotal runtime {time.time()-_t0:.0f}s')
print('DONE. These three now match what the regression models already report:')
print('  representation ablation, y-randomisation, and the 1-NN read-across')
print('  baseline. Send the whole block back and the deck and thesis get')
print('  updated to state both halves rather than regression only.')
