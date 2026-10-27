# =====================================================================
#  SCAFFOLD-SPLIT PREDICTIONS + PARITY FIGURE
#  Paste as a new cell where feat, scaffold_split and boost() are in
#  memory (08_full_model.ipynb, after Cell A).
#
#  Replaces check_scaffold_rmse.py -- this does that job and more.
#
#  Why this exists
#  ---------------
#  predictions_heldout.csv contains 10,108 rows = every compound in both
#  sets, and reproduces the CV10 row of Table A exactly (R2 0.679/0.717,
#  RMSE 0.696/0.687). So it is 10-fold cross-validation out-of-fold
#  predictions, NOT scaffold-split held-out predictions. A parity plot
#  built from it shows R2 0.68/0.72, which contradicts the 0.562/0.644
#  the thesis leads with.
#
#  This cell produces the scaffold-split equivalent, so figure and table
#  tell the same story, and it prints the scaffold RMSE that Table A
#  never had a column for.
#
#  Outputs: predictions_scaffold_heldout.csv
#           predicted_vs_experimental_scaffold.png
# =====================================================================
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, mean_squared_error

NSEED, SHOW_SEED = 12, 0
INK, TEAL, CORAL, GREY, PALE = '#22333B', '#116E64', '#BE5638', '#60727A', '#CBDDDA'
COL = {'5-HT2A': TEAL, 'Dopamine D3': CORAL}

rows, shown, stats = [], {}, {}

for t in feat:
    X, y, scaf = feat[t]
    r2s, rmses = [], []
    for s in range(NSEED):
        tr, te = scaffold_split(scaf, len(y), s)
        pr = boost().fit(X[tr], y[tr]).predict(X[te])
        r2s.append(r2_score(y[te], pr))
        rmses.append(np.sqrt(mean_squared_error(y[te], pr)))
        if s == SHOW_SEED:
            shown[t] = (y[te], pr)
            rows.append(pd.DataFrame({'target': t, 'seed': s,
                                      'y_true': y[te], 'y_pred': pr}))
    stats[t] = (np.mean(r2s), np.std(r2s), np.mean(rmses), np.std(rmses))

pd.concat(rows).to_csv('predictions_scaffold_heldout.csv', index=False)

# ------------------------------------------------------------- numbers
print('SCAFFOLD SPLIT, mean over %d seeds' % NSEED)
print(f'{"target":14s} {"R2":>14s} {"RMSE":>14s} {"vs 0.5 floor":>13s} {"fold in conc":>13s}')
print('-' * 74)
for t, (r2, r2sd, rmse, rmsesd) in stats.items():
    print(f'{t:14s} {r2:7.3f}+/-{r2sd:.3f} {rmse:7.3f}+/-{rmsesd:.3f} '
          f'{rmse/0.5:12.2f}x {10**rmse:12.1f}x')

print('\nCompression, scaffold split seed %d (for the distribution slide)' % SHOW_SEED)
for t, (yt, pr) in shown.items():
    se, sp = float(np.std(yt)), float(np.std(pr))
    print(f'  {t:14s} SD experimental {se:.2f}  SD predicted {sp:.2f}  '
          f'{sp/se:.0%} of the spread retained')

print('\nFor comparison, the CV10 numbers already in Table A: '
      'R2 0.679 / 0.717, RMSE 0.696 / 0.687')

# -------------------------------------------------------------- figure
lim_lo = np.floor(min(min(v[0].min(), v[1].min()) for v in shown.values()) - .4)
lim_hi = np.ceil(max(max(v[0].max(), v[1].max()) for v in shown.values()) + .4)
lim, ticks = (lim_lo, lim_hi), np.arange(lim_lo, lim_hi + 1e-9, 1.0)

fig, axs = plt.subplots(1, len(shown), figsize=(5.3 * len(shown), 5.4),
                        sharex=True, sharey=True)
axs = np.atleast_1d(axs)
for ax, t in zip(axs, shown):
    yt, pr = shown[t]
    ax.plot(lim, lim, '--', lw=1.5, color=GREY, zorder=1)
    ax.scatter(yt, pr, s=11, alpha=.32, color=COL.get(t, TEAL),
               edgecolors='none', zorder=2)
    ax.set_xlabel('experimental pK$_i$', color=INK)      # not "observed"
    ax.set_ylabel('predicted pK$_i$', color=INK)
    ax.set_title(f'{t}   (scaffold R$^2$ = {r2_score(yt, pr):.2f})',
                 color=INK, fontsize=12.5, fontweight='bold', pad=9)
    ax.set_xlim(*lim); ax.set_ylim(*lim)
    ax.set_xticks(ticks); ax.set_yticks(ticks)
    ax.set_aspect('equal', adjustable='box')             # 45 deg identity line
    ax.grid(alpha=.22, lw=.7, color=PALE); ax.set_axisbelow(True)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig('predicted_vs_experimental_scaffold.png', dpi=300, bbox_inches='tight')
plt.show()
print('\nsaved predictions_scaffold_heldout.csv and '
      'predicted_vs_experimental_scaffold.png')
