#!/usr/bin/env python3
"""
Preprocessing script to convert PPMI biomarker data into graph database format.
Generates separate CSV files for nodes (entities) and relationships (edges).

This enables importing the data into graph databases like Neo4j for advanced
relationship queries and network analysis.

Output Structure:
- Nodes CSVs: patients_nodes.csv, biomarkers_nodes.csv, cohorts_nodes.csv, genetic_variants_nodes.csv
- Relationships CSVs: measured_rels.csv, has_cohort_rels.csv, has_genotype_rels.csv
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from data_loader import PPMIDataLoader

# Create output directory
OUTPUT_DIR = "graph_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_patient_nodes(merged_data):
    """
    Create patient nodes CSV.
    Each patient becomes a node with demographic properties.
    """
    print("Creating patient nodes...")
    
    # Get unique patients with their attributes
    patient_cols = ['PATNO', 'SEX', 'SEX_LABEL', 'BIRTHDT', 'HANDED', 
                   'HISPLAT', 'RAWHITE', 'RABLACK', 'RAASIAN']
    
    # Select columns that exist
    available_cols = ['PATNO'] + [col for col in patient_cols[1:] if col in merged_data.columns]
    
    patients = merged_data[available_cols].drop_duplicates('PATNO').copy()
    patients.rename(columns={'PATNO': 'patientId:ID'}, inplace=True)
    
    # Add label for Neo4j
    patients.insert(1, ':LABEL', 'Patient')
    
    # Save to CSV
    output_path = os.path.join(OUTPUT_DIR, 'patients_nodes.csv')
    patients.to_csv(output_path, index=False)
    print(f"✓ Created {len(patients)} patient nodes -> {output_path}")
    
    return patients

def create_biomarker_nodes(merged_data):
    """
    Create biomarker nodes CSV.
    Each unique biomarker test becomes a node.
    """
    print("Creating biomarker nodes...")
    
    # Get unique biomarkers
    biomarker_cols = ['TESTNAME', 'CLINICAL_EVENT']
    available_cols = [col for col in biomarker_cols if col in merged_data.columns]
    
    if 'TESTNAME' not in merged_data.columns:
        print("⚠ TESTNAME column not found, skipping biomarker nodes")
        return pd.DataFrame()
    
    biomarkers = merged_data[available_cols].drop_duplicates('TESTNAME').copy()
    biomarkers.rename(columns={'TESTNAME': 'biomarkerId:ID'}, inplace=True)
    
    # Add label for Neo4j
    biomarkers.insert(1, ':LABEL', 'Biomarker')
    
    # Save to CSV
    output_path = os.path.join(OUTPUT_DIR, 'biomarkers_nodes.csv')
    biomarkers.to_csv(output_path, index=False)
    print(f"✓ Created {len(biomarkers)} biomarker nodes -> {output_path}")
    
    return biomarkers

def create_cohort_nodes(merged_data):
    """
    Create cohort/diagnosis nodes CSV.
    Each unique cohort/diagnosis group becomes a node.
    """
    print("Creating cohort nodes...")
    
    if 'COHORT_SIMPLE' not in merged_data.columns:
        print("⚠ COHORT_SIMPLE column not found, skipping cohort nodes")
        return pd.DataFrame()
    
    # Get unique cohorts
    cohorts = merged_data[['COHORT_SIMPLE', 'COHORT']].drop_duplicates('COHORT_SIMPLE').dropna(subset=['COHORT_SIMPLE']).copy()
    cohorts.rename(columns={'COHORT_SIMPLE': 'cohortId:ID', 'COHORT': 'fullName'}, inplace=True)
    
    # Add label for Neo4j
    cohorts.insert(1, ':LABEL', 'Cohort')
    
    # Save to CSV
    output_path = os.path.join(OUTPUT_DIR, 'cohorts_nodes.csv')
    cohorts.to_csv(output_path, index=False)
    print(f"✓ Created {len(cohorts)} cohort nodes -> {output_path}")
    
    return cohorts

def create_genetic_variant_nodes(merged_data):
    """
    Create genetic variant nodes CSV.
    """
    print("Creating genetic variant nodes...")
    
    genetic_cols = ['APOE', 'LRRK2', 'GBA', 'SNCA', 'RISK_GROUP']
    available_cols = [col for col in genetic_cols if col in merged_data.columns]
    
    if not available_cols:
        print("⚠ No genetic columns found, skipping genetic variant nodes")
        return pd.DataFrame()
    
    # Create a composite genetic profile ID
    variants = merged_data[['PATNO'] + available_cols].drop_duplicates().copy()
    
    # Create unique variant profiles
    variant_profiles = variants[available_cols].drop_duplicates().dropna(how='all').copy()
    variant_profiles['variantId:ID'] = range(1, len(variant_profiles) + 1)
    variant_profiles['variantId:ID'] = 'VAR_' + variant_profiles['variantId:ID'].astype(str)
    
    # Reorder columns
    cols = ['variantId:ID'] + available_cols
    variant_profiles = variant_profiles[cols]
    
    # Add label for Neo4j
    variant_profiles.insert(1, ':LABEL', 'GeneticVariant')
    
    # Save to CSV
    output_path = os.path.join(OUTPUT_DIR, 'genetic_variants_nodes.csv')
    variant_profiles.to_csv(output_path, index=False)
    print(f"✓ Created {len(variant_profiles)} genetic variant nodes -> {output_path}")
    
    return variant_profiles

def create_measured_relationships(merged_data):
    """
    Create MEASURED relationships CSV.
    Connects patients to biomarkers with measurement values and metadata.
    """
    print("Creating MEASURED relationships...")
    
    required_cols = ['PATNO', 'TESTNAME', 'TESTVALUE_NUMERIC']
    if not all(col in merged_data.columns for col in required_cols):
        print("⚠ Required columns not found, skipping MEASURED relationships")
        return pd.DataFrame()
    
    # Select relevant columns
    rel_cols = ['PATNO', 'TESTNAME', 'TESTVALUE_NUMERIC', 'RUNDATE', 'AGE_AT_BIOMARKER', 
                'CLINICAL_EVENT', 'PROJECTID']
    available_cols = [col for col in rel_cols if col in merged_data.columns]
    
    measured = merged_data[available_cols].dropna(subset=['PATNO', 'TESTNAME']).copy()
    
    # Rename for Neo4j
    measured.rename(columns={
        'PATNO': ':START_ID',
        'TESTNAME': ':END_ID',
        'TESTVALUE_NUMERIC': 'value:float',
        'RUNDATE': 'date',
        'AGE_AT_BIOMARKER': 'age:float'
    }, inplace=True)
    
    # Add relationship type
    measured.insert(1, ':TYPE', 'MEASURED')
    
    # Save to CSV
    output_path = os.path.join(OUTPUT_DIR, 'measured_rels.csv')
    measured.to_csv(output_path, index=False)
    print(f"✓ Created {len(measured)} MEASURED relationships -> {output_path}")
    
    return measured

def create_has_cohort_relationships(merged_data):
    """
    Create HAS_COHORT relationships CSV.
    Connects patients to their diagnostic cohorts.
    """
    print("Creating HAS_COHORT relationships...")
    
    if 'COHORT_SIMPLE' not in merged_data.columns:
        print("⚠ COHORT_SIMPLE column not found, skipping HAS_COHORT relationships")
        return pd.DataFrame()
    
    # Get patient-cohort relationships
    has_cohort = merged_data[['PATNO', 'COHORT_SIMPLE']].drop_duplicates().dropna().copy()
    
    # Rename for Neo4j
    has_cohort.rename(columns={
        'PATNO': ':START_ID',
        'COHORT_SIMPLE': ':END_ID'
    }, inplace=True)
    
    # Add relationship type
    has_cohort.insert(1, ':TYPE', 'HAS_COHORT')
    
    # Save to CSV
    output_path = os.path.join(OUTPUT_DIR, 'has_cohort_rels.csv')
    has_cohort.to_csv(output_path, index=False)
    print(f"✓ Created {len(has_cohort)} HAS_COHORT relationships -> {output_path}")
    
    return has_cohort

def create_has_genotype_relationships(merged_data, genetic_variants):
    """
    Create HAS_GENOTYPE relationships CSV.
    Connects patients to their genetic variant profiles.
    """
    print("Creating HAS_GENOTYPE relationships...")
    
    genetic_cols = ['APOE', 'LRRK2', 'GBA', 'SNCA', 'RISK_GROUP']
    available_cols = [col for col in genetic_cols if col in merged_data.columns]
    
    if not available_cols or genetic_variants.empty:
        print("⚠ Genetic data not available, skipping HAS_GENOTYPE relationships")
        return pd.DataFrame()
    
    # Get patient genetic data
    patient_genetics = merged_data[['PATNO'] + available_cols].drop_duplicates('PATNO').dropna(how='all', subset=available_cols).copy()
    
    # Merge with variant profiles to get variant IDs
    # Create a merge key
    genetic_variants_for_merge = genetic_variants.copy()
    
    # For simplicity, create a composite key
    # This is a simplified approach - in production, you'd want a more robust matching
    if len(patient_genetics) > 0 and len(genetic_variants) > 0:
        # Create relationships based on APOE if available
        if 'APOE' in patient_genetics.columns:
            patient_genetics['APOE_temp'] = patient_genetics['APOE']
            genetic_variants_for_merge['APOE_temp'] = genetic_variants_for_merge['APOE']
            
            has_genotype = patient_genetics.merge(
                genetic_variants_for_merge[['variantId:ID', 'APOE_temp']],
                on='APOE_temp',
                how='inner'
            )[['PATNO', 'variantId:ID']].copy()
            
            has_genotype.rename(columns={
                'PATNO': ':START_ID',
                'variantId:ID': ':END_ID'
            }, inplace=True)
            
            # Add relationship type
            has_genotype.insert(1, ':TYPE', 'HAS_GENOTYPE')
            
            # Save to CSV
            output_path = os.path.join(OUTPUT_DIR, 'has_genotype_rels.csv')
            has_genotype.to_csv(output_path, index=False)
            print(f"✓ Created {len(has_genotype)} HAS_GENOTYPE relationships -> {output_path}")
            
            return has_genotype
    
    print("⚠ Could not create HAS_GENOTYPE relationships")
    return pd.DataFrame()

def create_graph_schema_doc():
    """
    Create a markdown document describing the graph schema.
    """
    schema_doc = """# PPMI Graph Database Schema

