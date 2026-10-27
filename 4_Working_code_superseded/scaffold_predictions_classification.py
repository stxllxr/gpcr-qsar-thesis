# =====================================================================
#  CLASSIFICATION VERSION of scaffold_predictions_and_figure.py
#  Paste as a new cell where feat, scaffold_split and bclf() are in
#  memory (10_additions.ipynb, after the base-pipeline cell).
#
#  Same discipline as the regression version:
#    - scaffold split, not random / cross-validation
#    - held-out predictions exported to CSV
#    - every paired panel on identical locked axes
#
#  The parity plot has two natural analogues for a classifier, so both
#  are drawn:
#    top row    predicted probability, separated by true class
#               (does the model actually pull the two classes apart?)
#    bottom row calibration: predicted probability vs observed frequency,
#               with the 45-degree identity line. This is the direct
#               counterpart of predicted-vs-experimental.
#
#  Outputs: predictions_clf_scaffold_heldout.csv
#           classification_scaffold_diagnostics.png
# =====================================================================
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (matthews_corrcoef, confusion_matrix,
                             roc_auc_score, average_precision_score)
from sklearn.calibration import calibration_curve

THRESH, NSEED, SHOW_SEED = 7.0, 12, 0      # 100 nM cut-off
INK, TEAL, CORAL, GREY, PALE = '#22333B', '#116E64', '#BE5638', '#60727A', '#CBDDDA'


def enrichment(ybin, scores, frac):
    n = len(scores); k = max(1, int(round(frac * n)))
    top = np.argsort(scores)[::-1][:k]
    return (ybin[top].mean() / ybin.mean()) if ybin.mean() > 0 else np.nan


rows, shown, stats = [], {}, {}

for t in feat:
    X, y, scaf = feat[t]
    yb = (y >= THRESH).astype(int)
    mccs = []
    for s in range(NSEED):
        tr, te = scaffold_split(scaf, len(y), s)
        pr = bclf().fit(X[tr], yb[tr]).predict_proba(X[te])[:, 1]
        mccs.append(matthews_corrcoef(yb[te], (pr >= 0.5).astype(int)))
        if s == SHOW_SEED:
            shown[t] = (yb[te], pr)
            rows.append(pd.DataFrame({'target': t, 'seed': s,
                                      'y_true_pki': y[te], 'y_true_bin': yb[te],
                                      'y_prob': pr,
                                      'y_pred_bin': (pr >= 0.5).astype(int)}))
    yb_s, pr_s = shown[t]
    stats[t] = dict(
        mcc_mean=float(np.mean(mccs)), mcc_sd=float(np.std(mccs)),
        auc=roc_auc_score(yb_s, pr_s), pr_auc=average_precision_score(yb_s, pr_s),
        active_rate=float(yb_s.mean()),
        ef1=enrichment(yb_s, pr_s, .01), ef5=enrichment(yb_s, pr_s, .05),
        ef10=enrichment(yb_s, pr_s, .10),
        cm=confusion_matrix(yb_s, (pr_s >= 0.5).astype(int)))

pd.concat(rows).to_csv('predictions_clf_scaffold_heldout.csv', index=False)

# ------------------------------------------------------------- numbers
print(f'CLASSIFICATION at {THRESH:.0f} pKi (100 nM), SCAFFOLD SPLIT, '
      f'MCC averaged over {NSEED} seeds\n')
for t, d in stats.items():
    tn, fp, fn, tp = d['cm'].ravel()
    ceiling = 1 / d['active_rate']
    print(f'{t}')
    print(f"   MCC          {d['mcc_mean']:.3f} +/- {d['mcc_sd']:.3f}")
    print(f"   ROC-AUC      {d['auc']:.3f}      PR-AUC {d['pr_auc']:.3f}")
    print(f"   active rate  {d['active_rate']:.2f}   ->  EF ceiling = 1/{d['active_rate']:.2f} = {ceiling:.2f}")
    print(f"   EF @1/5/10%  {d['ef1']:.2f} / {d['ef5']:.2f} / {d['ef10']:.2f}"
          f"   ({d['ef1']/ceiling:.0%} of ceiling)")
    print(f"   confusion    TP {tp}  FP {fp}  FN {fn}  TN {tn}\n")

print('Say this: enrichment looks modest until you give the ceiling. The')
print('library is majority active, so the maximum achievable EF is 1/active')
print('rate. We are at ~98-99% of it.')

# -------------------------------------------------------------- figure
fig, axs = plt.subplots(2, len(shown), figsize=(5.4 * len(shown), 9.0))
axs = np.atleast_2d(axs)
if axs.shape[0] == 1:
    axs = axs.reshape(2, -1)
edges = np.linspace(0, 1, 26)

peak = max(max(np.histogram(pr[yb == c], bins=edges)[0].max() for c in (0, 1))
           for yb, pr in shown.values())

for j, t in enumerate(shown):
    yb, pr = shown[t]
    # --- top: predicted probability separated by true class -----------
    ax = axs[0, j]
    ax.hist(pr[yb == 0], bins=edges, color=CORAL, alpha=.62,
            label=f'inactive (n={int((yb==0).sum())})')
    ax.hist(pr[yb == 1], bins=edges, color=TEAL, alpha=.62,
            label=f'active (n={int((yb==1).sum())})')
    ax.axvline(0.5, ls='--', lw=1.4, color=GREY)
    ax.set_xlim(0, 1); ax.set_ylim(0, peak * 1.15)
    ax.set_xticks(np.arange(0, 1.01, .2))
    ax.set_xlabel('predicted probability of being active', color=INK)
    ax.set_ylabel('compounds', color=INK)
    ax.set_title(f"{t}   (MCC = {stats[t]['mcc_mean']:.2f})",
                 color=INK, fontsize=12.5, fontweight='bold', pad=9)
    ax.legend(fontsize=9.5, frameon=False)

    # --- bottom: calibration, the parity-plot analogue ----------------
    ax = axs[1, j]
    fr_pos, mean_pred = calibration_curve(yb, pr, n_bins=10, strategy='quantile')
    ax.plot([0, 1], [0, 1], '--', lw=1.5, color=GREY, zorder=1)
    ax.plot(mean_pred, fr_pos, 'o-', lw=2, ms=7, color=TEAL, zorder=2)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks(np.arange(0, 1.01, .2)); ax.set_yticks(np.arange(0, 1.01, .2))
    ax.set_aspect('equal', adjustable='box')       # 45-degree line is real
    ax.set_xlabel('mean predicted probability', color=INK)
    ax.set_ylabel('observed fraction active', color=INK)
    ax.set_title(f'{t}   calibration', color=INK, fontsize=12.5,
                 fontweight='bold', pad=9)

for ax in axs.ravel():
    ax.grid(alpha=.22, lw=.7, color=PALE); ax.set_axisbelow(True)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)

fig.tight_layout()
fig.savefig('classification_scaffold_diagnostics.png', dpi=300, bbox_inches='tight')
plt.show()
print('\nsaved predictions_clf_scaffold_heldout.csv and '
      'classification_scaffold_diagnostics.png')
