#!/usr/bin/env python3
"""
make_figures.py
Regenerate every figure in the thesis from the locked dataset, in a consistent
SANS-SERIF style.

Usage:
    python make_figures.py
Requires: pandas, numpy, matplotlib, seaborn, scikit-learn, rdkit, scipy
Inputs:
    curated_15desc.csv                         (descriptive figures)
    results_data/tab_repeated_raw.csv          (5-HT2A benchmark figure)
    results_data/panel_results.csv             (panel figure)
    results_data/panel_yrand2.csv              (panel figure)
Output:
    figures/*.png
"""

import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------------------------
# Global SANS-SERIF style  (edit FONT to taste; DejaVu Sans is always present)
# ---------------------------------------------------------------------------
SANS = ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"]
sns.set_theme(style="whitegrid")          # set seaborn first ...
mpl.rcParams.update({                      # ... then enforce our fonts/sizes
    "font.family": "sans-serif",
    "font.sans-serif": SANS,
    "mathtext.fontset": "dejavusans",     # keep math (pK_i, R^2) sans-serif too
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 12,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 11,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.unicode_minus": False,
})

CSV = "curated_15desc.csv"
RES = "results_data"
OUT = "figures"
os.makedirs(OUT, exist_ok=True)
def save(fig, name):
    fig.savefig(os.path.join(OUT, name)); plt.close(fig); print("wrote", name)

DESC15 = ["MW", "LogP", "LogS", "HBA", "HBD", "TPSA", "RotB", "RingCount",
          "HAC", "Fsp3", "HalogenCount", "QED", "LE", "LLE", "LELP"]
PHASE_PAL = ["#4C72B0", "#A6C5E8", "#E8C4A6", "#C44E52"]

df = pd.read_csv(CSV)
df["hal"] = np.where(df["HalogenCount"] > 0, "Halogenated", "Non-halogenated")


# ---- RDKit helpers (halogen type / subgroup) ------------------------------
def _halogen_counts(series):
    from rdkit import Chem, RDLogger
    RDLogger.DisableLog("rdApp.*")
    def c(s):
        m = Chem.MolFromSmiles(str(s))
        if m is None:
            return (0, 0, 0, 0)
        sy = [a.GetSymbol() for a in m.GetAtoms()]
        return (sy.count("F"), sy.count("Cl"), sy.count("Br"), sy.count("I"))
    return series.apply(c)


# ===========================================================================
# 1. Receptor family distribution (pie of main + bar of others)
# ===========================================================================
def fig_family():
    fam = df["family"].value_counts()
    main, others = fam.head(5), fam.iloc[5:]
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.5))
    vals = list(main.values) + [others.sum()]
    labs = list(main.index) + ["Others"]
    ax[0].pie(vals, labels=[f"{l}\n{v} ({100*v/len(df):.1f}%)" for l, v in zip(labs, vals)],
              colors=sns.color_palette("Set2", len(vals)), startangle=90,
              textprops={"fontsize": 10})
    ax[0].set_title("Receptor family distribution (main)")
    oc = others.sort_values()
    ax[1].barh(range(len(oc)), oc.values, color=sns.color_palette("crest", len(oc)))
    ax[1].set_yticks(range(len(oc))); ax[1].set_yticklabels(oc.index)
    for i, v in enumerate(oc.values):
        ax[1].text(v + 1, i, f"{v} ({100*v/len(df):.2f}%)", va="center", fontsize=9)
    ax[1].set_xlabel("Compound-target records"); ax[1].set_title("Other families")
    fig.tight_layout(); save(fig, "family_distribution.png")


# ===========================================================================
# 2. MW and pKi violins by clinical phase
# ===========================================================================
def fig_violins():
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.5))
    for a, col, title in [(ax[0], "MW", "Molecular Weight (Da) by clinical phase"),
                          (ax[1], "pKi", "pKi by clinical phase")]:
        sns.violinplot(data=df, x="max_phase", y=col, order=[1, 2, 3, 4],
                       hue="max_phase", palette=PHASE_PAL, legend=False,
                       inner="quartile", cut=0, ax=a)
        a.set_title(title); a.set_xlabel("Clinical phase")
    fig.tight_layout(); save(fig, "mw_pki_by_phase.png")


