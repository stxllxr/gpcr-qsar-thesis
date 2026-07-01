from chembl_webresource_client.new_client import new_client
import pandas as pd
import numpy as np
import tqdm


MAX_MOLECULAR_WEIGHT = 700
CLINICAL_PHASES = [1, 2, 3, 4]


def get_target_info(uniprot_id):

    target = new_client.target # type: ignore
    target_results = target.filter(
        target_components__accession=uniprot_id,
        organism="Homo sapiens"
    ).only("organism", "pref_name", "target_chembl_id", "target_type")
    
    df = pd.DataFrame.from_records(target_results)
    if len(df) == 0:
        raise ValueError(f"No Homo sapiens target found for UniProt ID: {uniprot_id}")
    
    return df.iloc[0]


def get_bioactivities(chembl_id, activity_type="Ki"):

    bioactivities = new_client.activity # type: ignore
    
    toi_bioactivities = bioactivities.filter(
        target_chembl_id=chembl_id,
        type=activity_type,
        relation="=",
        assay_type="B"
    ).only(
        "molecule_chembl_id",
        "standard_type",
        "standard_value",
        "standard_units",
        "relation",
        "assay_type",
        "pchembl_value"
    )
    
    print(f"Found {len(toi_bioactivities)} binding (B) bioactivities for {chembl_id}")
    
    # Convert to DataFrame
    df = pd.DataFrame.from_records(toi_bioactivities)
    
    if len(df) == 0:
        print(f"Warning: No bioactivities found for {chembl_id}")
        return df

    # data cleaning
    df.drop(columns=["standard_type", "relation"], axis=1, inplace=True, errors='ignore')
    df.rename(columns={"standard_value": activity_type}, inplace=True)
    df = df.astype({activity_type: 'float64', 'pchembl_value': 'float64'})
    
    
    # Filter for non-NA pchembl_value
    initial_count = len(df)
    df = df[df["pchembl_value"].notna()].copy()
    print(f"Removed {initial_count - len(df)} entries with NA pchembl_value")

    return df


def get_compound_properties(molecule_ids, show_progress=True, batch_size=50):

    maxphase_storage = []
    
    # Process in batches
    total_batches = (len(molecule_ids) + batch_size - 1) // batch_size
    
    if show_progress:
        print(f"Fetching properties for {len(molecule_ids)} molecules in {total_batches} batches...")
    
    for i in tqdm.tqdm(range(0, len(molecule_ids), batch_size), disable=not show_progress):
        batch = molecule_ids[i:i + batch_size]
        try:
            # Fetch batch of molecules
            data = new_client.molecule.filter( # type: ignore
                molecule_chembl_id__in=batch
            ).only("molecule_chembl_id", "max_phase", "molecule_properties", "molecule_structures")
            maxphase_storage.extend(list(data))
        except Exception as e:
            print(f"Error fetching batch {i//batch_size + 1}: {e}")
            # Fall back to individual fetching for this batch
            for mol in batch:
                try:
                    data = new_client.molecule.filter(molecule_chembl_id=mol).only( # type: ignore
                        "molecule_chembl_id", "max_phase", "molecule_properties", "molecule_structures"
                    )
                    maxphase_storage.extend(list(data))
                except Exception as e2:
                    print(f"Error fetching {mol}: {e2}")
    
    compounds_df = pd.DataFrame.from_records(maxphase_storage)
    
    return compounds_df


def filter_clinical_compounds(compounds_df, max_mw=MAX_MOLECULAR_WEIGHT, 
                              clinical_phases=CLINICAL_PHASES):
    
    df = compounds_df.copy()
    
    # Convert max_phase to numeric
    df["max_phase"] = pd.to_numeric(df["max_phase"], errors="coerce")
    
    # Extract molecular weight
    def get_mw(mp):
        if isinstance(mp, dict):
            return mp.get("full_mwt") or mp.get("mw_freebase")
        return None
    
    df["mol_weight"] = df["molecule_properties"].apply(get_mw)
    df["mol_weight"] = pd.to_numeric(df["mol_weight"], errors="coerce")
    
    # Extract canonical SMILES
    def get_smiles(ms):
        if isinstance(ms, dict):
            return ms.get("canonical_smiles")
        return None
    
    df["canonical_smiles"] = df["molecule_structures"].apply(get_smiles)
    
    # Apply filters

    filtered_df = df[df["max_phase"].isin(clinical_phases)].copy()
    filtered_df = filtered_df[
        filtered_df["mol_weight"].notna() & 
        (filtered_df["mol_weight"] < max_mw)
    ]
    
    # Drop molecule_properties and molecule_structures columns (no longer needed)
    # NOTE: Do not use inplace=True when assigning the result, it returns None
    filtered_df = filtered_df.drop(columns=["molecule_properties", "molecule_structures"], errors='ignore')

    return filtered_df


