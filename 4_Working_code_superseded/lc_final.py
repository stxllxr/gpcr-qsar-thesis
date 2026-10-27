#!/usr/bin/env python3
"""Definitive learning curve: final feature matrices, 5 seeds per size.

Fixes the defect in 06_expanded_models cell 17, which plotted the REQUESTED
subsample size rather than the actual one and put the last two points ~190
apart so their labels collided.  Here the x value recorded is the actual
number of training rows used, and each point is a mean over 5 scaffold splits.

Resumable: one JSON line per (target, size, seed) to lc_final.jsonl
"""
import os, sys, json, time, numpy as np
from sklearn.metrics import r2_score
from xgboost import XGBRegressor
from cluster_lib import load, scaffold_groups, group_split, OUT

SIZES = [200, 500, 1000, 2000, 3500, None]      # None = the full training pool
NSEED = 5
LOG = OUT + 'lc_final.jsonl'
done = set()
if os.path.exists(LOG):
    for l in open(LOG):
        r = json.loads(l); done.add((r['target'], r['size'], r['seed']))

def reg():
    return XGBRegressor(n_estimators=400, max_depth=4, learning_rate=0.05,
                        subsample=0.8, colsample_bytree=0.6, random_state=0, n_jobs=-1)

BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 95.0
t0 = time.time()
for t in ['5-HT2A', 'Dopamine_D3']:
    X, y, scaf = load(t)
    groups = scaffold_groups(scaf); n = len(y)
    for k in SIZES:
        key_size = k if k else -1
        for s in range(NSEED):
            if (t, key_size, s) in done: continue
            if time.time() - t0 > BUDGET: print('PAUSE', flush=True); sys.exit(0)
            tr, te = group_split(groups, n, s)
            if k and k < len(tr):
                trk = np.random.RandomState(s).choice(tr, k, replace=False)
            else:
                trk = np.asarray(tr)
            m = reg().fit(X[trk], y[trk])
            rec = dict(target=t, size=key_size, seed=s,
                       n_train=int(len(trk)),          # the ACTUAL size, not the request
                       r2=float(r2_score(y[te], m.predict(X[te]))))
            with open(LOG, 'a') as f: f.write(json.dumps(rec) + '\n')
print('ALL DONE')