# ===========================================================================
# 3. Dual-axis mean MW & pKi trend across phases
# ===========================================================================
def fig_trend():
    g = df.groupby("max_phase").agg(mw=("MW", "mean"), mw_se=("MW", "sem"),
                                    pki=("pKi", "mean"), pki_se=("pKi", "sem"))
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.errorbar(g.index, g["pki"], yerr=g["pki_se"], fmt="o-", color="#4C72B0",
                 capsize=4, lw=2, label="pKi")
    ax1.set_ylabel("Mean pKi (\u00b1 SEM)", color="#4C72B0")
    ax1.tick_params(axis="y", labelcolor="#4C72B0")
    ax1.set_xlabel("Clinical phase"); ax1.set_xticks([1, 2, 3, 4])
    ax2 = ax1.twinx()
    ax2.errorbar(g.index, g["mw"], yerr=g["mw_se"], fmt="s--", color="#C44E52",
                 capsize=4, lw=2, label="MW")
    ax2.set_ylabel("Mean Molecular Weight (Da, \u00b1 SEM)", color="#C44E52")
    ax2.tick_params(axis="y", labelcolor="#C44E52"); ax2.grid(False)
    ax1.set_title("Binding affinity and molecular weight across clinical phases")
    fig.tight_layout(); save(fig, "mw_pki_trend.png")


# ===========================================================================
# 4. Pearson & Spearman correlation heatmaps
# ===========================================================================
def fig_heatmaps():
    fig, ax = plt.subplots(1, 2, figsize=(16, 7))
    for a, meth, t in zip(ax, ["pearson", "spearman"], ["Pearson", "Spearman"]):
        sns.heatmap(df[DESC15].corr(method=meth), cmap="coolwarm", vmin=-1, vmax=1,
                    square=True, ax=a, cbar_kws={"shrink": .8})
        a.set_title(f"{t} correlation (15 descriptors)")
    fig.tight_layout(); save(fig, "correlation_heatmaps.png")


# ===========================================================================
# 5 & 6. Correlation scatter grids
# ===========================================================================
def _scatter_grid(pairs, color, name):
    fig, ax = plt.subplots(2, 2, figsize=(11, 9)); ax = ax.ravel()
    for i, (x, y) in enumerate(pairs):
        sns.regplot(data=df, x=x, y=y, ax=ax[i],
                    scatter_kws={"s": 10, "alpha": 0.3, "color": color},
                    line_kws={"color": "black", "ls": "--"})
        r = df[x].corr(df[y])
        ax[i].set_title(f"{x} vs {y}  (r={r:.3f}, R\u00b2={r**2:.3f})", fontsize=12)
    fig.tight_layout(); save(fig, name)

def fig_pos_scatter():
    _scatter_grid([("MW", "HAC"), ("LogP", "LELP"), ("HBA", "TPSA"), ("LogS", "LLE")],
                  "#4C72B0", "corr_positive_scatter.png")

def fig_neg_scatter():
    _scatter_grid([("LogP", "LogS"), ("LogS", "LELP"), ("LLE", "LELP"), ("HAC", "LE")],
                  "#C44E52", "corr_negative_scatter.png")


# ===========================================================================
# 7. Halogenation status donut + halogen-type bar
# ===========================================================================
def fig_halogen_dist():
    hal = df["HalogenCount"] > 0
    ch = _halogen_counts(df.loc[hal, "parent_smiles"]); nh = int(hal.sum())
    F = sum(x[0] > 0 for x in ch); Cl = sum(x[1] > 0 for x in ch)
    Br = sum(x[2] > 0 for x in ch); I = sum(x[3] > 0 for x in ch)
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.5))
    ax[0].pie([hal.sum(), (~hal).sum()],
              labels=[f"Halogenated\n({hal.sum()}, {100*hal.mean():.1f}%)",
                      f"Non-halogenated\n({(~hal).sum()}, {100*(~hal).mean():.1f}%)"],
              colors=["#C44E52", "#4C9FC4"], startangle=90,
              wedgeprops=dict(width=0.42), textprops={"fontsize": 11})
    ax[0].set_title("Halogenation status (total dataset)")
    types = pd.Series({"Chlorine (Cl)": Cl, "Fluorine (F)": F,
                       "Iodine (I)": I, "Bromine (Br)": Br}).sort_values()
    ax[1].barh(range(len(types)), types.values, color=sns.color_palette("flare", len(types)))
    ax[1].set_yticks(range(len(types))); ax[1].set_yticklabels(types.index)
    for i, v in enumerate(types.values):
        ax[1].text(v + 5, i, f"{v} ({100*v/nh:.1f}%)", va="center", fontsize=9)
    ax[1].set_xlabel("Compounds"); ax[1].set_title("Halogen type (among halogenated)")
    fig.tight_layout(); save(fig, "halogen_distribution.png")


