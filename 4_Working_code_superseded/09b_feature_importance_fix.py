# =====================================================================
#  ROBUST replacement for the feature-importance + predicted-vs-observed
#  figures.  Paste as a NEW CELL at the bottom of 08_full_model.ipynb
#  (after Cells A/B). Reuses feat, sets, rf, boost, scaffold_split, r2_score.
#  Does NOT use DrawMorganBits (that's what crashed) — draws each ECFP4
#  bit environment by highlighting it on an example molecule, which works
#  on every RDKit version.
# =====================================================================
import numpy as np, matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D
from sklearn.metrics import r2_score

# ---------- 1) Fig 3.20 : 12 most informative ECFP4 substructures (5-HT2A) ----------
try:
    t = '5-HT2A'; X, y, scaf = feat[t]
    rfm = rf().fit(X, y)
    imp = rfm.feature_importances_[:2048]            # ECFP4 bits are the first 2048 columns
    top = np.argsort(imp)[::-1][:12]
    smis = list(sets[t].parent_smiles)

    def bit_example(bid):
        for s in smis:
            m = Chem.MolFromSmiles(str(s))
            if m is None:
                continue
            bi = {}
            AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048, bitInfo=bi)
            if bid in bi:
                return m, bi
        return None, None

    def draw_env(m, bid, bi, size=(330, 250)):
        atom_id, radius = bi[bid][0]                  # (central atom, radius) of the bit
        if radius > 0:
            env = Chem.FindAtomEnvironmentOfRadiusN(m, radius, atom_id)
            atoms = {atom_id}
            for b in env:
                bd = m.GetBondWithIdx(b); atoms.add(bd.GetBeginAtomIdx()); atoms.add(bd.GetEndAtomIdx())
            bonds = list(env)
        else:
            atoms, bonds = {atom_id}, []
        d = rdMolDraw2D.MolDraw2DCairo(*size)
        rdMolDraw2D.PrepareAndDrawMolecule(d, m, highlightAtoms=list(atoms), highlightBonds=bonds)
        d.FinishDrawing()
        return Image.open(BytesIO(d.GetDrawingText()))

    fig, axes = plt.subplots(3, 4, figsize=(12, 8))
    for ax, b in zip(axes.flat, top):
        m, bi = bit_example(int(b))
        if m is not None:
            ax.imshow(draw_env(m, int(b), bi))
        ax.set_title(f"bit {b}  (imp {imp[b]:.3f})", fontsize=11)
        ax.axis('off')
    fig.tight_layout()
    fig.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
    plt.show()
    print('OK  -> saved feature_importance.png')
except Exception as e:
    print('feature_importance FAILED:', repr(e))

# ---------- 2) Predicted vs observed (scaffold split seed 0, XGBoost) ----------
try:
    fig, axs = plt.subplots(1, 2, figsize=(11, 5))
    for ax, t in zip(axs, feat):
        X, y, scaf = feat[t]; tr, te = scaffold_split(scaf, len(y), 0)
        pr = boost().fit(X[tr], y[tr]).predict(X[te])
        ax.scatter(y[te], pr, s=8, alpha=0.3, color='#4C72B0')
        lo, hi = min(y[te].min(), pr.min()), max(y[te].max(), pr.max())
        ax.plot([lo, hi], [lo, hi], 'r--', lw=1)
        ax.set_xlabel('observed pKi'); ax.set_ylabel('predicted pKi')
        ax.set_title(f'{t}   (scaffold-split R² = {r2_score(y[te], pr):.2f})')
    fig.tight_layout(); fig.savefig('predicted_vs_observed.png', dpi=300)
    plt.show()
    print('OK  -> saved predicted_vs_observed.png')
except Exception as e:
    print('predicted_vs_observed FAILED:', repr(e))

print('\nUpload feature_importance.png and predicted_vs_observed.png to the chat.')
