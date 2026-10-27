#!/usr/bin/env python3
"""Re-run the three classification controls quoted on deck slide 30, because
none of them could be traced to a saved file.

  A. representation ablation  (ECFP4 / descriptors / fused, MCC, 12 seeds)
  B. read-across MCC on the scaffold split (1-NN Tanimoto, 12 seeds)
  C. y-randomisation of MCC (100 permutations, scaffold seed 0)

Resumable: appends one JSON line per unit of work to verify_ctrl.jsonl.
"""
import os, sys, json, time, numpy as np
from sklearn.metrics import matthews_corrcoef
from cluster_lib import load, bitvects, scaffold_groups, group_split, clf, read_across, OUT, THRESH

LOG = OUT + 'verify_ctrl.jsonl'
done = set()
if os.path.exists(LOG):
    for l in open(LOG):
        r = json.loads(l); done.add((r['job'], r['target'], r['seed'], r.get('rep', '')))

BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 150.0
t0 = time.time()

def emit(**kw):
    with open(LOG, 'a') as f: f.write(json.dumps(kw) + '\n')
    print(kw, flush=True)

SL = {'ecfp': slice(0, 2048), 'desc': slice(2048, None), 'fused': slice(0, None)}

for t in ['5-HT2A', 'Dopamine_D3']:
    X, y, scaf = load(t)
    yb = (y >= THRESH).astype(int)
    groups = scaffold_groups(scaf)
    n = len(y)
    bvs = None
    for seed in range(12):
        for rep in ['ecfp', 'desc', 'fused']:
            key = ('A', t, seed, rep)
            if key in done: continue
            if time.time() - t0 > BUDGET: print('PAUSE'); sys.exit(0)
            tr, te = group_split(groups, n, seed)
            m = clf().fit(X[tr][:, SL[rep]], yb[tr]).predict(X[te][:, SL[rep]])
            emit(job='A', target=t, seed=seed, rep=rep,
                 mcc=float(matthews_corrcoef(yb[te], m)))
        key = ('B', t, seed, '')
        if key not in done:
            if time.time() - t0 > BUDGET: print('PAUSE'); sys.exit(0)
            if bvs is None: bvs = bitvects(X[:, :2048])
            tr, te = group_split(groups, n, seed)
            pred = read_across(bvs, tr, te, yb)
            emit(job='B', target=t, seed=seed, rep='',
                 mcc=float(matthews_corrcoef(yb[te], pred)))
print('ALL DONE for jobs A and B')
