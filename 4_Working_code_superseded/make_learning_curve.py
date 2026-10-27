#!/usr/bin/env python3
"""Learning curve, two panels, from lc_final.jsonl (5 scaffold splits per size).

Data: lc_final.py on the final feature matrices. Each point is a mean over 5
splits; the band is +/- 1 SD. The x value is the ACTUAL number of training
rows used, which is what 06_expanded_models cell 17 got wrong.

Writes: thesis_clean/figures/deck_learning_curve.png
"""
import json, statistics as st
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INK, TEAL, CORAL, GREY, PALE = '#22333B', '#116E64', '#BE5638', '#60727A', '#CBDDDA'
OUT = '/sessions/sharp-elegant-gauss/mnt/outputs/thesis_clean/figures/deck_learning_curve.png'

d = defaultdict(list)
for l in open('/sessions/sharp-elegant-gauss/mnt/outputs/lc_final.jsonl'):
    r = json.loads(l); d[(r['target'], r['size'])].append(r)

def series(t):
    ks = sorted(d, key=lambda k: (1e9 if k[1] < 0 else k[1]))
    ks = [k for k in ks if k[0] == t]
    xs = [int(st.mean([r['n_train'] for r in d[k]])) for k in ks]
    ys = [st.mean([r['r2'] for r in d[k]]) for k in ks]
    sd = [st.pstdev([r['r2'] for r in d[k]]) for k in ks]
    return xs, ys, sd

PANELS = [('5-HT$_{2A}$ learning curve', '5-HT2A', TEAL),
          ('Dopamine D$_3$ learning curve', 'Dopamine_D3', CORAL)]

XLIM, YLIM = (0, 4800), (0.10, 0.75)
XTICKS = np.arange(0, 4801, 1200)
YTICKS = np.arange(0.1, 0.751, 0.10)

fig, axs = plt.subplots(1, 2, figsize=(12.6, 4.7), sharex=True, sharey=True)
for ax, (title, key, col) in zip(axs, PANELS):
    xs, ys, sd = series(key)
    ax.fill_between(xs, np.array(ys) - np.array(sd), np.array(ys) + np.array(sd),
                    color=col, alpha=.16, lw=0)
    ax.plot(xs, ys, '-o', lw=3.0, ms=9, color=col, mec='white', mew=1.5, zorder=3)
    for i, (x, y) in enumerate(zip(xs, ys)):
        # suppress a label when the NEXT point is too close in x to sit beside it.
        # Only 5-HT2A 3,500 vs full-pool 3,696 (196 apart) trips it; 200 vs 500 (300) does not.
        # exactly the collision in 06_expanded_models cell 17. The marker stays; only
        # the text is dropped, and the full-pool value is the one worth reading.
        if i < len(xs) - 1 and (xs[i + 1] - x) < 250:
            continue
        ax.annotate(f'{y:.3f}', xy=(x, y), xytext=(0, 16), textcoords='offset points',
                    ha='center', fontsize=11.5, color=INK, fontweight='bold')
        ax.annotate(f'n={x:,}', xy=(x, y), xytext=(0, 3), textcoords='offset points',
                    ha='center', fontsize=9.5, color=GREY)
    ax.set_xlim(*XLIM); ax.set_ylim(*YLIM)
    ax.set_xticks(XTICKS); ax.set_yticks(YTICKS)
    ax.set_xlabel('training compounds (actual)', fontsize=12.5, color=INK)
    ax.set_title(title, fontsize=13.5, color=INK, fontweight='bold', pad=10)
    ax.grid(alpha=.22, lw=.7, color=PALE); ax.set_axisbelow(True)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    ax.spines['bottom'].set_color(PALE); ax.spines['left'].set_color(PALE)
    ax.tick_params(colors=GREY, labelsize=10.5)

axs[0].set_ylabel('scaffold-split R$^2$', fontsize=12.5, color=INK)
axs[0].text(0.02, 0.03, 'mean of 5 scaffold splits; band = $\\pm$1 SD',
            transform=axs[0].transAxes, fontsize=9, color=GREY, style='italic')
fig.tight_layout(pad=0.6)
fig.savefig(OUT, dpi=300, transparent=True, bbox_inches='tight', pad_inches=0.05)
print('wrote', OUT)
for _, k, _ in PANELS:
    xs, ys, sd = series(k)
    print(' ', k, [(x, round(y, 3)) for x, y in zip(xs, ys)])
