# ---- experimental vs predicted, SIDE-BY-SIDE bars, shared locked axes -----------
import numpy as np, matplotlib.pyplot as plt

TEAL, CORAL, INK, GREY = '#116E64', '#BE5638', '#22333B', '#60727A'
NBINS = 22                      # fewer bins than the overlay: paired bars need room

allv = np.concatenate([np.concatenate(v) for v in DATA.values()])
lo, hi = np.floor(allv.min()*2)/2 - 0.5, np.ceil(allv.max()*2)/2 + 0.5
edges  = np.linspace(lo, hi, NBINS + 1)
ctr    = (edges[:-1] + edges[1:]) / 2
w      = (edges[1] - edges[0]) * 0.42        # each bar a bit under half a bin
ticks  = np.arange(np.ceil(lo), np.floor(hi) + 1, 1.0)

fig, axs = plt.subplots(1, len(DATA), figsize=(12.0, 4.2), sharex=True, sharey=True)
axs = np.atleast_1d(axs); peak = 0
for ax, (t, (yt, yp)) in zip(axs, DATA.items()):
    ho, _ = np.histogram(yt, bins=edges, density=True)
    hp, _ = np.histogram(yp, bins=edges, density=True)
    peak = max(peak, ho.max(), hp.max())
    ax.bar(ctr - w/2, ho, width=w, color=TEAL,  label='experimental',  edgecolor='white', linewidth=0.4)
    ax.bar(ctr + w/2, hp, width=w, color=CORAL, label='predicted', edgecolor='white', linewidth=0.4)
    ax.set_title(f'{t}   (SD {yt.std():.2f} exp vs {yp.std():.2f} pred,'
                 f' {yp.std()/yt.std():.0%} retained)', fontsize=11, color=INK)
    ax.set_xlabel('pK$_i$', color=INK)
    ax.set_xlim(lo, hi); ax.set_xticks(ticks)
    ax.spines[['top', 'right']].set_visible(False); ax.tick_params(colors=GREY)
    ax.legend(frameon=False, fontsize=10)
for ax in axs: ax.set_ylim(0, peak*1.15)
axs[0].set_ylabel('density', color=INK)
fig.tight_layout()
fig.savefig('obs_vs_pred_distribution.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
