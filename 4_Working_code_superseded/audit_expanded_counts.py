#!/usr/bin/env python3
"""
Audit the expanded-ML dataset construction for 5-HT2A and Dopamine D3.

Prints the EXACT compound count at every pipeline step, from the raw ChEMBL Ki
fetch down to the final modelling set. This reproduces the pipeline of
06_expanded_models_eqKi.ipynb (cells 4/6/8) with instrumentation added, so you
can show precisely where "a few thousand raw measurements" becomes "~1,100
unique molecules per target".

USAGE (run where ChEMBL is reachable, i.e. your machine, not the sandbox):
    cd <folder containing data/curated_15desc.csv>
    python audit_expanded_counts.py

NOTE: this hits the LIVE ChEMBL API, which is now v37. The thesis is pinned to
v36, so the raw record counts will differ by a handful of rows from the locked
numbers -- the STRUCTURE of the funnel (records -> unique molecules) is the point.
"""
import os, time, numpy as np, pandas as pd
from rdkit import Chem, RDLogger; RDLogger.DisableLog('rdApp.*')
from rdkit.Chem import Descriptors
from rdkit.Chem.SaltRemover import SaltRemover
from chembl_webresource_client.new_client import new_client
from chembl_webresource_client.settings import Settings
Settings.Instance().TIMEOUT = 60
Settings.Instance().TOTAL_RETRIES = 10
Settings.Instance().MAX_LIMIT = 1000

TARGETS = {'5-HT2A': 'P28223', 'Dopamine D3': 'P35462'}
LOCKED_CSV = 'data/curated_15desc.csv' if os.path.exists('data/curated_15desc.csv') else 'curated_15desc.csv'
target_api, activity_api, molecule_api = new_client.target, new_client.activity, new_client.molecule


def _retry(call, what, tries=8):
    for k in range(tries):
        try:
            return call()
        except Exception as e:
            print(f"    {what}: {type(e).__name__} -> retry {k+1}/{tries}")
            time.sleep(5 * (k + 1))
    raise RuntimeError(f"{what} failed")


def resolve(acc):
    h = _retry(lambda: list(target_api.filter(
        target_components__accession=acc, target_type='SINGLE PROTEIN',
        organism='Homo sapiens').only(['target_chembl_id'])), f"resolve {acc}")
    return h[0]['target_chembl_id'] if h else None


sr = SaltRemover()
def parent(s):
    m = Chem.MolFromSmiles(str(s)) if isinstance(s, str) else None
    if m is None:
        return None
    p = sr.StripMol(m, dontRemoveEverything=True)
    if p is None or p.GetNumAtoms() == 0:
        fr = Chem.GetMolFrags(m, asMols=True)
        p = max(fr, key=lambda x: x.GetNumAtoms()) if fr else m
    return p


pep = Chem.MolFromSmarts('[NX3][CX4][CX3](=O)[NX3][CX4][CX3](=O)')
def landrum(g):                                    # highest pKi per molecule, artefacts removed
    v = g['pKi'].round(2)
    v = v[~v.duplicated(keep='first')]             # drop exact-duplicate copies
    v = [x for x in v if not any(abs(x - o - 3.0) < 1e-6 or abs(x - o + 3.0) < 1e-6 for o in v)]
    return max(v) if v else np.nan                 # drop 3.0-log unit errors


locked = pd.read_csv(LOCKED_CSV)
def clinical_ids(target):
    key = target.split()[-1] if 'Dopamine' in target else target
    return set(locked[locked.target.str.contains(key, case=False)].molecule_chembl_id)


for name, acc in TARGETS.items():
    tid = resolve(acc)
    print(f"\n===== {name}  ({tid}) =====")
    funnel = []

    q_all = activity_api.filter(target_chembl_id=tid, standard_type='Ki', assay_type='B', target_organism='Homo sapiens')
    q_eq = activity_api.filter(target_chembl_id=tid, standard_type='Ki', assay_type='B',
                               standard_relation='=', standard_units='nM', target_organism='Homo sapiens')
    n_all = _retry(lambda: len(q_all), "count all")
    n_eq = _retry(lambda: len(q_eq), "count eq")
    funnel.append(("raw Ki(B) records, all relations", n_all))
    funnel.append(("exact '=' Ki in nM  [USED]", n_eq))
    funnel.append(("censored (>/<) or non-nM, EXCLUDED", n_all - n_eq))

    raw = pd.DataFrame(list(q_eq.only(['molecule_chembl_id', 'canonical_smiles', 'standard_value'])))
    raw['standard_value'] = pd.to_numeric(raw['standard_value'], errors='coerce')
    raw = raw[raw['standard_value'] > 0].copy()
    raw['pKi'] = 9.0 - np.log10(raw['standard_value'])

    ids = raw['molecule_chembl_id'].dropna().unique().tolist()
    ph = {}
    for i in range(0, len(ids), 200):
        recs = _retry(lambda: list(molecule_api.filter(molecule_chembl_id__in=ids[i:i + 200])
                                   .only(['molecule_chembl_id', 'max_phase'])), f"max_phase {i}")
        for m in recs:
            ph[m['molecule_chembl_id']] = m['max_phase']
    raw['max_phase'] = pd.to_numeric(raw['molecule_chembl_id'].map(ph), errors='coerce')

    pre = raw[~raw['max_phase'].isin([1, 2, 3, 4])].copy()          # preclinical = max_phase 0/null
    funnel.append(("preclinical records (max_phase 0/null)", len(pre)))
    funnel.append(("  unique preclinical molecules (raw)", pre.molecule_chembl_id.nunique()))

    d = pre.dropna(subset=['pKi']).copy()
    d['mol'] = d['canonical_smiles'].apply(parent)
    d = d[d['mol'].notna()]
    funnel.append(("after salt-strip / parse (records)", len(d)))
    d = d[d['mol'].apply(lambda m: Descriptors.MolWt(m)) < 700]
    funnel.append(("after MW < 700 (records)", len(d)))
    d = d[~d['mol'].apply(lambda m: m.HasSubstructMatch(pep))]
    funnel.append(("after peptide removal (records)", len(d)))
    d['parent_smiles'] = d['mol'].apply(Chem.MolToSmiles)

    agg = d.groupby('molecule_chembl_id').apply(landrum).dropna()
    funnel.append(("unique preclinical molecules (Landrum + dedup)", len(agg)))

    clin = clinical_ids(name)
    new_pre = [m for m in agg.index if m not in clin]
    funnel.append(("clinical molecules (from locked v36 set)", len(clin)))
    funnel.append(("NEW preclinical added (not already clinical)", len(new_pre)))
    funnel.append(("FINAL modelling set  = clinical + new preclinical", len(clin) + len(new_pre)))

    print(f"  {'step':50s}count")
    print("  " + "-" * 58)
    for k, v in funnel:
        print(f"  {k:50s}{v}")

print("\nThesis (v36) reference:  5-HT2A = 172 + 950 = 1,122   |   D3 = 173 + 982 = 1,155")