## Overview
This document describes the graph database schema for the PPMI (Parkinson's Progression Markers Initiative) biomarker data.

## Node Types

### Patient
Represents individual patients/participants in the study.

**Properties:**
- `patientId` (ID): Unique patient identifier (PATNO)
- `SEX`: Biological sex
- `SEX_LABEL`: Sex label (Male/Female)
- `BIRTHDT`: Birth date
- `HANDED`: Handedness
- `HISPLAT`: Hispanic/Latino ethnicity
- `RAWHITE`: White race indicator
- `RABLACK`: Black race indicator
- `RAASIAN`: Asian race indicator

### Biomarker
Represents different types of biomarker tests/measurements.

**Properties:**
- `biomarkerId` (ID): Biomarker test name (TESTNAME)
- `CLINICAL_EVENT`: Associated clinical event

### Cohort
Represents diagnostic groups or cohorts (e.g., PD, HC, Prodromal).

**Properties:**
- `cohortId` (ID): Simplified cohort name
- `fullName`: Full cohort description

### GeneticVariant
Represents genetic variant profiles.

**Properties:**
- `variantId` (ID): Unique variant profile identifier
- `APOE`: APOE genotype
- `LRRK2`: LRRK2 variant status
- `GBA`: GBA variant status
- `SNCA`: SNCA variant status
- `RISK_GROUP`: Genetic risk classification

## Relationship Types

### MEASURED
Connects a Patient to a Biomarker with measurement details.

**Properties:**
- `value` (float): Numeric measurement value
- `date`: Date of measurement
- `age` (float): Patient age at measurement
- `CLINICAL_EVENT`: Clinical event context
- `PROJECTID`: Source project identifier

**Pattern:** `(Patient)-[MEASURED]->(Biomarker)`

### HAS_COHORT
Connects a Patient to their diagnostic Cohort.

**Pattern:** `(Patient)-[HAS_COHORT]->(Cohort)`

### HAS_GENOTYPE
Connects a Patient to their GeneticVariant profile.

**Pattern:** `(Patient)-[HAS_GENOTYPE]->(GeneticVariant)`

## Example Queries

### Find all measurements for a specific patient
```cypher
MATCH (p:Patient {patientId: '3000'})-[m:MEASURED]->(b:Biomarker)
RETURN p, m, b
```

### Find patients with specific genetic variant and their biomarkers
```cypher
MATCH (p:Patient)-[HAS_GENOTYPE]->(g:GeneticVariant {APOE: 'e4/e4'})
MATCH (p)-[m:MEASURED]->(b:Biomarker)
WHERE b.biomarkerId CONTAINS 'Alpha-synuclein'
RETURN p.patientId, AVG(m.value) as avg_value
```

### Compare biomarker levels across cohorts
```cypher
MATCH (p:Patient)-[HAS_COHORT]->(c:Cohort)
MATCH (p)-[m:MEASURED]->(b:Biomarker {biomarkerId: 'ABeta 1-42'})
RETURN c.cohortId, AVG(m.value) as avg_value, COUNT(m) as n_measurements
ORDER BY avg_value DESC
```

## Import Instructions

### Neo4j Import (neo4j-admin)
```bash
neo4j-admin database import full \\
  --nodes=Patient=graph_data/patients_nodes.csv \\
  --nodes=Biomarker=graph_data/biomarkers_nodes.csv \\
  --nodes=Cohort=graph_data/cohorts_nodes.csv \\
  --nodes=GeneticVariant=graph_data/genetic_variants_nodes.csv \\
  --relationships=MEASURED=graph_data/measured_rels.csv \\
  --relationships=HAS_COHORT=graph_data/has_cohort_rels.csv \\
  --relationships=HAS_GENOTYPE=graph_data/has_genotype_rels.csv \\
  ppmi
```

### Cypher LOAD CSV (for smaller datasets)
```cypher
// Load Patient nodes
LOAD CSV WITH HEADERS FROM 'file:///patients_nodes.csv' AS row
CREATE (p:Patient {
  patientId: row.`patientId:ID`,
  SEX: row.SEX,
  SEX_LABEL: row.SEX_LABEL
  // ... other properties
});

// Load MEASURED relationships
LOAD CSV WITH HEADERS FROM 'file:///measured_rels.csv' AS row
MATCH (p:Patient {patientId: row.`:START_ID`})
MATCH (b:Biomarker {biomarkerId: row.`:END_ID`})
CREATE (p)-[m:MEASURED {
  value: toFloat(row.`value:float`),
  age: toFloat(row.`age:float`),
  date: row.date
}]->(b);
```

## Generated Files

| File | Type | Description |
|------|------|-------------|
| `patients_nodes.csv` | Nodes | Patient entities |
| `biomarkers_nodes.csv` | Nodes | Biomarker test types |
| `cohorts_nodes.csv` | Nodes | Diagnostic cohorts |
| `genetic_variants_nodes.csv` | Nodes | Genetic variant profiles |
| `measured_rels.csv` | Relationships | Patient-to-Biomarker measurements |
| `has_cohort_rels.csv` | Relationships | Patient-to-Cohort assignments |
| `has_genotype_rels.csv` | Relationships | Patient-to-GeneticVariant connections |
"""
    
    output_path = os.path.join(OUTPUT_DIR, 'GRAPH_SCHEMA.md')
    with open(output_path, 'w') as f:
        f.write(schema_doc)
    print(f"✓ Created graph schema documentation -> {output_path}")

def main():
    """
    Main preprocessing pipeline.
    """
    print("="*60)
    print("PPMI Graph Database Preprocessing")
    print("="*60)
    print()
    
    # Load data
    print("Loading PPMI data...")
    loader = PPMIDataLoader()
    merged_data = loader.create_merged_dataset()
    
    if merged_data is None or merged_data.empty:
        print("✗ Failed to load data. Exiting.")
        return
    
    print(f"✓ Loaded {len(merged_data)} records for {merged_data['PATNO'].nunique()} patients")
    print()
    
    # Create node CSVs
    print("-"*60)
    print("Creating Node CSVs")
    print("-"*60)
    patients = create_patient_nodes(merged_data)
    biomarkers = create_biomarker_nodes(merged_data)
    cohorts = create_cohort_nodes(merged_data)
    genetic_variants = create_genetic_variant_nodes(merged_data)
    print()
    
    # Create relationship CSVs
    print("-"*60)
    print("Creating Relationship CSVs")
    print("-"*60)
    measured = create_measured_relationships(merged_data)
    has_cohort = create_has_cohort_relationships(merged_data)
    has_genotype = create_has_genotype_relationships(merged_data, genetic_variants)
    print()
    
    # Create schema documentation
    print("-"*60)
    print("Creating Documentation")
    print("-"*60)
    create_graph_schema_doc()
    print()
    
    print("="*60)
    print("Preprocessing Complete!")
    print("="*60)
    print(f"Output directory: {OUTPUT_DIR}/")
    print()
    print("Summary:")
    print(f"  • {len(patients)} patients")
    print(f"  • {len(biomarkers)} biomarkers")
    print(f"  • {len(cohorts)} cohorts")
    print(f"  • {len(genetic_variants)} genetic variants")
    print(f"  • {len(measured)} measurements")
    print(f"  • {len(has_cohort)} patient-cohort relationships")
    print(f"  • {len(has_genotype)} patient-genotype relationships")
    print()
    print("Next steps:")
    print("  1. Review the generated CSV files in the graph_data/ directory")
    print("  2. Read GRAPH_SCHEMA.md for schema details and import instructions")
    print("  3. Import into your graph database using neo4j-admin or LOAD CSV")

if __name__ == "__main__":
    main()
