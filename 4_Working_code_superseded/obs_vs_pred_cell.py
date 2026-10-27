# =============================================================================
#  Experimental vs predicted pKi  -  SHARED, LOCKED AXES
#  Paste as ONE new cell in 10_additions.ipynb, anywhere after cell 5.
#  Uses your own objects: feat, scaffold_split(), boost()  -  nothing is redefined.
#  Seed 0, same as the enrichment/ROC figure, so it matches the thesis.
# =============================================================================
import numpy as np, matplotlib.pyplot as plt, pandas as pd

TEAL, CORAL, INK, GREY = '#116E64', '#BE5638', '#22333B', '#60727A'
PKI_LIM = None      # None = derive one shared range; or hard-code e.g. (3.5, 12.0)
NBINS   = 34

# ---- 1. held-out predictions, per target -----------------------------------
DATA = {}
for t in feat:
    X, y, scaf = feat[t]
    tr, te = scaffold_split(scaf, len(y), 0)
    yp = boost().fit(X[tr], y[tr]).predict(X[te])
    DATA[t] = (np.asarray(y)[te], np.asarray(yp))
    print(f'{t}: n_test={len(te)}')

# ---- 2. ONE range for every panel ------------------------------------------
allv = np.concatenate([np.concatenate(v) for v in DATA.values()])
lo, hi = PKI_LIM if PKI_LIM else (np.floor(allv.min()*2)/2 - 0.5,
                                  np.ceil(allv.max()*2)/2 + 0.5)
bins  = np.linspace(lo, hi, NBINS)
ticks = np.arange(np.ceil(lo), np.floor(hi) + 1, 1.0)
print(f'\nshared axis range: ({lo:.1f}, {hi:.1f})  <- reuse in every other figure')

# ---- 3. distribution: experimental vs predicted --------------------------------
fig, axs = plt.subplots(1, len(DATA), figsize=(11.5, 4.0), sharex=True, sharey=True)
axs = np.atleast_1d(axs); peak = 0
for ax, (t, (yt, yp)) in zip(axs, DATA.items()):
    h1, _, _ = ax.hist(yt, bins=bins, histtype='stepfilled', alpha=0.45,
                       color=TEAL, label='experimental', density=True)
    h2, _, _ = ax.hist(yp, bins=bins, histtype='step', lw=2.2,
                       color=CORAL, label='predicted', density=True)
    peak = max(peak, h1.max(), h2.max())
    ax.axvline(yt.mean(), color=TEAL, ls=':', lw=1.6)
    ax.axvline(yp.mean(), color=CORAL, ls=':', lw=1.6)
    ax.set_title(f'{t}   (SD {yt.std():.2f} exp vs {yp.std():.2f} pred)',
                 fontsize=11, color=INK)
    ax.set_xlabel('pK$_i$', color=INK); ax.set_xlim(lo, hi); ax.set_xticks(ticks)
    ax.spines[['top', 'right']].set_visible(False); ax.tick_params(colors=GREY)
    ax.legend(frameon=False, fontsize=10)
    print(f'{t}:  exp mean {yt.mean():.2f} SD {yt.std():.2f}  |  '
          f'pred mean {yp.mean():.2f} SD {yp.std():.2f}  |  '
          f'variance retained {yp.std()/yt.std():.0%}')
for ax in axs:
    ax.set_ylim(0, peak * 1.15)
axs[0].set_ylabel('density', color=INK)
fig.tight_layout(); fig.savefig('obs_vs_pred_distribution.png', dpi=300,
                                bbox_inches='tight', facecolor='white'); plt.show()

# ---- 4. scatter: x and y identical, square, true 45-degree line ------------
fig, axs = plt.subplots(1, len(DATA), figsize=(10.5, 5.0), sharex=True, sharey=True)
axs = np.atleast_1d(axs)
for ax, (t, (yt, yp)) in zip(axs, DATA.items()):
    ax.scatter(yt, yp, s=9, alpha=0.35, color=TEAL, edgecolors='none')
    ax.plot([lo, hi], [lo, hi], ls='--', lw=1.4, color=CORAL)
    r2 = 1 - ((yt - yp)**2).sum() / ((yt - yt.mean())**2).sum()
    ax.set_title(f'{t}   (R$^2$ = {r2:.2f})', fontsize=11, color=INK)
    ax.set_xlabel('experimental pK$_i$', color=INK)
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xticks(ticks); ax.set_yticks(ticks)
    ax.set_aspect('equal', adjustable='box')
    ax.spines[['top', 'right']].set_visible(False); ax.tick_params(colors=GREY)
axs[0].set_ylabel('predicted pK$_i$', color=INK)
fig.tight_layout(); fig.savefig('obs_vs_pred_scatter.png', dpi=300,
                                bbox_inches='tight', facecolor='white'); plt.show()

# ---- 5. keep the numbers so a kernel restart never costs you this again ----
pd.concat([pd.DataFrame({'target': t, 'y_true': v[0], 'y_pred': v[1]})
           for t, v in DATA.items()], ignore_index=True) \
  .to_csv('predictions_heldout.csv', index=False)
print('\nsaved -> obs_vs_pred_distribution.png, obs_vs_pred_scatter.png, '
      'predictions_heldout.csv')
