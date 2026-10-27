#!/usr/bin/env python3
"""Reproduce the Cohen's d values hardcoded in make_expansion_fig.py."""
import numpy as np, pandas as pd, warnings, sys
warnings.filterwarnings('ignore')
sys.path.insert(0,'/sessions/sharp-elegant-gauss/mnt/outputs')
from rdkit import Chem, RDLogger; RDLogger.DisableLog('rdApp.*')
from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors
from build_feats import build, locked, KEY

DESC = {'MW':Descriptors.MolWt,'LogP':Crippen.MolLogP,'TPSA':Descriptors.TPSA,
        'HBA':Descriptors.NumHAcceptors,'HBD':Descriptors.NumHDonors,
        'RotB':Descriptors.NumRotatableBonds,'HAC':Descriptors.HeavyAtomCount,
        'RingCount':Descriptors.RingCount,'Fsp3':rdMolDescriptors.CalcFractionCSP3,
        'Halogens':lambda m: sum(1 for a in m.GetAtoms() if a.GetSymbol() in ('F','Cl','Br','I'))}

def cohens_d(a,b):
    na,nb=len(a),len(b)
    sp=np.sqrt(((na-1)*a.var(ddof=1)+(nb-1)*b.var(ddof=1))/(na+nb-2))
    return (a.mean()-b.mean())/sp if sp>0 else 0.0

HARD = {'HAC':(0.40,0.77),'MW':(0.41,0.72),'RingCount':(0.47,0.66),'HBA':(0.52,0.58),
        'RotB':(0.19,0.56),'TPSA':(0.53,0.26),'Fsp3':(0.39,0.43),'LogP':(-0.01,0.28),
        'Halogens':(0.10,0.22),'HBD':(-0.07,-0.24)}
got={}
for j,t in enumerate(['5-HT2A','Dopamine D3']):
    s=build(t)
    clin=set(locked[locked.target.str.contains(KEY[t],case=False)].molecule_chembl_id.unique())
    is_clin=s.molecule_chembl_id.isin(clin).values
    mols=[Chem.MolFromSmiles(str(x)) for x in s.parent_smiles]
    ok=np.array([m is not None for m in mols])
    tab=pd.DataFrame({k:[f(m) if m is not None else np.nan for m in mols] for k,f in DESC.items()})
    tab['clinical']=is_clin; tab=tab[ok]
    print(f'\n=== {t}  clinical n={int(is_clin.sum())}  preclinical n={int((~is_clin).sum())}')
    for k in DESC:
        a=tab.loc[~tab.clinical,k].dropna().values
        b=tab.loc[tab.clinical,k].dropna().values
        got.setdefault(k,[]).append(round(float(cohens_d(a,b)),2))
print('\n%-10s %-16s %-16s %s'%('desc','in figure','recomputed','match'))
bad=0
for k in HARD:
    h=HARD[k]; g=tuple(got[k])
    m=all(abs(x-y)<=0.02 for x,y in zip(h,g))
    bad+= (not m)
    print('%-10s %-16s %-16s %s'%(k,h,g,'OK' if m else '*** MISMATCH'))
print('\nmismatches:',bad)
