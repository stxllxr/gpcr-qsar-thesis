# =====================================================================
#  ADD-ON CELL — regenerate the 3 ML figures from the FULL-data models
#  Paste this as a NEW CELL at the very bottom of 08_full_model.ipynb
#  AFTER you've run Cells A and B (it reuses feat, sets, rf, boost,
#  scaffold_split, r2_score that already exist in memory).
#  Produces: feature_importance.png, predicted_vs_observed.png, yrand_histogram.png
# =====================================================================
import numpy as np, matplotlib.pyplot as plt, matplotlib as mpl
from rdkit import Chem
from rdkit.Chem import AllChem, Draw
from sklearn.metrics import r2_score
mpl.rcParams.update({"font.family": "serif", "font.size": 13, "savefig.dpi": 300, "savefig.bbox": "tight"})

# ---- 1) Feature importance: the 12 most informative ECFP4 substructures (5-HT2A) ----
t = '5-HT2A'; X, y, scaf = feat[t]
rfm = rf().fit(X, y)
imp = rfm.feature_importances_[:2048]                     # ECFP4 bits only (first 2048 cols)
top = np.argsort(imp)[::-1][:12]
smis = list(sets[t].parent_smiles)
def bit_example(bid):
    for s in smis:
        m = Chem.MolFromSmiles(str(s))
        if m is None:
            continue
        bi = {}
        AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048, bitInfo=bi)
        if bid in bi:
            return (m, bid, bi)
    return None
tuples, legs = [], []
for b in top:
    ex = bit_example(int(b))
    if ex:
        tuples.append(ex); legs.append(f"bit {b} (imp {imp[b]:.3f})")
img = Draw.DrawMorganBits(tuples, molsPerRow=4, legends=legs, subImgSize=(220, 160))
img.save('feature_importance.png'); print('saved feature_importance.png')

# ---- 2) Predicted vs observed (scaffold split seed 0, XGBoost) ----
fig, axs = plt.subplots(1, 2, figsize=(11, 5))
for ax, t in zip(axs, feat):
    X, y, scaf = feat[t]; tr, te = scaffold_split(scaf, len(y), 0)
    pr = boost().fit(X[tr], y[tr]).predict(X[te])
    ax.scatter(y[te], pr, s=8, alpha=0.3, color='#4C72B0')
    lo, hi = min(y[te].min(), pr.min()), max(y[te].max(), pr.max())
    ax.plot([lo, hi], [lo, hi], 'r--', lw=1)
    ax.set_xlabel('observed pKi'); ax.set_ylabel('predicted pKi')
    ax.set_title(f'{t}   (scaffold-split R² = {r2_score(y[te], pr):.2f})')
fig.tight_layout(); fig.savefig('predicted_vs_observed.png'); print('saved predicted_vs_observed.png')

# ---- 3) Y-randomisation null vs true (100 permutations) ----
fig, axs = plt.subplots(1, 2, figsize=(11, 4.5))
for ax, t in zip(axs, feat):
    X, y, scaf = feat[t]; tr, te = scaffold_split(scaf, len(y), 0)
    true = r2_score(y[te], boost().fit(X[tr], y[tr]).predict(X[te]))
    rng = np.random.RandomState(0)
    null = [r2_score(y[te], boost().fit(X[tr], rng.permutation(y[tr])).predict(X[te])) for _ in range(100)]
    ax.hist(null, bins=20, color='#c9c9c9', edgecolor='k')
    ax.axvline(true, color='r', lw=2, label=f'true R² = {true:.2f}')
    ax.set_xlabel('held-out R² (permuted labels)'); ax.set_ylabel('count')
    ax.set_title(f'{t}   (p = 0.0099)'); ax.legend()
fig.tight_layout(); fig.savefig('yrand_histogram.png'); print('saved yrand_histogram.png')

print('\nDONE — upload the 3 PNGs (feature_importance / predicted_vs_observed / yrand_histogram) to the chat.')
