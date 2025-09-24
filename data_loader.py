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

# Define the base path - use repository root or environment variable if set
import os
BASE_PATH = os.environ.get('PPMI_DATA_PATH', os.path.dirname(os.path.abspath(__file__)))

class PPMIDataLoader:
    """Class to handle loading and preprocessing of PPMI data"""
    
    def __init__(self):
        self.base_path = BASE_PATH
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
        
        bio_path = os.path.join(self.base_path, "Biospecimen Analysis Results (The Biomarkers We're Focusing On)")
        
        # Try to load current biospecimen data first, fall back to pilot/SAA data
        biomarker_files = [
            "Current_Biospecimen_Analysis_Results_18Sep2025.csv",
            "Pilot_Biospecimen_Analysis_Results_18Sep2025.csv",
            "SAA_Biospecimen_Analysis_Results_18Sep2025.csv"
        ]
        
        self.biomarker_data = None
        for filename in biomarker_files:
            filepath = os.path.join(bio_path, filename)
            if os.path.exists(filepath):
                print(f"Loading {filename}...")
                if self.biomarker_data is None:
                    self.biomarker_data = pd.read_csv(filepath, low_memory=False)
                else:
                    # Append additional data
                    additional_data = pd.read_csv(filepath, low_memory=False)
                    self.biomarker_data = pd.concat([self.biomarker_data, additional_data], ignore_index=True)
                print(f"Loaded {len(additional_data if 'additional_data' in locals() else self.biomarker_data)} records from {filename}")
        
        if self.biomarker_data is None:
            raise FileNotFoundError("No biomarker data files found in repository")
        
        print(f"Total biomarker records: {len(self.biomarker_data)}")
        
        # Filter for key biomarkers and focus projects
        biomarker_keywords = ['synuclein', 'tau', 'p-tau', 'ptau', 'alpha', 'aSyn', 'amyloid', 'abeta']
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
        demo_path = os.path.join(self.base_path, "Core Patient & Visit Information (Essential for Linking All Data)")
        self.demographics = pd.read_csv(
            os.path.join(demo_path, "Demographics_18Sep2025.csv"),
            low_memory=False
        )
        
        # Age at visit
        self.age_data = pd.read_csv(os.path.join(demo_path, "Age_at_visit_18Sep2025.csv"))
        
        # Clinical diagnosis
        clin_path = os.path.join(self.base_path, "Clinical & Motor Assessments(To Correlate Biomarkers with Disease Status & Progression)")
        self.clinical_data = pd.read_csv(
            os.path.join(clin_path, "Medical History/Clinical_Diagnosis_18Sep2025.csv"),
            low_memory=False
        )
        
        # MDS-UPDRS Part III (motor examination) - handle gracefully if missing
        updrs_path = os.path.join(clin_path, "ALL Motor : MDS-UPDRS")
        updrs_file = os.path.join(updrs_path, "MDS-UPDRS_Part_III_18Sep2025.csv")
        
        if os.path.exists(updrs_file):
            self.updrs_data = pd.read_csv(updrs_file, low_memory=False)
            print(f"Loaded UPDRS data: {len(self.updrs_data)} records")
        else:
            print("⚠️ MDS-UPDRS data not found - creating empty DataFrame")
            # Create an empty DataFrame with expected columns
            self.updrs_data = pd.DataFrame(columns=['PATNO', 'EVENT_ID', 'NP3TOT'])
            print("UPDRS data not available (likely excluded from repository)")
        
        # Process demographics
        self.demographics['BIRTHDT'] = pd.to_datetime(self.demographics['BIRTHDT'], format='%m/%Y', errors='coerce')
        self.demographics['SEX_LABEL'] = self.demographics['SEX'].map({0: 'Female', 1: 'Male'})
        
        print(f"Loaded demographics for {self.demographics['PATNO'].nunique()} patients")
        
        return self.demographics, self.clinical_data, self.updrs_data
    
    def load_genetic_data(self):
        """Load genetic data"""
        print("Loading genetic data...")
        
        gen_path = os.path.join(self.base_path, "Genetic Data (For Context and Stratification)")
        self.genetic_data = pd.read_csv(
            os.path.join(gen_path, "Genetic Data - Consensus APOE Genotype and Pathogenic Variants for LRRK2, GBA, VPS35, SNCA, PRKN, PARK7, and PINK1.csv")
        )
        
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