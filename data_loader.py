#!/usr/bin/env python3
"""
Data preprocessing module for PPMI Parkinson's Disease Biomarker Dashboard
Handles loading, cleaning, and merging of biomarker, clinical, and genetic data
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Define the base path
# BASE_PATH = "/Users/georgeng/Library/CloudStorage/GoogleDrive-2018076@teacher.hkuspace.hku.hk/My Drive/Courses/Duke-NUS MD/Research Articles/PD Related/Datasets/PPMI Various Datasets"

# Define URLs for data files hosted on GitHub Releases
BASE_URL = "https://github.com/just4jc/ppmi-biomarker-dashboard/releases/download/v1.0.0"

DATA_URLS = {
    "biomarker": f"{BASE_URL}/Current_Biospecimen_Analysis_Results_18Sep2025.csv",
    "demographics": f"{BASE_URL}/Demographics_18Sep2025.csv",
    "age": f"{BASE_URL}/Age_at_visit_18Sep2025.csv",
    "clinical_dx": f"{BASE_URL}/Clinical_Diagnosis_18Sep2025.csv",
    "updrs": f"{BASE_URL}/MDS-UPDRS_Part_III_18Sep2025.csv",
    "genetic": f"{BASE_URL}/Genetic%20Data%20-%20Consensus%20APOE%20Genotype%20and%20Pathogenic%20Variants%20for%20LRRK2,%20GBA,%20VPS35,%20SNCA,%20PRKN,%20PARK7,%20and%20PINK1.csv"
}

def _read_data(local_path, url):
    """Try to read from local path, fall back to URL."""
    try:
        # Prefer local file if it exists
        if os.path.exists(local_path):
            print(f"Reading data from local file: {local_path}")
            return pd.read_csv(local_path, low_memory=False)
        else:
            # Fallback to URL
            print(f"Local file not found. Reading data from URL: {url}")
            return pd.read_csv(url, low_memory=False)
    except Exception as e:
        print(f"Error reading data for {os.path.basename(local_path)}: {e}")
        # Raise a more informative error for deployment
        raise FileNotFoundError(
            f"Could not load data from local path ({local_path}) or URL ({url}). "
            "Ensure data files are in the correct local directory or accessible via the URL."
        ) from e

class PPMIDataLoader:
    """Class to handle loading and preprocessing of PPMI data"""
    
    def __init__(self, base_path='.'):
        self.base_path = base_path
        self.biomarker_data = None
        self.demographics = None
        self.clinical_data = None
        self.genetic_data = None
        self.age_data = None
        self.updrs_data = None
        self.merged_data = None
        
    def load_biomarker_data(self):
        """Load and preprocess biomarker analysis results"""
        print("Loading biomarker data...")
        
        local_path = os.path.join(self.base_path, "biospecimen_analysis_results", "Current_Biospecimen_Analysis_Results_18Sep2025.csv")
        self.biomarker_data = _read_data(local_path, DATA_URLS["biomarker"])
        
        # Filter for key biomarkers and focus projects
        pd_pros_proteins = ['NEFL', 'TIMP1', 'A2M', 'VCAM1', 'GFAP', 'IL6R', 'ENRAGE', 'VEGFA', 'DCN', 'MMP2', 'GP130', 'FGF21', 'UCHL1', 'ICAM1']
        biomarker_keywords = ['synuclein', 'tau', 'p-tau', 'ptau', 'alpha', 'aSyn', 'amyloid', 'abeta'] + pd_pros_proteins
        focus_projects = [124, 125, 159, 172, 173, 207]
        
        # Focus on key biomarkers OR focus projects
        key_biomarkers = self.biomarker_data[
            (self.biomarker_data['TESTNAME'].str.contains('|'.join(biomarker_keywords), case=False, na=False)) |
            (self.biomarker_data['PROJECTID'].isin(focus_projects))
        ].copy()
        
        # Clean test values - convert to numeric where possible
        key_biomarkers['TESTVALUE_NUMERIC'] = pd.to_numeric(key_biomarkers['TESTVALUE'], errors='coerce')
        
        # Convert run date to datetime
        key_biomarkers['RUNDATE'] = pd.to_datetime(key_biomarkers['RUNDATE'], errors='coerce')
        
        # Create a simplified cohort mapping
        cohort_mapping = {
            'Control': 'HC',
            'PD': 'PD', 
            'Prodromal': 'Prodromal PD',
            'SWEDD': 'SWEDD'
        }
        key_biomarkers['COHORT_SIMPLE'] = key_biomarkers['COHORT'].map(cohort_mapping)
        
        self.biomarker_data = key_biomarkers
        print(f"Loaded {len(self.biomarker_data)} biomarker records for {self.biomarker_data['PATNO'].nunique()} patients")
        
        return self.biomarker_data
    
    def load_clinical_data(self):
        """Load clinical and demographic data"""
        print("Loading clinical and demographic data...")
        
        # Demographics
        local_demo_path = os.path.join(self.base_path, "core_patient_visit_info", "Demographics_18Sep2025.csv")
        self.demographics = _read_data(local_demo_path, DATA_URLS["demographics"])
        
        # Age at visit
        local_age_path = os.path.join(self.base_path, "core_patient_visit_info", "Age_at_visit_18Sep2025.csv")
        self.age_data = _read_data(local_age_path, DATA_URLS["age"])
        
        # Clinical diagnosis
        local_clin_path = os.path.join(self.base_path, "clinical_motor_assessments", "medical_history", "Clinical_Diagnosis_18Sep2025.csv")
        self.clinical_data = _read_data(local_clin_path, DATA_URLS["clinical_dx"])
        
        # MDS-UPDRS Part III (motor examination)
        local_updrs_path = os.path.join(self.base_path, "clinical_motor_assessments", "all_motor_mds_updrs", "MDS-UPDRS_Part_III_18Sep2025.csv")
        self.updrs_data = _read_data(local_updrs_path, DATA_URLS["updrs"])
        
        # Process demographics
        self.demographics['BIRTHDT'] = pd.to_datetime(self.demographics['BIRTHDT'], format='%m/%Y', errors='coerce')
        self.demographics['SEX_LABEL'] = self.demographics['SEX'].map({0: 'Female', 1: 'Male'})
        
        print(f"Loaded demographics for {self.demographics['PATNO'].nunique()} patients")
        print(f"Loaded UPDRS data: {len(self.updrs_data)} records")
        
        return self.demographics, self.clinical_data, self.updrs_data
    
    def load_genetic_data(self):
        """Load genetic data"""
        print("Loading genetic data...")
        
        local_path = os.path.join(self.base_path, "genetic_data", "Genetic Data - Consensus APOE Genotype and Pathogenic Variants for LRRK2, GBA, VPS35, SNCA, PRKN, PARK7, and PINK1.csv")
        self.genetic_data = _read_data(local_path, DATA_URLS["genetic"])
        
        # Create risk groups based on pathogenic variants
        self.genetic_data['RISK_GROUP'] = self.genetic_data['PATHVAR_COUNT'].apply(
            lambda x: 'High Risk' if x > 0 else 'Standard Risk'
        )
        
        print(f"Loaded genetic data for {self.genetic_data['PATNO'].nunique()} patients")
        
        return self.genetic_data
    
    def create_merged_dataset(self):
        """Create merged dataset for analysis"""
        print("Creating merged dataset...")
        
        if self.biomarker_data is None:
            self.load_biomarker_data()
        if self.demographics is None:
            self.load_clinical_data()
        if self.genetic_data is None:
            self.load_genetic_data()
        
        # Start with biomarker data as base
        merged = self.biomarker_data.copy()
        
        # Add demographics
        demo_cols = ['PATNO', 'SEX', 'SEX_LABEL', 'BIRTHDT', 'HANDED', 'HISPLAT', 'RAWHITE', 'RABLACK', 'RAASIAN']
        merged = merged.merge(
            self.demographics[demo_cols].drop_duplicates('PATNO'), 
            on='PATNO', 
            how='left',
            suffixes=('', '_demo')
        )
        
        # Add genetic data
        gen_cols = ['PATNO', 'APOE', 'PATHVAR_COUNT', 'LRRK2', 'GBA', 'SNCA', 'RISK_GROUP']
        merged = merged.merge(
            self.genetic_data[gen_cols],
            on='PATNO',
            how='left'
        )
        
        # Calculate age at biomarker collection
        merged['AGE_AT_BIOMARKER'] = (merged['RUNDATE'] - merged['BIRTHDT']).dt.days / 365.25
        
        # Add UPDRS scores if available
        # Group UPDRS by patient and take mean scores
        if len(self.updrs_data) > 0:
            # Check which columns exist in the data
            available_cols = {
                'NP3TOT': 'NP3TOT' if 'NP3TOT' in self.updrs_data.columns else None,
                'NP3BRADY': 'NP3BRADY' if 'NP3BRADY' in self.updrs_data.columns else None,
                'NP3RIGN': 'NP3RIGN' if 'NP3RIGN' in self.updrs_data.columns else None,  # Neck rigidity
                'NP3PTRMR': 'NP3PTRMR' if 'NP3PTRMR' in self.updrs_data.columns else None,  # Postural tremor right
                'NP3PTRML': 'NP3PTRML' if 'NP3PTRML' in self.updrs_data.columns else None,  # Postural tremor left
            }
            
            # Filter to only existing columns
            agg_dict = {col: 'mean' for col in available_cols.values() if col is not None}
            
            if agg_dict:  # Only proceed if we have some columns to aggregate
                updrs_summary = self.updrs_data.groupby('PATNO').agg(agg_dict).reset_index()
                merged = merged.merge(updrs_summary, on='PATNO', how='left')
        
        self.merged_data = merged
        print(f"Created merged dataset with {len(merged)} records for {merged['PATNO'].nunique()} patients")
        
        return self.merged_data
    
    def get_biomarker_summary(self):
        """Get summary of available biomarkers"""
        if self.biomarker_data is None:
            self.load_biomarker_data()
        
        summary = self.biomarker_data.groupby(['TESTNAME', 'COHORT_SIMPLE']).agg({
            'PATNO': 'nunique',
            'TESTVALUE_NUMERIC': ['count', 'mean', 'std']
        }).round(2)
        
        return summary
    
    def get_key_biomarkers_data(self, biomarkers=None):
        """Get data for specific key biomarkers"""
        if self.merged_data is None:
            self.create_merged_dataset()
        
        if biomarkers is None:
            # Default key biomarkers
            biomarkers = [
                'CSF Alpha-synuclein',
                'ABeta 1-42',
                'pTau',
                'tTau',
                'ABeta42',
                'ABeta40',
                'pTau181',
                'Ptau217p'
            ]
        
        key_data = self.merged_data[
            self.merged_data['TESTNAME'].isin(biomarkers)
        ].copy()
        
        return key_data

    def calculate_pd_pros(self, data_to_process):
        """
        Replicates the PD-ProS score calculation from Tsukita et al., Nature Aging 2022.
        This function uses the 14-protein panel and their published coefficients.
        """
        print("Calculating PD Proteomic Score (PD-ProS) using 14-protein panel...")

        if data_to_process is None or data_to_process.empty:
            print("Warning: Input data is empty. Cannot calculate PD-ProS.")
            return data_to_process
        
        data = data_to_process.copy()
        
        # 14 proteins and their coefficients from the paper
        pd_pros_panel = {
            'NEFL': 0.13, 'GFAP': 0.11, 'UCHL1': 0.10, 'GP130': -0.09,
            'MMP2': -0.08, 'TIMP1': -0.08, 'A2M': -0.07, 'IL6R': 0.07,
            'ICAM1': 0.07, 'VCAM1': 0.06, 'DCN': -0.06, 'VEGFA': 0.05,
            'FGF21': 0.05, 'ENRAGE': 0.05
        }
        required_proteins = list(pd_pros_panel.keys())
        
        if 'TESTNAME' not in data.columns or 'TESTVALUE' not in data.columns:
            print("Warning: 'TESTNAME' or 'TESTVALUE' not in data. Cannot calculate PD-ProS.")
            data['PD_PROS'] = np.nan
            return data

        # Pivot data to have proteins as columns
        try:
            data['TESTVALUE'] = pd.to_numeric(data['TESTVALUE'], errors='coerce')
            pivoted = data.pivot_table(
                index=['PATNO', 'RUNDATE'], 
                columns='TESTNAME', 
                values='TESTVALUE'
            )
            print(f"Pivoted data for PD-ProS calculation. Shape: {pivoted.shape}")
        except Exception as e:
            print(f"Error pivoting data for PD-ProS: {e}")
            data['PD_PROS'] = np.nan
            return data

        available_proteins = [p for p in required_proteins if p in pivoted.columns]
        missing_proteins = set(required_proteins) - set(available_proteins)
        if missing_proteins:
            print(f"Warning: The following proteins required for PD-ProS are missing: {missing_proteins}")

        if not available_proteins:
            print("Warning: No required proteins found. Cannot calculate PD-ProS.")
            data['PD_PROS'] = np.nan
            return data

        # Standardize (z-score) the available protein values
        for protein in available_proteins:
            mean = pivoted[protein].mean()
            std = pivoted[protein].std()
            if std > 0:
                pivoted[f'{protein}_z'] = (pivoted[protein] - mean) / std
            else:
                pivoted[f'{protein}_z'] = 0 # If no variance, z-score is 0
        
        # Calculate the weighted sum for the PD-ProS score
        pivoted['PD_PROS_CALCULATED'] = 0
        for protein in available_proteins:
            pivoted['PD_PROS_CALCULATED'] += pivoted[f'{protein}_z'] * pd_pros_panel[protein]
        
        # Merge the calculated score back into the original dataframe
        pivoted_to_merge = pivoted[['PD_PROS_CALCULATED']].reset_index()
        
        # Ensure RUNDATE is in the same format for merging if it's not already
        if 'RUNDATE' in data.columns and data['RUNDATE'].dtype != pivoted_to_merge['RUNDATE'].dtype:
             data['RUNDATE'] = pd.to_datetime(data['RUNDATE'])
             pivoted_to_merge['RUNDATE'] = pd.to_datetime(pivoted_to_merge['RUNDATE'])

        data = data.merge(
            pivoted_to_merge,
            on=['PATNO', 'RUNDATE'],
            how='left'
        )
        
        data.rename(columns={'PD_PROS_CALCULATED': 'PD_PROS'}, inplace=True)
        
        print("PD-ProS calculation complete.")
        return data

def main():
    """Test the data loader"""
    loader = PPMIDataLoader()
    
    # Load all data
    biomarkers = loader.load_biomarker_data()
    clinical = loader.load_clinical_data()
    genetic = loader.load_genetic_data()
    
    # Create merged dataset
    merged = loader.create_merged_dataset()
    
    # Get summary
    summary = loader.get_biomarker_summary()
    print("\nBiomarker Summary:")
    print(summary.head(10))
    
    # Get key biomarkers
    key_data = loader.get_key_biomarkers_data()
    print(f"\nKey biomarkers data: {len(key_data)} records")
    print("Available key biomarkers:")
    print(key_data['TESTNAME'].value_counts())

if __name__ == "__main__":
    main()