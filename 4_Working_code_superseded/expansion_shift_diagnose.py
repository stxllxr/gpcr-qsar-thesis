# =====================================================================
#  WHAT DRIVES THE CLINICAL / PRECLINICAL OFFSET?
#  Paste in 10_additions.ipynb after pca_clinical_vs_preclinical.py.
#
#  The PCA showed 84-87% coverage but a centroid gap of 0.70 and 1.08 SD.
#  A gap without an explanation is a liability in a defense. This finds
#  which descriptors actually differ, so the offset can be stated as a
#  chemical fact rather than an unexplained number.
#
#  Uses RDKit on the SMILES so the descriptors are the interpretable ones
#  from Part One, not the ~200 normalised DescriptaStorus columns.
# =====================================================================
import numpy as np, pandas as pd, os
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors
RDLogger.DisableLog('rdApp.*')

LOCKED = 'data/curated_15desc.csv' if os.path.exists('data/curated_15desc.csv') else 'curated_15desc.csv'
KEY = {'5-HT2A': '5-HT2A', 'Dopamine D3': 'D3'}
locked = pd.read_csv(LOCKED)

DESC = {
    'MW':        Descriptors.MolWt,
    'LogP':      Crippen.MolLogP,
    'TPSA':      Descriptors.TPSA,
    'HBA':       Descriptors.NumHAcceptors,
    'HBD':       Descriptors.NumHDonors,
    'RotB':      Descriptors.NumRotatableBonds,
    'HAC':       Descriptors.HeavyAtomCount,
    'RingCount': Descriptors.RingCount,
    'Fsp3':      rdMolDescriptors.CalcFractionCSP3,
    'Halogens':  lambda m: sum(1 for a in m.GetAtoms()
                               if a.GetSymbol() in ('F', 'Cl', 'Br', 'I')),
}


def cohens_d(a, b):
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    return (a.mean() - b.mean()) / sp if sp > 0 else 0.0


for t in feat:
    s = sets[t]
    clin_ids = set(locked[locked.target.str.contains(KEY[t], case=False)]
                   .molecule_chembl_id.unique())
    is_clin = s.molecule_chembl_id.isin(clin_ids).values

    mols = [Chem.MolFromSmiles(str(x)) for x in s.parent_smiles]
    ok = np.array([m is not None for m in mols])
    tab = pd.DataFrame({k: [f(m) if m is not None else np.nan for m in mols]
                        for k, f in DESC.items()})
    tab['clinical'] = is_clin
    tab = tab[ok]

    rows = []
    for k in DESC:
        a = tab.loc[~tab.clinical, k].dropna().values      # preclinical
        b = tab.loc[tab.clinical, k].dropna().values       # clinical
        rows.append((k, b.mean(), a.mean(), a.mean() - b.mean(), cohens_d(a, b)))
    r = pd.DataFrame(rows, columns=['descriptor', 'clinical', 'preclinical',
                                    'diff', 'cohens_d'])
    r['abs_d'] = r.cohens_d.abs()
    r = r.sort_values('abs_d', ascending=False)

    print(f'\n=== {t}  (clinical n={int(is_clin.sum())}, '
          f'preclinical n={int((~is_clin).sum())}) ===')
    print('preclinical minus clinical, sorted by effect size')
    print(r[['descriptor', 'clinical', 'preclinical', 'diff', 'cohens_d']]
          .to_string(index=False, float_format=lambda v: f'{v:8.2f}'))
    big = r[r.abs_d >= 0.5].descriptor.tolist()
    print('  |d| >= 0.5 (medium or larger):', big if big else 'none')

print("""
Reading it
  Cohen's d: 0.2 small, 0.5 medium, 0.8 large. A positive value means the
  preclinical compounds score HIGHER on that descriptor.

  If the offset is carried by MW / HAC / LogP being higher in the preclinical
  set, that is the expected and easily explained pattern: clinical compounds
  have already survived property optimisation and developability filtering,
  while preclinical lead-optimisation series are typically larger and more
  lipophilic. That is a chemical statement you can make, not an anomaly.
""")
