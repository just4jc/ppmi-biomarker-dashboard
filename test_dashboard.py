#!/usr/bin/env python3
"""
Test script to verify PPMI data loading and basic functionality
Run this before launching the dashboard to ensure everything works
"""

import sys
import os
import traceback

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing package imports...")
    
    try:
        import pandas as pd
        print("✓ pandas imported successfully")
    except ImportError as e:
        print(f"✗ pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ numpy import failed: {e}")
        return False
    
    try:
        import streamlit as st
        print("✓ streamlit imported successfully")
    except ImportError as e:
        print(f"✗ streamlit import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✓ plotly imported successfully")
    except ImportError as e:
        print(f"✗ plotly import failed: {e}")
        return False
    
    try:
        from scipy import stats
        print("✓ scipy imported successfully")
    except ImportError as e:
        print(f"✗ scipy import failed: {e}")
        return False
    
    return True

def test_data_files():
    """Test that required data files exist"""
    print("\nTesting data file availability...")
    
    base_path = "/Users/georgeng/Library/CloudStorage/GoogleDrive-2018076@teacher.hkuspace.hku.hk/My Drive/Courses/Duke-NUS MD/Research Articles/PD Related/Datasets/PPMI Various Datasets"
    
    required_files = [
        "Biospecimen Analysis Results (The Biomarkers We're Focusing On)/Current_Biospecimen_Analysis_Results_18Sep2025.csv",
        "Core Patient & Visit Information (Essential for Linking All Data)/Demographics_18Sep2025.csv",
        "Core Patient & Visit Information (Essential for Linking All Data)/Age_at_visit_18Sep2025.csv",
        "Clinical & Motor Assessments(To Correlate Biomarkers with Disease Status & Progression)/Medical History/Clinical_Diagnosis_18Sep2025.csv",
        "Clinical & Motor Assessments(To Correlate Biomarkers with Disease Status & Progression)/ALL Motor : MDS-UPDRS/MDS-UPDRS_Part_III_18Sep2025.csv",
        "Genetic Data (For Context and Stratification)/Genetic Data - Consensus APOE Genotype and Pathogenic Variants for LRRK2, GBA, VPS35, SNCA, PRKN, PARK7, and PINK1.csv"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"✓ {os.path.basename(file_path)} exists")
        else:
            print(f"✗ {os.path.basename(file_path)} NOT FOUND")
            all_exist = False
    
    return all_exist

def test_data_loading():
    """Test that data can be loaded successfully"""
    print("\nTesting data loading...")
    
    try:
        from data_loader import PPMIDataLoader
        print("✓ PPMIDataLoader imported successfully")
        
        loader = PPMIDataLoader()
        print("✓ PPMIDataLoader instantiated")
        
        # Test biomarker data loading
        biomarker_data = loader.load_biomarker_data()
        print(f"✓ Biomarker data loaded: {len(biomarker_data)} records")
        
        # Test clinical data loading
        demographics, clinical, updrs = loader.load_clinical_data()
        print(f"✓ Demographics loaded: {len(demographics)} records")
        print(f"✓ UPDRS data loaded: {len(updrs)} records")
        
        # Test genetic data loading
        genetic = loader.load_genetic_data()
        print(f"✓ Genetic data loaded: {len(genetic)} records")
        
        # Test merged dataset creation
        merged = loader.create_merged_dataset()
        print(f"✓ Merged dataset created: {len(merged)} records")
        
        return True
        
    except Exception as e:
        print(f"✗ Data loading failed: {e}")
        traceback.print_exc()
        return False

def test_key_biomarkers():
    """Test that key biomarkers are available in the data"""
    print("\nTesting key biomarker availability...")
    
    try:
        from data_loader import PPMIDataLoader
        loader = PPMIDataLoader()
        merged_data = loader.create_merged_dataset()
        
        key_biomarkers = [
            'CSF Alpha-synuclein',
            'ABeta 1-42',
            'pTau',
            'tTau'
        ]
        
        available_biomarkers = merged_data['TESTNAME'].unique()
        
        for biomarker in key_biomarkers:
            if biomarker in available_biomarkers:
                count = len(merged_data[merged_data['TESTNAME'] == biomarker])
                print(f"✓ {biomarker}: {count} measurements")
            else:
                print(f"✗ {biomarker}: NOT FOUND")
        
        print(f"\nTotal unique biomarkers available: {len(available_biomarkers)}")
        print("Sample biomarkers:")
        for i, biomarker in enumerate(sorted(available_biomarkers)[:10]):
            print(f"  {i+1}. {biomarker}")
        
        return True
        
    except Exception as e:
        print(f"✗ Key biomarker test failed: {e}")
        return False

def test_cohorts_and_filtering():
    """Test that cohorts and filtering work correctly"""
    print("\nTesting cohort distribution and filtering...")
    
    try:
        from data_loader import PPMIDataLoader
        loader = PPMIDataLoader()
        merged_data = loader.create_merged_dataset()
        
        # Test cohort distribution
        cohort_counts = merged_data['COHORT_SIMPLE'].value_counts()
        print("Cohort distribution:")
        for cohort, count in cohort_counts.items():
            print(f"  {cohort}: {count} records")
        
        # Test basic filtering
        hc_data = merged_data[merged_data['COHORT_SIMPLE'] == 'HC']
        pd_data = merged_data[merged_data['COHORT_SIMPLE'] == 'PD']
        
        print(f"\nHealthy Controls: {hc_data['PATNO'].nunique()} unique patients")
        print(f"Parkinson's Disease: {pd_data['PATNO'].nunique()} unique patients")
        
        # Test genetic risk groups
        if 'RISK_GROUP' in merged_data.columns:
            risk_counts = merged_data['RISK_GROUP'].value_counts()
            print("\nGenetic risk groups:")
            for risk, count in risk_counts.items():
                print(f"  {risk}: {count} records")
        
        return True
        
    except Exception as e:
        print(f"✗ Cohort/filtering test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("PPMI Dashboard Test Suite")
    print("="*60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Data Files", test_data_files),
        ("Data Loading", test_data_loading),
        ("Key Biomarkers", test_key_biomarkers),
        ("Cohorts & Filtering", test_cohorts_and_filtering)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'-'*40}")
        print(f"Running: {test_name}")
        print(f"{'-'*40}")
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You can launch the dashboard with:")
        print("   streamlit run ppmi_dashboard.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix issues before launching dashboard.")
        print("\nCommon solutions:")
        print("- Install missing packages: pip install -r requirements.txt")
        print("- Check data file paths in data_loader.py")
        print("- Ensure PPMI data files are in the correct directory structure")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)