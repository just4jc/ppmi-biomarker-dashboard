#!/usr/bin/env python3
"""
Data exploration script for PPMI biomarker datasets
Focus on alpha-synuclein, tau, p-tau biomarkers
"""

import pandas as pd
import numpy as np
import os

# Define the base path
BASE_PATH = "/Users/georgeng/Library/CloudStorage/GoogleDrive-2018076@teacher.hkuspace.hku.hk/My Drive/Courses/Duke-NUS MD/Research Articles/PD Related/Datasets/PPMI Various Datasets"

def explore_biomarker_data():
    """Explore biomarker analysis results"""
    
    # Load biomarker data
    bio_path = os.path.join(BASE_PATH, "Biospecimen Analysis Results (The Biomarkers We're Focusing On)")
    
    print("=== BIOMARKER DATA EXPLORATION ===")
    
    # Current biospecimen results
    current_bio = pd.read_csv(os.path.join(bio_path, "Current_Biospecimen_Analysis_Results_18Sep2025.csv"))
    print(f"\nCurrent biospecimen data shape: {current_bio.shape}")
    print(f"Columns: {list(current_bio.columns)}")
    print(f"Unique test names (first 20): {current_bio['TESTNAME'].unique()[:20]}")
    
    # Filter for key biomarkers
    biomarker_keywords = ['synuclein', 'tau', 'p-tau', 'ptau', 'alpha', 'aSyn', 'amyloid', 'abeta']
    bio_filtered = current_bio[current_bio['TESTNAME'].str.contains('|'.join(biomarker_keywords), case=False, na=False)]
    
    print(f"\nFiltered biomarker tests (containing key terms): {len(bio_filtered)} rows")
    print(f"Unique filtered test names: {bio_filtered['TESTNAME'].unique()}")
    
    # Check project IDs related to our focus
    focus_projects = [124, 125, 159, 172, 173, 207]
    project_filtered = current_bio[current_bio['PROJECTID'].isin(focus_projects)]
    print(f"\nFocus project biomarker tests: {len(project_filtered)} rows")
    print("Tests by project:")
    for pid in focus_projects:
        proj_tests = project_filtered[project_filtered['PROJECTID'] == pid]['TESTNAME'].unique()
        print(f"  Project {pid}: {len(proj_tests)} unique tests")
        if len(proj_tests) > 0:
            print(f"    Tests: {proj_tests[:5]}...")  # Show first 5
    
    # Check cohorts
    print(f"\nUnique cohorts: {current_bio['COHORT'].unique()}")
    print("Cohort counts:")
    print(current_bio['COHORT'].value_counts())
    
    return current_bio, bio_filtered, project_filtered

def explore_clinical_data():
    """Explore clinical and demographic data"""
    
    print("\n=== CLINICAL DATA EXPLORATION ===")
    
    # Demographics
    demo_path = os.path.join(BASE_PATH, "Core Patient & Visit Information (Essential for Linking All Data)")
    demographics = pd.read_csv(os.path.join(demo_path, "Demographics_18Sep2025.csv"))
    print(f"\nDemographics shape: {demographics.shape}")
    print(f"Unique patients: {demographics['PATNO'].nunique()}")
    
    # Age at visit
    age_data = pd.read_csv(os.path.join(demo_path, "Age_at_visit_18Sep2025.csv"))
    print(f"Age data shape: {age_data.shape}")
    
    # Clinical diagnosis
    clin_path = os.path.join(BASE_PATH, "Clinical & Motor Assessments(To Correlate Biomarkers with Disease Status & Progression)")
    clinical_diag = pd.read_csv(os.path.join(clin_path, "Medical History/Clinical_Diagnosis_18Sep2025.csv"))
    print(f"Clinical diagnosis shape: {clinical_diag.shape}")
    
    # MDS-UPDRS data
    updrs_path = os.path.join(clin_path, "ALL Motor : MDS-UPDRS")
    updrs3 = pd.read_csv(os.path.join(updrs_path, "MDS-UPDRS_Part_III_18Sep2025.csv"))
    print(f"MDS-UPDRS Part III shape: {updrs3.shape}")
    
    return demographics, age_data, clinical_diag, updrs3

def explore_genetic_data():
    """Explore genetic data"""
    
    print("\n=== GENETIC DATA EXPLORATION ===")
    
    gen_path = os.path.join(BASE_PATH, "Genetic Data (For Context and Stratification)")
    genetic = pd.read_csv(os.path.join(gen_path, "Genetic Data - Consensus APOE Genotype and Pathogenic Variants for LRRK2, GBA, VPS35, SNCA, PRKN, PARK7, and PINK1.csv"))
    print(f"Genetic data shape: {genetic.shape}")
    print(f"APOE genotypes: {genetic['APOE'].value_counts()}")
    print(f"Pathogenic variants: {genetic['PATHVAR_COUNT'].value_counts()}")
    
    return genetic

if __name__ == "__main__":
    # Run exploration
    bio_current, bio_filtered, bio_projects = explore_biomarker_data()
    demographics, age_data, clinical_diag, updrs3 = explore_clinical_data()
    genetic_data = explore_genetic_data()
    
    print("\n=== SUMMARY ===")
    print(f"Total patients in biomarker data: {bio_current['PATNO'].nunique()}")
    print(f"Total patients in demographics: {demographics['PATNO'].nunique()}")
    print(f"Total patients in genetic data: {genetic_data['PATNO'].nunique()}")
    
    # Fix RUNDATE column - filter out non-string values before finding min/max
    rundate_series = bio_current['RUNDATE'].dropna()
    rundate_strings = rundate_series[rundate_series.astype(str).str.match(r'\d{4}-\d{2}-\d{2}')]
    if len(rundate_strings) > 0:
        print(f"Date range in biomarker data: {rundate_strings.min()} to {rundate_strings.max()}")
    else:
        print("No valid dates found in RUNDATE column")