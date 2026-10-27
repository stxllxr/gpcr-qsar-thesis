# =====================================================================
#  ADDITIONS to 08_full_model.ipynb  --  all ADDITIVE, nothing removed.
#  Paste each block below as a NEW CELL at the bottom of the notebook,
#  AFTER you have run Cells 1-5 (imports, build, featurise, Cell A, Cell B),
#  so that  feat, sets, scaffold_split, boost, rf  already exist in memory.
#
#  Adds:  CatBoost (reg + clf) | pKi & prediction distributions |
#         classification at 100 nM / 1 uM (ROC-AUC, PR-AUC) |
#         enrichment factor (virtual-screening prioritisation) |
#         SHAP feature importance | without-promiscuous ablation.
#
#  Thresholds (pKi = 9 - log10(Ki[nM])):  100 nM -> pKi 7.0 ; 1 uM -> pKi 6.0.
#  100 nM gives a near-balanced active/inactive split and is the primary task.
# =====================================================================


# ===================================================================== #
#  CELL 10  --  setup, extra models, and the pKi distribution figure
# ===================================================================== #
get_ipython().system('pip -q install catboost shap')   # safe if already installed

import numpy as np, matplotlib.pyplot as plt, matplotlib as mpl
import xgboost as xgb
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (r2_score, roc_auc_score, average_precision_score,
                             roc_curve)
from catboost import CatBoostRegressor, CatBoostClassifier
mpl.rcParams.update({"font.family": "serif", "font.size": 12,
                     "savefig.dpi": 300, "savefig.bbox": "tight"})

# --- model factories (same style/params as your XGB/RF) ---
def cbr():  return CatBoostRegressor(iterations=400, depth=6, learning_rate=0.05,
                                     random_seed=0, verbose=0)
def bclf(): return XGBClassifier(n_estimators=400, max_depth=4, learning_rate=0.05,
                                 subsample=0.8, colsample_bytree=0.6, random_state=0,
                                 n_jobs=-1, eval_metric='logloss')
def rclf(): return RandomForestClassifier(n_estimators=400, random_state=0, n_jobs=-1)
def cclf(): return CatBoostClassifier(iterations=400, depth=6, learning_rate=0.05,
                                      random_seed=0, verbose=0)
CLF   = {'XGBoost': bclf, 'RandomForest': rclf, 'CatBoost': cclf}
THRESH = {'100 nM': 7.0, '1 uM': 6.0}        # primary = 100 nM
NSEED = 12

# --- Figure: pKi distribution per target, with the two activity cut-offs ---
fig, axes = plt.subplots(1, len(feat), figsize=(5.4*len(feat), 4.2))
if len(feat) == 1: axes = [axes]
for ax, t in zip(axes, feat):
    y = feat[t][1]
    ax.hist(y, bins=30, color='#6699cc', edgecolor='k', alpha=0.85)
    for lab, thr in THRESH.items():
        ax.axvline(thr, ls='--', lw=1.6,
                   color='#c0392b' if lab == '100 nM' else '#e08e0b')
        ax.text(thr, ax.get_ylim()[1]*0.92, f' {lab}', rotation=90,
                va='top', ha='left', fontsize=9)
    ax.set_xlabel('pK$_i$'); ax.set_ylabel('compounds'); ax.set_title(t)
fig.tight_layout(); fig.savefig('pki_distribution.png'); plt.show()
print('saved pki_distribution.png  |  base active-rate @100nM:',
      {t: round(float((feat[t][1] >= 7.0).mean()), 2) for t in feat})


# ===================================================================== #
#  CELL 11  --  CatBoost regression, added to the scaffold-split comparison
#  (drop these numbers next to XGB/RF in Table 3.7)
# ===================================================================== #
print('Regression, scaffold split, mean R2 over %d seeds (CatBoost added):' % NSEED)
reg_rows = []
for t in feat:
    X, y, scaf = feat[t]
    rs = []
    for s in range(NSEED):
        tr, te = scaffold_split(scaf, len(y), s)
        if len(te) < 5 or len(np.unique(y[te])) < 2: continue
        rs.append(r2_score(y[te], cbr().fit(X[tr], y[tr]).predict(X[te])))
    rs = np.array(rs)
    reg_rows.append((t, rs.mean(), rs.std()))
    print(f'   {t:12s} CatBoost  R2 = {rs.mean():.3f} +/- {rs.std():.3f}')


