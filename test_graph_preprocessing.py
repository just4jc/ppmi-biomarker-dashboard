#!/usr/bin/env python3
"""
Test script to verify graph database preprocessing functionality.
"""

import os
import sys
import pandas as pd

def test_graph_preprocessing():
    """Test that the graph preprocessing script generates correct files."""
    
    print("=" * 60)
    print("Graph Database Preprocessing Tests")
    print("=" * 60)
    print()
    
    # Expected files
    expected_files = {
        'nodes': [
            'patients_nodes.csv',
            'biomarkers_nodes.csv',
            'cohorts_nodes.csv',
            'genetic_variants_nodes.csv'
        ],
        'relationships': [
            'measured_rels.csv',
            'has_cohort_rels.csv',
            'has_genotype_rels.csv'
        ],
        'documentation': [
            'GRAPH_SCHEMA.md'
        ]
    }
    
    all_expected = (expected_files['nodes'] + 
                    expected_files['relationships'] + 
                    expected_files['documentation'])
    
    # Check if graph_data directory exists
    if not os.path.exists('graph_data'):
        print("⚠ graph_data directory not found. Running preprocessing script...")
        import subprocess
        result = subprocess.run(['python', 'preprocess_for_graph_db.py'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Preprocessing failed: {result.stderr}")
            return False
    
    # Check file existence
    print("Checking file existence...")
    all_exist = True
    for filename in all_expected:
        filepath = os.path.join('graph_data', filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✓ {filename} ({size:,} bytes)")
        else:
            print(f"✗ {filename} NOT FOUND")
            all_exist = False
    print()
    
    if not all_exist:
        return False
    
    # Validate CSV structure
    print("Validating CSV structure...")
    
    # Test patients_nodes.csv
    try:
        patients = pd.read_csv('graph_data/patients_nodes.csv')
        assert 'patientId:ID' in patients.columns, "Missing patientId:ID column"
        assert ':LABEL' in patients.columns, "Missing :LABEL column"
        assert len(patients) > 0, "No patients found"
        print(f"✓ patients_nodes.csv: {len(patients)} patients")
    except Exception as e:
        print(f"✗ patients_nodes.csv validation failed: {e}")
        return False
    
    # Test biomarkers_nodes.csv
    try:
        biomarkers = pd.read_csv('graph_data/biomarkers_nodes.csv')
        assert 'biomarkerId:ID' in biomarkers.columns, "Missing biomarkerId:ID column"
        assert ':LABEL' in biomarkers.columns, "Missing :LABEL column"
        assert len(biomarkers) > 0, "No biomarkers found"
        print(f"✓ biomarkers_nodes.csv: {len(biomarkers)} biomarkers")
    except Exception as e:
        print(f"✗ biomarkers_nodes.csv validation failed: {e}")
        return False
    
    # Test cohorts_nodes.csv
    try:
        cohorts = pd.read_csv('graph_data/cohorts_nodes.csv')
        assert 'cohortId:ID' in cohorts.columns, "Missing cohortId:ID column"
        assert ':LABEL' in cohorts.columns, "Missing :LABEL column"
        assert len(cohorts) > 0, "No cohorts found"
        print(f"✓ cohorts_nodes.csv: {len(cohorts)} cohorts")
    except Exception as e:
        print(f"✗ cohorts_nodes.csv validation failed: {e}")
        return False
    
    # Test measured_rels.csv
    try:
        measured = pd.read_csv('graph_data/measured_rels.csv')
        assert ':START_ID' in measured.columns, "Missing :START_ID column"
        assert ':END_ID' in measured.columns, "Missing :END_ID column"
        assert ':TYPE' in measured.columns, "Missing :TYPE column"
        assert 'value:float' in measured.columns, "Missing value:float column"
        assert len(measured) > 0, "No measurements found"
        assert measured[':TYPE'].iloc[0] == 'MEASURED', "Incorrect relationship type"
        print(f"✓ measured_rels.csv: {len(measured)} measurements")
    except Exception as e:
        print(f"✗ measured_rels.csv validation failed: {e}")
        return False
    
    # Test has_cohort_rels.csv
    try:
        has_cohort = pd.read_csv('graph_data/has_cohort_rels.csv')
        assert ':START_ID' in has_cohort.columns, "Missing :START_ID column"
        assert ':END_ID' in has_cohort.columns, "Missing :END_ID column"
        assert ':TYPE' in has_cohort.columns, "Missing :TYPE column"
        assert len(has_cohort) > 0, "No cohort relationships found"
        assert has_cohort[':TYPE'].iloc[0] == 'HAS_COHORT', "Incorrect relationship type"
        print(f"✓ has_cohort_rels.csv: {len(has_cohort)} relationships")
    except Exception as e:
        print(f"✗ has_cohort_rels.csv validation failed: {e}")
        return False
    
    print()
    
    # Validate data consistency
    print("Checking data consistency...")
    
    # Check that all patient IDs in relationships exist in patients_nodes
    patient_ids = set(patients['patientId:ID'])
    measured_patient_ids = set(measured[':START_ID'])
    
    missing_patients = measured_patient_ids - patient_ids
    if len(missing_patients) > 0:
        print(f"⚠ Warning: {len(missing_patients)} patient IDs in measurements not found in patient nodes")
    else:
        print("✓ All patient IDs in measurements exist in patient nodes")
    
    # Check that all biomarker IDs in relationships exist in biomarkers_nodes
    biomarker_ids = set(biomarkers['biomarkerId:ID'])
    measured_biomarker_ids = set(measured[':END_ID'])
    
    missing_biomarkers = measured_biomarker_ids - biomarker_ids
    if len(missing_biomarkers) > 0:
        print(f"⚠ Warning: {len(missing_biomarkers)} biomarker IDs in measurements not found in biomarker nodes")
    else:
        print("✓ All biomarker IDs in measurements exist in biomarker nodes")
    
    # Check that all cohort IDs in relationships exist in cohorts_nodes
    cohort_ids = set(cohorts['cohortId:ID'])
    has_cohort_ids = set(has_cohort[':END_ID'])
    
    missing_cohorts = has_cohort_ids - cohort_ids
    if len(missing_cohorts) > 0:
        print(f"⚠ Warning: {len(missing_cohorts)} cohort IDs in relationships not found in cohort nodes")
    else:
        print("✓ All cohort IDs in relationships exist in cohort nodes")
    
    print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Nodes: {len(patients)} patients, {len(biomarkers)} biomarkers, {len(cohorts)} cohorts")
    print(f"Relationships: {len(measured)} measurements, {len(has_cohort)} cohort assignments")
    print()
    print("✓ All tests passed!")
    print()
    
    return True

if __name__ == "__main__":
    success = test_graph_preprocessing()
    sys.exit(0 if success else 1)
