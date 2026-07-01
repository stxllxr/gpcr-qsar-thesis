"""
Baseline comparison for the 5-HT2A QSAR case study.
Reproduces ECFP4-RF and adds the two missing baselines:
  - 1-NN Tanimoto read-across (does naive similarity match the RF?)
  - PLS and properly-regularised Ridge on a high-dim 2D-descriptor panel
    (is the reported Ridge 'failure' really under-regularisation?)
Protocol mirrors the thesis: 80/20 Bemis-Murcko scaffold split, 25 seeds,
fold-internal median imputation + standardisation for descriptor models.
"""
import numpy as np, pandas as pd
from rdkit import Chem, DataStructs
from rdkit import RDLogger; RDLogger.DisableLog("rdApp.*")
from rdkit.Chem import AllChem, Descriptors
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit.ML.Descriptors import MoleculeDescriptors
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.cross_decomposition import PLSRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import r2_score, root_mean_squared_error as rmse
import warnings; warnings.filterwarnings("ignore")

df = pd.read_csv("curated_15desc.csv")
df = df[df.target.astype(str).str.contains("5-HT2A", case=False)].copy()
df = df.drop_duplicates("molecule_chembl_id").reset_index(drop=True)
mols = [Chem.MolFromSmiles(s) for s in df.parent_smiles]
keep = [i for i,m in enumerate(mols) if m is not None]
df = df.iloc[keep].reset_index(drop=True); mols = [mols[i] for i in keep]
y = df.pKi.values.astype(float)
N = len(df); print(f"5-HT2A modelling set: n={N}")

# ---- ECFP4 (stereo-blind, radius 2, 2048 bit) ----
fps = [AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048) for m in mols]
X_ecfp = np.zeros((N, 2048), dtype=int)
for i,fp in enumerate(fps):
    DataStructs.ConvertToNumpyArray(fp, X_ecfp[i])

# ---- RDKit 2D descriptor panel (~210 descriptors; the collinear 2D space) ----
names = [n for n,_ in Descriptors._descList]
calc = MoleculeDescriptors.MolecularDescriptorCalculator(names)
X_desc = np.array([list(calc.CalcDescriptors(m)) for m in mols], dtype=float)
X_desc[~np.isfinite(X_desc)] = np.nan
print(f"2D descriptor panel: {X_desc.shape[1]} descriptors")

# ---- Bemis-Murcko scaffolds ----
def scaffold(m):
    try: return Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(m))
    except Exception: return ""
scaf = np.array([scaffold(m) for m in mols])
print(f"distinct scaffolds: {len(set(scaf))}")

def scaffold_split(seed, test_frac=0.20):
    rng = np.random.RandomState(seed)
    groups = {}
    for i,s in enumerate(scaf): groups.setdefault(s, []).append(i)
    keys = list(groups); rng.shuffle(keys)
    test, n_test_target = [], int(round(test_frac*N))
    for k in keys:
        if len(test) >= n_test_target: break
        test += groups[k]
    test = set(test); tr = [i for i in range(N) if i not in test]; te = sorted(test)
    assert not (set(scaf[tr]) & set(scaf[te])), "scaffold leakage!"
    return np.array(tr), np.array(te)

def tanimoto_1nn(tr, te):
    pred = []
    for j in te:
        sims = DataStructs.BulkTanimotoSimilarity(fps[j], [fps[i] for i in tr])
        pred.append(y[tr][int(np.argmax(sims))])
    return np.array(pred)

def desc_model(model, tr, te):
    imp = SimpleImputer(strategy="median").fit(X_desc[tr])
    Xtr, Xte = imp.transform(X_desc[tr]), imp.transform(X_desc[te])
    sc = StandardScaler().fit(Xtr)
    Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
    model.fit(Xtr, y[tr])
    return model.predict(Xte).ravel()

rows = []
for seed in range(25):
    tr, te = scaffold_split(seed)
    yte = y[te]
    # A. ECFP4 + RF (reproduce headline)
    rf = RandomForestRegressor(n_estimators=300, random_state=seed, n_jobs=-1)
    rf.fit(X_ecfp[tr], y[tr]); p = rf.predict(X_ecfp[te])
    rows.append(("ECFP4+RF (headline)", seed, r2_score(yte,p), rmse(yte,p)))
    # B. ECFP4 + 1-NN read-across
    p = tanimoto_1nn(tr, te)
    rows.append(("ECFP4 1-NN read-across", seed, r2_score(yte,p), rmse(yte,p)))
    # C. 2D + Ridge alpha=1.0  (thesis config)
    p = desc_model(Ridge(alpha=1.0), tr, te)
    rows.append(("2D + Ridge (alpha=1.0)", seed, r2_score(yte,p), rmse(yte,p)))
    # D. 2D + RidgeCV (properly regularised)
    p = desc_model(RidgeCV(alphas=np.logspace(-1,4,20)), tr, te)
    rows.append(("2D + Ridge (CV alpha)", seed, r2_score(yte,p), rmse(yte,p)))
    # E. 2D + PLS (latent-variable linear baseline)
    p = desc_model(PLSRegression(n_components=6), tr, te)
    rows.append(("2D + PLS (6 comp)", seed, r2_score(yte,p), rmse(yte,p)))

res = pd.DataFrame(rows, columns=["model","seed","R2","RMSE"])
summary = res.groupby("model").agg(
    mean_R2=("R2","mean"), median_R2=("R2","median"),
    R2_lo=("R2", lambda s: np.percentile(s,2.5)),
    R2_hi=("R2", lambda s: np.percentile(s,97.5)),
    frac_pos=("R2", lambda s: (s>0).mean()),
    mean_RMSE=("RMSE","mean")).round(3)
order = ["ECFP4+RF (headline)","ECFP4 1-NN read-across","2D + PLS (6 comp)",
         "2D + Ridge (CV alpha)","2D + Ridge (alpha=1.0)"]
summary = summary.loc[order]
pd.set_option("display.width",160)
print("\n==== 25-split scaffold benchmark (5-HT2A) ====")
print(summary.to_string())
summary.to_csv("results_data/baseline_comparison.csv")
print("\nsaved results_data/baseline_comparison.csv")
