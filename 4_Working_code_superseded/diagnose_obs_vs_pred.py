# =============================================================================
#  DIAGNOSE + PLOT: experimental vs predicted pKi
#  Paste as one cell in 10_additions.ipynb, after cell 5 has been run.
#  It reports where the data disappears, then plots only if the data is usable.
# =============================================================================
import numpy as np, matplotlib.pyplot as plt

print("STEP 1 - does the setup exist?")
for name in ['feat', 'scaffold_split', 'boost']:
    print(f"   {name:<16} {'FOUND' if name in globals() else 'MISSING  <-- run cell 5 first'}")
if 'feat' not in globals():
    raise SystemExit("Stop: run cells 1-5 first, in order, in this same kernel.")

print(f"\nSTEP 2 - what is in feat?   keys = {list(feat.keys())}")
if len(feat) == 0:
    raise SystemExit("Stop: feat is empty. Re-run cell 3 (curation) and cell 4 (featurise).")

DATA, problems = {}, []
for t in feat:
    X, y, scaf = feat[t]
    y = np.asarray(y, dtype=float).ravel()
    print(f"\n--- {t} ---")
    print(f"   X {np.shape(X)},  y n={y.size},  scaffolds n={len(scaf)}")
    if y.size == 0:
        problems.append(f"{t}: y is empty"); continue
    nan_y = int((~np.isfinite(y)).sum())
    print(f"   y: min={np.nanmin(y):.2f} max={np.nanmax(y):.2f} "
          f"mean={np.nanmean(y):.2f}  non-finite={nan_y}")

    tr, te = scaffold_split(scaf, len(y), 0)
    print(f"   split: train={len(tr)}  test={len(te)}")
    if len(te) == 0:
        problems.append(f"{t}: TEST SPLIT IS EMPTY -> nothing to plot"); continue
    if len(tr) == 0:
        problems.append(f"{t}: train split empty"); continue

    yt = y[te]
    yp = np.asarray(boost().fit(X[tr], y[tr]).predict(X[te]), dtype=float).ravel()
    nan_p = int((~np.isfinite(yp)).sum())
    print(f"   predictions: n={yp.size}  non-finite={nan_p}")

    keep = np.isfinite(yt) & np.isfinite(yp)          # drop bad pairs
    if keep.sum() == 0:
        problems.append(f"{t}: every value is NaN/inf after prediction"); continue
    if keep.sum() < yt.size:
        print(f"   dropped {yt.size - keep.sum()} non-finite pairs")
    DATA[t] = (yt[keep], yp[keep])
    print(f"   USABLE: n={keep.sum()}  exp SD={yt[keep].std():.2f}  pred SD={yp[keep].std():.2f}")

print("\n" + "=" * 62)
if problems:
    print("PROBLEMS FOUND:")
    for p in problems: print("   -", p)
if not DATA:
    raise SystemExit("Nothing plottable. Fix the problems above.")
print(f"OK - plotting {len(DATA)} target(s)")

# ---- shared, locked axes ----------------------------------------------------
allv = np.concatenate([np.concatenate(v) for v in DATA.values()])
lo, hi = np.floor(allv.min()*2)/2 - 0.5, np.ceil(allv.max()*2)/2 + 0.5
assert np.isfinite([lo, hi]).all(), "axis limits are not finite"
bins  = np.linspace(lo, hi, 34)
ticks = np.arange(np.ceil(lo), np.floor(hi) + 1, 1.0)
print(f"shared axis range: ({lo:.1f}, {hi:.1f})")

TEAL, CORAL, INK, GREY = '#116E64', '#BE5638', '#22333B', '#60727A'
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
    ax.set_title(f'{t}   (SD {yt.std():.2f} exp vs {yp.std():.2f} pred)', fontsize=11, color=INK)
    ax.set_xlabel('pK$_i$', color=INK); ax.set_xlim(lo, hi); ax.set_xticks(ticks)
    ax.spines[['top','right']].set_visible(False); ax.tick_params(colors=GREY)
    ax.legend(frameon=False, fontsize=10)
    print(f"{t}: variance retained {yp.std()/yt.std():.0%}")
for ax in axs: ax.set_ylim(0, peak*1.15)
axs[0].set_ylabel('density', color=INK)
fig.tight_layout(); fig.savefig('obs_vs_pred_distribution.png', dpi=300,
                                bbox_inches='tight', facecolor='white'); plt.show()

import pandas as pd
pd.concat([pd.DataFrame({'target': t, 'y_true': v[0], 'y_pred': v[1]})
           for t, v in DATA.items()], ignore_index=True) \
  .to_csv('predictions_heldout.csv', index=False)
print("saved -> obs_vs_pred_distribution.png, predictions_heldout.csv")