# ===================================================================== #
#  CELL 12  --  classification (active/inactive) + enrichment factor
#  Reports ROC-AUC, PR-AUC and EF@1/5/10% for every model x threshold.
#  EF@k% = (active-rate in the top-k% ranked by model score) / (overall active-rate).
# ===================================================================== #
def enrichment(ybin, scores, frac):
    n = len(scores); k = max(1, int(round(frac*n)))
    idx = np.argsort(scores)[::-1][:k]; base = ybin.mean()
    return (ybin[idx].mean()/base) if base > 0 else np.nan

clf_rows = []
for lab, thr in THRESH.items():
    print(f'\n=== classification @ {lab} (active = pKi >= {thr}) ===')
    for t in feat:
        X, y, scaf = feat[t]; yb = (y >= thr).astype(int)
        for mn, mk in CLF.items():
            au, pr, e1, e5, e10 = [], [], [], [], []
            for s in range(NSEED):
                tr, te = scaffold_split(scaf, len(y), s)
                if len(np.unique(yb[tr])) < 2 or len(np.unique(yb[te])) < 2: continue
                p = mk().fit(X[tr], yb[tr]).predict_proba(X[te])[:, 1]
                au.append(roc_auc_score(yb[te], p))
                pr.append(average_precision_score(yb[te], p))
                e1.append(enrichment(yb[te], p, 0.01))
                e5.append(enrichment(yb[te], p, 0.05))
                e10.append(enrichment(yb[te], p, 0.10))
            clf_rows.append((lab, t, mn, np.mean(au), np.mean(pr),
                             np.nanmean(e1), np.nanmean(e5), np.nanmean(e10)))
            print(f'   {t:12s} {mn:12s} AUC={np.mean(au):.3f}  PR={np.mean(pr):.3f}  '
                  f'EF@1%={np.nanmean(e1):.2f}  EF@5%={np.nanmean(e5):.2f}  EF@10%={np.nanmean(e10):.2f}')

import pandas as pd
pd.DataFrame(clf_rows, columns=['threshold','target','model','ROC_AUC','PR_AUC',
             'EF@1%','EF@5%','EF@10%']).to_csv('classification_metrics.csv', index=False)
print('\nsaved classification_metrics.csv')


# ===================================================================== #
#  CELL 13  --  enrichment / ROC figure + predicted-value distribution
#  (XGBoost, 100 nM, single scaffold split seed 0)
# ===================================================================== #
fig, axs = plt.subplots(1, 3, figsize=(15, 4.4))
colors = {'5-HT2A': '#c0392b', 'Dopamine D3': '#2c7fb8'}
for t in feat:
    X, y, scaf = feat[t]; yb = (y >= 7.0).astype(int)
    tr, te = scaffold_split(scaf, len(y), 0)
    col = colors.get(t, None)
    # --- ROC ---
    p = bclf().fit(X[tr], yb[tr]).predict_proba(X[te])[:, 1]
    fpr, tpr, _ = roc_curve(yb[te], p)
    axs[0].plot(fpr, tpr, color=col, lw=2,
                label=f'{t} (AUC {roc_auc_score(yb[te], p):.2f})')
    # --- enrichment curve: actives recovered vs fraction screened ---
    order = np.argsort(p)[::-1]; rec = np.cumsum(yb[te][order]) / yb[te].sum()
    frac = np.arange(1, len(order)+1) / len(order)
    axs[1].plot(frac, rec, color=col, lw=2, label=t)
    # --- predicted-value distribution (regression) ---
    pr = boost().fit(X[tr], y[tr]).predict(X[te])
    axs[2].hist(pr, bins=25, histtype='step', lw=2, color=col, label=f'{t} predicted')
axs[0].plot([0, 1], [0, 1], 'k--', lw=1); axs[0].set_title('ROC (100 nM)')
axs[0].set_xlabel('false positive rate'); axs[0].set_ylabel('true positive rate'); axs[0].legend(fontsize=9)
axs[1].plot([0, 1], [0, 1], 'k--', lw=1); axs[1].set_title('Enrichment (actives recovered)')
axs[1].set_xlabel('fraction of library screened'); axs[1].set_ylabel('fraction of actives found'); axs[1].legend(fontsize=9)
axs[2].set_title('Predicted pK$_i$ distribution'); axs[2].set_xlabel('predicted pK$_i$'); axs[2].set_ylabel('compounds'); axs[2].legend(fontsize=9)
fig.tight_layout(); fig.savefig('enrichment_roc.png'); plt.show()
print('saved enrichment_roc.png')


