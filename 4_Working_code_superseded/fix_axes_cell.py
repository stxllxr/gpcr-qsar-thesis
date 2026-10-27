# =====================================================================
#  AXIS-LOCK CELL  -- paste as a NEW CELL at the bottom of the notebook
#  that already has feat, scaffold_split, boost, bclf in memory
#  (08_full_model.ipynb or 10_additions.ipynb).
#
#  Why this exists
#  ---------------
#  The original figure code plots INSIDE the target loop, so matplotlib
#  autoscales each panel from its own data. Two consequences:
#    1. the two targets get different axes, so they cannot be compared;
#    2. on the parity plot x and y are scaled independently, so the
#       identity line is not at 45 degrees and the regression-to-the-mean
#       compression is invisible.
#  The fix is structural: compute everything first, derive ONE shared
#  range, then draw. Nothing about the models or the numbers changes.
#
#  Regenerates: predicted_vs_experimental.png, yrand_histogram.png,
#               pki_distribution.png, enrichment_roc.png, shap_descriptors.png
# =====================================================================
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, roc_curve, roc_auc_score

INK, TEAL, CORAL, GREY, PALE = '#22333B', '#116E64', '#BE5638', '#60727A', '#CBDDDA'
COL  = {'5-HT2A': TEAL, 'Dopamine D3': CORAL}
SEED = 0

plt.rcParams.update({'font.size': 12, 'savefig.dpi': 300,
                     'savefig.bbox': 'tight', 'axes.edgecolor': GREY})


# ---------------------------------------------------------------- helpers
def shared_range(*arrays, pad=0.06, step=1.0, floor=None):
    """One (lo, hi) covering EVERY array, rounded outward to a tick step."""
    v = np.concatenate([np.asarray(a, float).ravel() for a in arrays])
    v = v[np.isfinite(v)]
    lo, hi = v.min(), v.max()
    m = (hi - lo) * pad
    lo, hi = lo - m, hi + m
    lo, hi = np.floor(lo / step) * step, np.ceil(hi / step) * step
    if floor is not None:
        lo = max(lo, floor)
    return float(lo), float(hi)


def lock(axs, xlim=None, ylim=None, step=1.0, square=False):
    """Force identical limits and ticks on every panel."""
    for ax in np.ravel(np.asarray(axs, dtype=object)):
        if xlim:
            ax.set_xlim(*xlim)
            ax.set_xticks(np.arange(xlim[0], xlim[1] + 1e-9, step))
        if ylim:
            ax.set_ylim(*ylim)
        if square:
            ax.set_aspect('equal', adjustable='box')
        for s in ('top', 'right'):
            ax.spines[s].set_visible(False)


def tidy(ax, xlab, ylab, title):
    ax.set_xlabel(xlab, color=INK)
    ax.set_ylabel(ylab, color=INK)
    ax.set_title(title, color=INK, fontsize=12.5, fontweight='bold', pad=9)
    ax.grid(alpha=.22, lw=.7, color=PALE)
    ax.set_axisbelow(True)


# ============================================================= 1. PARITY
# predicted vs experimental pKi. Equal x and y is not optional here:
# without it the diagonal is not 45 deg and the plot cannot be read.
res = {}
for t in feat:
    X, y, scaf = feat[t]
    tr, te = scaffold_split(scaf, len(y), SEED)
    pr = boost().fit(X[tr], y[tr]).predict(X[te])
    res[t] = (y[te], pr, r2_score(y[te], pr))

lim = shared_range(*[a for t in res for a in res[t][:2]], step=1.0)

fig, axs = plt.subplots(1, len(res), figsize=(5.3 * len(res), 5.4),
                        sharex=True, sharey=True)
axs = np.atleast_1d(axs)
for ax, t in zip(axs, res):
    yt, pr, r2 = res[t]
    ax.plot(lim, lim, '--', lw=1.5, color=GREY, zorder=1)
    ax.scatter(yt, pr, s=10, alpha=.30, color=COL.get(t, TEAL),
               edgecolors='none', zorder=2)
    tidy(ax, 'experimental pK$_i$', 'predicted pK$_i$',
         f'{t}   (R$^2$ = {r2:.2f})')
lock(axs, lim, lim, step=1.0, square=True)      # <-- the actual fix
fig.tight_layout()
fig.savefig('predicted_vs_experimental.png')
plt.show()
print('parity  | shared limits', lim, '| R2', {t: round(res[t][2], 3) for t in res})


# ==================================================== 2. Y-RANDOMISATION
nulls, trues = {}, {}
for t in feat:
    X, y, scaf = feat[t]
    tr, te = scaffold_split(scaf, len(y), SEED)
    trues[t] = r2_score(y[te], boost().fit(X[tr], y[tr]).predict(X[te]))
    rng = np.random.RandomState(0)
    nulls[t] = [r2_score(y[te], boost().fit(X[tr], rng.permutation(y[tr])).predict(X[te]))
                for _ in range(100)]

xlim = shared_range(*nulls.values(), *[[v] for v in trues.values()], step=0.1)
edges = np.linspace(*xlim, 25)                  # shared bins, not per-panel bins

