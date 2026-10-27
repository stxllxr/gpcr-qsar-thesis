# =====================================================================
#  SCAFFOLD-SPLIT RMSE  -- paste as a new cell where feat, scaffold_split
#  and boost() are in memory (08_full_model.ipynb after Cell A).
#
#  Why
#  ---
#  Table A in 08_full_model prints scaffold_R2, CV10_R2 and CV10_RMSE.
#  There is no scaffold RMSE column. But results.tex says the scaffold
#  split reached "root-mean-squared errors of 0.70 and 0.69 log units",
#  and 0.70 / 0.69 are exactly the CV10_RMSE values. So the RMSE being
#  quoted for the scaffold split is very likely the cross-validation RMSE.
#
#  Since scaffold R2 (0.562 / 0.644) is well below CV R2 (0.679 / 0.717)
#  on the same data, the scaffold RMSE must be HIGHER, not equal. This
#  cell measures it directly so the thesis can quote the right number.
# =====================================================================
import numpy as np
from sklearn.metrics import r2_score, mean_squared_error

NSEED = 12
print(f'{"target":14s} {"scaffold R2":>12s} {"scaffold RMSE":>14s} {"y SD":>7s} {"RMSE/0.5":>9s}')
print('-' * 62)

summary = {}
for t in feat:
    X, y, scaf = feat[t]
    r2s, rmses = [], []
    for s in range(NSEED):
        tr, te = scaffold_split(scaf, len(y), s)
        pr = boost().fit(X[tr], y[tr]).predict(X[te])
        r2s.append(r2_score(y[te], pr))
        rmses.append(np.sqrt(mean_squared_error(y[te], pr)))
    r2, rmse, sd = np.mean(r2s), np.mean(rmses), float(np.std(y))
    summary[t] = (r2, rmse, sd)
    print(f'{t:14s} {r2:12.3f} {rmse:14.3f} {sd:7.2f} {rmse/0.5:9.2f}x')

print('\nInterpretation')
print('  The last column is the ratio to the ~0.5 log-unit inter-laboratory')
print('  noise floor (Kalliokoski 2013; Landrum & Riniker 2024). Quote THIS')
print('  number for the scaffold split, and label the 0.68-0.70 values in')
print('  Table 3.7 explicitly as 10-fold CV RMSE.')
for t, (r2, rmse, sd) in summary.items():
    print(f'  {t}: scaffold RMSE {rmse:.2f} log units '
          f'= a factor of {10**rmse:.1f} in concentration')