def finalize_dataset(df):
    """
    Clean up and finalize the dataset columns for better usability.
    
    Operations:
    - Rename 'canonical_smiles' to 'smiles'
    - Remove 'standard_units' column (unit information)
    - Remove 'standard_type' column (redundant type information like 'Ki')
    - Remove 'assay_type' column (all are 'B' for binding)
    - Remove 'Ki' column (non-converted raw activity value)
    
    Parameters:
    -----------
    df : pd.DataFrame
        The merged dataset to finalize
        
    Returns:
    --------
    pd.DataFrame
        The finalized dataset with cleaned columns
    """
    if df.empty:
        return df
    
    final_df = df.copy()
    
    # Rename canonical_smiles to smiles
    if 'canonical_smiles' in final_df.columns:
        final_df.rename(columns={'canonical_smiles': 'smiles'}, inplace=True)
    
    # Remove unwanted columns
    columns_to_remove = ['units', 'value', 'assay_type','type']
    final_df = final_df.drop(columns=columns_to_remove, errors='ignore')
    
    return final_df


def fetch_target_dataset(uniprot_id, target_name, activity_type="Ki", 
                        save_csv=True, output_filename=None):

    print(f"\n{'='*60}")
    print(f"Fetching data for {target_name}")
    print(f"{'='*60}\n")
    
    # Step 1: Get target info
    print("Step 1: Fetching target information...")
    target_info = get_target_info(uniprot_id)
    chembl_id = target_info.target_chembl_id
    print(f"ChEMBL ID for {target_name}: {chembl_id}\n")
    
    # Step 2: Get bioactivities
    print("Step 2: Fetching bioactivities...")
    bioactivities_df = get_bioactivities(chembl_id, activity_type)
    
    if len(bioactivities_df) == 0:
        print(f"No bioactivities found for {target_name}. Stopping.")
        return pd.DataFrame()
    
    # Step 3: Get compound properties
    print("\nStep 3: Fetching compound properties...")
    molecule_ids = bioactivities_df["molecule_chembl_id"].unique().tolist()
    compounds_df = get_compound_properties(molecule_ids)
    
    # Step 4: Filter by clinical phase and molecular weight
    print("\nStep 4: Filtering compounds...")
    filtered_compounds = filter_clinical_compounds(compounds_df)
    
    # Defensive check before merge
    if not isinstance(filtered_compounds, pd.DataFrame) or filtered_compounds.empty:
        print("No compounds left after filtering. Stopping before merge.")
        return pd.DataFrame()

    # Step 5: Merge datasets
    print("\nStep 5: Merging bioactivities with compound properties...")
    merged_df = pd.merge(
        bioactivities_df,
        filtered_compounds, # type: ignore
        on="molecule_chembl_id",
        how="inner"
    )
    
    # Step 6: Finalize dataset (clean up columns)
    print("\nStep 6: Finalizing dataset...")
    final_df = finalize_dataset(merged_df)
    
    print(f"Final dataset shape: {final_df.shape}")
    print(f"Final columns: {list(final_df.columns)}")
    
    # Step 7: Save to CSV
    if save_csv:
        if output_filename is None:
            output_filename = f"{target_name.lower().replace(' ', '_')}_final_dataset.csv"
        
        final_df.to_csv(output_filename, index=False)
        print(f"\nDataset saved to: {output_filename}")
    
    print(f"\n{'='*60}\n")
    
    return final_df