# ===========================================================================
# 8. Clinical phase by halogenation status
# ===========================================================================
def fig_phase_hal():
    ct = pd.crosstab(df["max_phase"], df["hal"], normalize="columns") * 100
    fig, ax = plt.subplots(figsize=(8.5, 5)); x = np.arange(4); w = 0.38
    ax.bar(x - w/2, ct["Halogenated"], w, label="Halogenated", color="#C44E52")
    ax.bar(x + w/2, ct["Non-halogenated"], w, label="Non-halogenated", color="#4C9FC4")
    for i, p in enumerate([1, 2, 3, 4]):
        ax.text(i - w/2, ct["Halogenated"][p] + 0.6, f"{ct['Halogenated'][p]:.1f}%", ha="center", fontsize=8)
        ax.text(i + w/2, ct["Non-halogenated"][p] + 0.6, f"{ct['Non-halogenated'][p]:.1f}%", ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(["Phase I", "Phase II", "Phase III", "Phase IV"])
    ax.set_ylabel("% of compounds")
    ax.set_title("Clinical phase by halogenation status (\u03c7\u00b2=3.34, p=0.342)")
    ax.legend(); fig.tight_layout(); save(fig, "phase_by_halogenation.png")


# ===========================================================================
# 9. Fsp3 by halogen subgroup
# ===========================================================================
def fig_fsp3():
    ch = _halogen_counts(df["parent_smiles"])
    def sub(t):
        f, cl, br, i = t; h = cl + br + i
        return ("non_halogenated" if f == 0 and h == 0 else
                "fluorine_only" if f > 0 and h == 0 else
                "heavy_only" if f == 0 and h > 0 else "mixed")
    df["hsub"] = [sub(t) for t in ch]
    order = ["non_halogenated", "fluorine_only", "heavy_only", "mixed"]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    sns.boxplot(data=df, x="hsub", y="Fsp3", order=order, hue="hsub",
                palette="Set2", legend=False, ax=ax)
    ax.set_title("Molecular saturation (Fsp3) by halogen subgroup")
    ax.set_xlabel("Halogen subgroup")
    fig.tight_layout(); save(fig, "fsp3_halogen_subgroups.png")


# ===========================================================================
# 10. PCA scree + score plot
# ===========================================================================
def fig_pca():
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    Z = StandardScaler().fit_transform(df[DESC15].fillna(df[DESC15].median()))
    pca = PCA().fit(Z); ev = pca.explained_variance_ratio_ * 100; sc = pca.transform(Z)
    fig, ax = plt.subplots(1, 2, figsize=(14, 5.5))
    ax[0].plot(range(1, 16), ev, "o-", color="#4C72B0", label="individual")
    ax[0].plot(range(1, 16), np.cumsum(ev), "s--", color="#C44E52", label="cumulative")
    ax[0].axhline(80, color="gray", ls=":", lw=1)
    ax[0].set_xlabel("Principal component"); ax[0].set_ylabel("Explained variance (%)")
    ax[0].set_title("Scree plot"); ax[0].legend()
    s = ax[1].scatter(sc[:, 0], sc[:, 1], c=df["max_phase"], cmap="viridis", s=14, alpha=0.6)
    ax[1].set_xlabel(f"PC1 ({ev[0]:.1f}%)"); ax[1].set_ylabel(f"PC2 ({ev[1]:.1f}%)")
    ax[1].set_title("PCA score plot (coloured by clinical phase)")
    fig.colorbar(s, ax=ax[1], label="max_phase")
    fig.tight_layout(); save(fig, "pca_scree_scores.png")


# ===========================================================================
# 11. LogP vs LogS by halogenation
# ===========================================================================
def fig_logp_logs():
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.5), sharex=True, sharey=True)
    for a, grp, c in zip(ax, ["Halogenated", "Non-halogenated"], ["#C44E52", "#4C9FC4"]):
        d = df[df["hal"] == grp]
        sns.regplot(data=d, x="LogP", y="LogS", ax=a,
                    scatter_kws={"s": 10, "alpha": 0.3, "color": c},
                    line_kws={"color": "black", "ls": "--"})
        a.set_title(f"{grp} (n={len(d)})  r={d['LogP'].corr(d['LogS']):.3f}")
    fig.tight_layout(); save(fig, "logp_logs_by_halogen.png")


