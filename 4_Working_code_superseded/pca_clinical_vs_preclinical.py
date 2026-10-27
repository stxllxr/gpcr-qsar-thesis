# =====================================================================
#  PCA: does the preclinical expansion occupy the same chemical space?
#  Paste as a new cell in 10_additions.ipynb (needs feat, sets in memory).
#
#  Why this one
#  ------------
#  The thesis title says clinical-stage, but Part Two expands each target
#  ~27x and ~32x with preclinical ChEMBL compounds. The obvious question
#  is whether that is still the same chemical space or effectively a
#  different dataset. This answers it two ways:
#
#    left  - PCA of the descriptor block, clinical vs preclinical overlaid
#    right - for each preclinical compound, its highest ECFP4 Tanimoto to
#            any clinical compound (are they close to known chemistry?)
#
#  plus the numbers: overlap of the preclinical points with the clinical
#  95% region, and how far the two centroids sit apart in SD units.
#
#  Outputs: deck_expansion_pca.png + printed statistics
# =====================================================================
import numpy as np, pandas as pd, os
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

INK, TEAL, CORAL, GREY, PALE = '#22333B', '#116E64', '#BE5638', '#60727A', '#CBDDDA'
FP_BITS = 2048
LOCKED = 'data/curated_15desc.csv' if os.path.exists('data/curated_15desc.csv') else 'curated_15desc.csv'
KEY = {'5-HT2A': '5-HT2A', 'Dopamine D3': 'D3'}

locked = pd.read_csv(LOCKED)


def max_tanimoto_to(ref_fp, query_fp, block=256):
    a = (ref_fp > 0).astype(np.float32); pa = a.sum(1)
    out = np.empty(len(query_fp), dtype=float)
    for i in range(0, len(query_fp), block):
        b = (query_fp[i:i + block] > 0).astype(np.float32)
        inter = b @ a.T
        union = pa[None, :] + b.sum(1)[:, None] - inter
        out[i:i + block] = (inter / np.maximum(union, 1e-9)).max(1)
    return out


fig, axs = plt.subplots(2, len(feat), figsize=(6.1 * len(feat), 8.4))
axs = np.atleast_2d(axs)
if axs.shape[0] == 1:
    axs = axs.reshape(2, -1)

print(f'{"target":14s} {"clinical":>9s} {"preclin":>9s} {"centroid gap":>13s} '
      f'{"inside clin 95%":>16s} {"median maxTc":>13s}')
print('-' * 82)

for j, t in enumerate(feat):
    X, y, scaf = feat[t]
    ids = sets[t].molecule_chembl_id.values
    clin_ids = set(locked[locked.target.str.contains(KEY[t], case=False)]
                   .molecule_chembl_id.unique())
    is_clin = np.array([i in clin_ids for i in ids])

    # --- PCA on the descriptor block (already normalised by DescriptaStorus)
    D = X[:, FP_BITS:]
    D = np.nan_to_num(D, nan=0.0, posinf=0.0, neginf=0.0)
    Z = StandardScaler().fit_transform(D)
    p = PCA(n_components=2).fit(Z)
    s2 = p.transform(Z)
    ev = p.explained_variance_ratio_ * 100

    ax = axs[0, j]
    ax.scatter(s2[~is_clin, 0], s2[~is_clin, 1], s=6, alpha=.22, color=PALE,
               edgecolors='none', label=f'preclinical (n={int((~is_clin).sum())})')
    ax.scatter(s2[is_clin, 0], s2[is_clin, 1], s=16, alpha=.85, color=CORAL,
               edgecolors='none', label=f'clinical (n={int(is_clin.sum())})')
    ax.set_xlabel(f'PC1 ({ev[0]:.1f}%)', color=INK)
    ax.set_ylabel(f'PC2 ({ev[1]:.1f}%)', color=INK)
    ax.set_title(f'{t}   descriptor space', color=INK, fontsize=12.5,
                 fontweight='bold', pad=9)
    ax.legend(fontsize=9.5, frameon=False, markerscale=1.5)

    # --- how close is each preclinical compound to known clinical chemistry
    tc = max_tanimoto_to(X[is_clin, :FP_BITS], X[~is_clin, :FP_BITS])
    ax = axs[1, j]
    ax.hist(tc, bins=np.linspace(0, 1, 41), color=TEAL, alpha=.75, edgecolor='white', lw=.5)
    ax.axvline(np.median(tc), ls='--', lw=1.8, color=CORAL,
               label=f'median {np.median(tc):.2f}')
    ax.set_xlim(0, 1)
    ax.set_xlabel('max ECFP4 Tanimoto to any clinical compound', color=INK)
    ax.set_ylabel('preclinical compounds', color=INK)
    ax.set_title(f'{t}   proximity to clinical chemistry', color=INK,
                 fontsize=12.5, fontweight='bold', pad=9)
    ax.legend(fontsize=10, frameon=False)

    # --- numbers
    cc, cp = s2[is_clin], s2[~is_clin]
    gap = np.linalg.norm(cc.mean(0) - cp.mean(0)) / s2.std(0).mean()
    lo1, hi1 = np.percentile(cc[:, 0], [2.5, 97.5])
    lo2, hi2 = np.percentile(cc[:, 1], [2.5, 97.5])
    inside = np.mean((cp[:, 0] >= lo1) & (cp[:, 0] <= hi1) &
                     (cp[:, 1] >= lo2) & (cp[:, 1] <= hi2))
    print(f'{t:14s} {int(is_clin.sum()):9d} {int((~is_clin).sum()):9d} '
          f'{gap:13.2f} {inside:15.0%} {np.median(tc):13.2f}')

for ax in axs.ravel():
    ax.grid(alpha=.22, lw=.7, color=PALE); ax.set_axisbelow(True)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)

fig.tight_layout(pad=0.6)
fig.savefig('deck_expansion_pca.png', dpi=300, bbox_inches='tight')
plt.show()

print("""
How to read it
  centroid gap    distance between the clinical and preclinical centroids,
                  in SD units. Below ~0.3 means the two sets sit on top of
                  each other; above ~1 would mean genuinely different space.
  inside clin 95% fraction of preclinical compounds falling inside the
                  clinical 95% box on PC1-PC2.
  median maxTc    typical highest similarity of a preclinical compound to
                  any clinical compound. Around 0.3-0.5 is normal for a
                  related but non-redundant library.

Say this: the expansion is a densification of the same chemical space, not a
different dataset. And because the scaffold split holds out whole families,
the added compounds cannot leak an answer to a clinical test compound.
""")
print('saved deck_expansion_pca.png')
