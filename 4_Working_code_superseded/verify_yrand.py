#!/usr/bin/env python3
"""Job C: y-randomisation of MCC, 100 permutations, scaffold split seed 0."""
import os, sys, json, time, numpy as np
from sklearn.metrics import matthews_corrcoef
from cluster_lib import load, scaffold_groups, group_split, clf, OUT, THRESH

LOG = OUT + 'verify_yrand.jsonl'
done = set()
if os.path.exists(LOG):
    for l in open(LOG):
        r = json.loads(l); done.add((r['target'], r['perm']))

BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 95.0
t0 = time.time()
for t in ['5-HT2A', 'Dopamine_D3']:
    X, y, scaf = load(t)
    yb = (y >= THRESH).astype(int)
    tr, te = group_split(scaffold_groups(scaf), len(y), 0)
    for perm in range(-1, 100):          # -1 = the true, unpermuted fit
        if (t, perm) in done: continue
        if time.time() - t0 > BUDGET: print('PAUSE', flush=True); sys.exit(0)
        ytr = yb[tr] if perm < 0 else np.random.RandomState(perm).permutation(yb[tr])
        m = clf().fit(X[tr], ytr).predict(X[te])
        rec = dict(target=t, perm=perm, mcc=float(matthews_corrcoef(yb[te], m)))
        with open(LOG, 'a') as f: f.write(json.dumps(rec) + '\n')
print('ALL DONE job C')