# ===========================================================================
# 12. 5-HT2A repeated-split benchmark (needs results_data/tab_repeated_raw.csv)
# ===========================================================================
def fig_benchmark():
    p = os.path.join(RES, "tab_repeated_raw.csv")
    if not os.path.exists(p):
        print("skip benchmark (missing", p, ")"); return
    raw = pd.read_csv(p); raw["combo"] = raw["feature"] + "\n" + raw["model"]
    order = raw.groupby("combo")["R2"].mean().sort_values(ascending=False).index.tolist()
    data = [raw.loc[raw.combo == c, "R2"].values for c in order]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    bp = ax.boxplot(data, patch_artist=True, widths=0.6, showfliers=False)
    for patch, c in zip(bp["boxes"], plt.cm.viridis(np.linspace(0.15, 0.85, len(order)))):
        patch.set_facecolor(c); patch.set_alpha(0.75)
    for med in bp["medians"]:
        med.set_color("black"); med.set_linewidth(1.5)
    rng = np.random.default_rng(0)
    for i, d in enumerate(data):
        ax.scatter(np.full_like(d, i + 1) + rng.uniform(-0.12, 0.12, len(d)),
                   d, s=12, color="black", alpha=0.35, zorder=3)
    ax.axhline(0, color="red", ls="--", lw=1, alpha=0.7)
    ax.set_xticklabels(order); ax.set_ylabel("Held-out test R\u00b2")
    ax.set_title("5-HT2A QSAR: held-out R\u00b2 across 25 randomised scaffold splits")
    ax.set_ylim(-2.2, 0.75)
    fig.tight_layout(); save(fig, "qsar_benchmark.png")


# ===========================================================================
# 13. Multi-target panel generalisation
# ===========================================================================
def fig_panel():
    pb = os.path.join(RES, "panel_results.csv"); py = os.path.join(RES, "panel_yrand2.csv")
    if not (os.path.exists(pb) and os.path.exists(py)):
        print("skip panel (missing result CSVs)"); return
    b = pd.read_csv(pb).merge(pd.read_csv(py)[["target", "p"]], on="target")
    b = b.sort_values("mean_R2", ascending=False).reset_index(drop=True)
    b["short"] = (b["target"].str.replace("Serotonin ", "5-HT").str.replace("Adrenergic ", "")
                  .str.replace("Dopamine ", "").str.replace("Muscarinic ", "")
                  .str.replace("Adenosine ", "").str.replace("Opiate ", ""))
    fig, ax = plt.subplots(figsize=(9, 5)); yp = np.arange(len(b))[::-1]
    err = np.array([b["mean_R2"] - b["R2_lo"], b["R2_hi"] - b["mean_R2"]])
    cols = ["#2c7fb8" if p < 0.05 else ("#7fcdbb" if p < 0.12 else "#d9d9d9") for p in b["p"]]
    ax.errorbar(b["mean_R2"], yp, xerr=err, fmt="o", ms=9, capsize=4, lw=1.5,
                ecolor="gray", mfc="white", mec="gray", zorder=2)
    for i in range(len(b)):
        ax.scatter(b["mean_R2"][i], yp[i], s=90, color=cols[i], zorder=3, edgecolor="black", lw=0.6)
    ax.axvline(0, color="red", ls="--", lw=1, alpha=0.7)
    ax.set_yticks(yp); ax.set_yticklabels([f"{r['short']} (n={r['n']})" for _, r in b.iterrows()])
    ax.set_xlabel("Mean held-out R\u00b2 (25 scaffold splits, 95% CI)")
    ax.set_title("Multi-target generalisation of the ECFP4-Random Forest model")
    ax.set_xlim(-0.5, 0.75)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color="#2c7fb8", label="y-rand p<0.05"),
                       Patch(color="#7fcdbb", label="0.05<=p<0.12"),
                       Patch(color="#d9d9d9", label="n.s.")], loc="lower right")
    fig.tight_layout(); save(fig, "panel_generalisation.png")


if __name__ == "__main__":
    fig_family(); fig_violins(); fig_trend(); fig_heatmaps()
    fig_pos_scatter(); fig_neg_scatter(); fig_halogen_dist(); fig_phase_hal()
    fig_fsp3(); fig_pca(); fig_logp_logs(); fig_benchmark(); fig_panel()
    print("\nAll figures written to ./%s/  (sans-serif: %s)" % (OUT, SANS[0]))