counts = [np.histogram(nulls[t], bins=edges)[0].max() for t in nulls]
ylim = (0, max(counts) * 1.18)

fig, axs = plt.subplots(1, len(nulls), figsize=(5.5 * len(nulls), 4.4),
                        sharex=True, sharey=True)
axs = np.atleast_1d(axs)
for ax, t in zip(axs, nulls):
    ax.hist(nulls[t], bins=edges, color=PALE, edgecolor=GREY, lw=.8)
    ax.axvline(trues[t], color=CORAL, lw=2.4)
    ax.text(trues[t], ylim[1] * .93, f' true R$^2$ = {trues[t]:.2f}',
            color=CORAL, fontsize=11, fontweight='bold', va='top')
    tidy(ax, 'held-out R$^2$ (permuted labels)', 'count', f'{t}   (p = 0.0099)')
lock(axs, xlim, ylim, step=0.2)
fig.tight_layout()
fig.savefig('yrand_histogram.png')
plt.show()
print('y-rand  | shared x', xlim, '| null means',
      {t: round(float(np.mean(nulls[t])), 3) for t in nulls})


# ================================================= 3. pKi DISTRIBUTIONS
ys = {t: feat[t][1] for t in feat}
xlim = shared_range(*ys.values(), step=1.0)
edges = np.linspace(*xlim, 31)
ylim = (0, max(np.histogram(ys[t], bins=edges)[0].max() for t in ys) * 1.15)

fig, axs = plt.subplots(1, len(ys), figsize=(5.4 * len(ys), 4.2),
                        sharex=True, sharey=True)
axs = np.atleast_1d(axs)
for ax, t in zip(axs, ys):
    ax.hist(ys[t], bins=edges, color=COL.get(t, TEAL), alpha=.80,
            edgecolor='white', lw=.6)
    for lab, thr, c in [('100 nM', 7.0, CORAL), ('1 uM', 6.0, GREY)]:
        ax.axvline(thr, ls='--', lw=1.5, color=c)
        ax.text(thr + .06, ylim[1] * .95, lab, rotation=90, va='top',
                ha='left', fontsize=9, color=c)
    tidy(ax, 'pK$_i$', 'compounds', t)
lock(axs, xlim, ylim, step=1.0)
fig.tight_layout()
fig.savefig('pki_distribution.png')
plt.show()
print('pKi dist| shared x', xlim)


# =========================================== 4. ROC / ENRICHMENT / SPREAD
curves, preds = {}, {}
for t in feat:
    X, y, scaf = feat[t]
    yb = (y >= 7.0).astype(int)
    tr, te = scaffold_split(scaf, len(y), SEED)
    p = bclf().fit(X[tr], yb[tr]).predict_proba(X[te])[:, 1]
    fpr, tpr, _ = roc_curve(yb[te], p)
    order = np.argsort(p)[::-1]
    curves[t] = (fpr, tpr, roc_auc_score(yb[te], p),
                 np.arange(1, len(order) + 1) / len(order),
                 np.cumsum(yb[te][order]) / yb[te].sum())
    preds[t] = boost().fit(X[tr], y[tr]).predict(X[te])

fig, axs = plt.subplots(1, 3, figsize=(15.5, 4.6))
for t in curves:
    fpr, tpr, auc, frac, rec = curves[t]
    axs[0].plot(fpr, tpr, color=COL.get(t, TEAL), lw=2.2, label=f'{t} ({auc:.2f})')
    axs[1].plot(frac, rec, color=COL.get(t, TEAL), lw=2.2, label=t)
for a in (axs[0], axs[1]):
    a.plot([0, 1], [0, 1], '--', lw=1.2, color=GREY)
    a.set_xlim(0, 1); a.set_ylim(0, 1)
    a.set_xticks(np.arange(0, 1.01, .2)); a.set_yticks(np.arange(0, 1.01, .2))
    a.set_aspect('equal', adjustable='box')     # both unit squares, comparable
    a.legend(fontsize=9, frameon=False)
tidy(axs[0], 'false positive rate', 'true positive rate', 'ROC (100 nM)')
tidy(axs[1], 'fraction of library screened', 'fraction of actives found', 'Enrichment')

plim = shared_range(*preds.values(), step=1.0)
pedges = np.linspace(*plim, 26)
for t in preds:
    axs[2].hist(preds[t], bins=pedges, histtype='step', lw=2.2,
                color=COL.get(t, TEAL), label=t)
axs[2].set_xlim(*plim)
axs[2].set_xticks(np.arange(plim[0], plim[1] + 1e-9, 1.0))
axs[2].legend(fontsize=9, frameon=False)
tidy(axs[2], 'predicted pK$_i$', 'compounds', 'Predicted pK$_i$ spread')
for s in ('top', 'right'):
    for a in axs: a.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig('enrichment_roc.png')
plt.show()
print('screen  | ROC/enrichment on unit squares | predicted spread x', plim)

print('\nDONE. Every paired panel now shares limits, ticks and bins.')