# ===================================================================== #
#  CELL 14  --  SHAP feature importance (native XGBoost TreeSHAP)
#  Uses xgboost's exact pred_contribs (version-proof, no shap loader issues).
#  Highlights the interpretable named descriptors.
# ===================================================================== #
try:
    from descriptastorus.descriptors import rdNormalizedDescriptors
    dcols = [c[0] for c in rdNormalizedDescriptors.RDKit2DNormalized().columns]
except Exception:
    dcols = []

fig, axes = plt.subplots(1, len(feat), figsize=(6.2*len(feat), 5))
if len(feat) == 1: axes = [axes]
for ax, t in zip(axes, feat):
    X, y, scaf = feat[t]
    nd = X.shape[1] - 2048
    dd = list(dcols)
    if len(dd) == nd + 1: dd = dd[1:]
    if len(dd) != nd:     dd = [f'desc_{i}' for i in range(nd)]
    names = np.array([f'ECFP_{i}' for i in range(2048)] + dd)
    m = boost().fit(X, y)
    samp = X[np.random.RandomState(0).choice(len(X), min(1000, len(X)), replace=False)]
    contribs = m.get_booster().predict(xgb.DMatrix(samp), pred_contribs=True)
    mabs = np.abs(contribs[:, :-1]).mean(0)          # drop bias column
    desc_idx = np.arange(2048, 2048 + nd)
    top = desc_idx[np.argsort(mabs[desc_idx])[::-1]][:15][::-1]
    ax.barh(range(len(top)), mabs[top], color='#3b7dd8')
    ax.set_yticks(range(len(top))); ax.set_yticklabels(names[top], fontsize=9)
    ax.set_xlabel('mean |SHAP|'); ax.set_title(f'{t}: top descriptors')
fig.tight_layout(); fig.savefig('shap_descriptors.png'); plt.show()
print('saved shap_descriptors.png')


# ===================================================================== #
#  CELL 15  --  ablation: retrain WITHOUT promiscuous compounds
#  Promiscuous = molecules engaging >= PROM_CUT distinct targets in the
#  curated all-target set (curated_15desc.csv). Tests whether performance
#  leans on a few multi-target drugs.  Robustness check; expect a small drop.
# ===================================================================== #
from rdkit import Chem
PROM_CUT = 5
_locked = pd.read_csv(LOCKED)
_tc = _locked.groupby('molecule_chembl_id').target.nunique()
promis = set(_tc[_tc >= PROM_CUT].index)
print(f'promiscuous set: {len(promis)} molecules with >= {PROM_CUT} distinct targets\n')
print('Regression R2 (mean over %d seeds): full vs without-promiscuous' % NSEED)
for t in feat:
    X, y, scaf = feat[t]
    vm = np.array([Chem.MolFromSmiles(str(s)) is not None for s in sets[t].parent_smiles])
    ids = sets[t].molecule_chembl_id.values[vm]
    assert len(ids) == len(y), 'row alignment mismatch -- re-run featurise cell first'
    keep = ~np.isin(ids, list(promis)); nrem = int((~keep).sum())
    def _mean_r2(Xx, yy, ss):
        rs = []
        for s in range(NSEED):
            tr, te = scaffold_split(ss, len(yy), s)
            if len(te) < 5 or len(np.unique(yy[te])) < 2: continue
            rs.append(r2_score(yy[te], boost().fit(Xx[tr], yy[tr]).predict(Xx[te])))
        return float(np.mean(rs))
    full = _mean_r2(X, y, scaf)
    abl  = _mean_r2(X[keep], y[keep], scaf[keep])
    print(f'   {t:12s} removed {nrem:3d}/{len(y)}   full={full:.3f}   without-promiscuous={abl:.3f}   d={abl-full:+.3f}')

print('\nALL ADDITION CELLS COMPLETE.')
print('Figures: pki_distribution.png, enrichment_roc.png, shap_descriptors.png')
print('Table:   classification_metrics.csv  (upload any of these to me for the thesis)')
