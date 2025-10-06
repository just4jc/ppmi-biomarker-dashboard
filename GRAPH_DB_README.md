# Graph Database Preprocessing for PPMI Data

This feature enables preprocessing of the PPMI biomarker data into a graph database format suitable for import into Neo4j or other graph databases.

## Overview

The preprocessing script (`preprocess_for_graph_db.py`) transforms the PPMI biomarker dataset into:
- **Node CSVs**: Entities like patients, biomarkers, cohorts, and genetic variants
- **Relationship CSVs**: Connections between entities (measurements, cohort assignments, genotypes)

This graph representation enables advanced queries like:
- Finding all patients with specific biomarker patterns
- Analyzing biomarker correlations across genetic profiles
- Tracing longitudinal progression patterns through the graph

## Quick Start

### 1. Run the Preprocessing Script

```bash
python preprocess_for_graph_db.py
```

This will create a `graph_data/` directory with the following files:

**Node CSVs:**
- `patients_nodes.csv` - Patient demographic data
- `biomarkers_nodes.csv` - Biomarker test definitions
- `cohorts_nodes.csv` - Diagnostic cohort groups
- `genetic_variants_nodes.csv` - Genetic variant profiles

**Relationship CSVs:**
- `measured_rels.csv` - Patient biomarker measurements
- `has_cohort_rels.csv` - Patient cohort assignments
- `has_genotype_rels.csv` - Patient genetic profiles

**Documentation:**
- `GRAPH_SCHEMA.md` - Detailed schema and import instructions

### 2. Review the Generated Files

```bash
ls -lh graph_data/
head graph_data/patients_nodes.csv
head graph_data/measured_rels.csv
```

### 3. Import into Neo4j

#### Option A: Using neo4j-admin (Recommended for large datasets)

```bash
neo4j-admin database import full \
  --nodes=Patient=graph_data/patients_nodes.csv \
  --nodes=Biomarker=graph_data/biomarkers_nodes.csv \
  --nodes=Cohort=graph_data/cohorts_nodes.csv \
  --nodes=GeneticVariant=graph_data/genetic_variants_nodes.csv \
  --relationships=MEASURED=graph_data/measured_rels.csv \
  --relationships=HAS_COHORT=graph_data/has_cohort_rels.csv \
  --relationships=HAS_GENOTYPE=graph_data/has_genotype_rels.csv \
  ppmi
```

#### Option B: Using Cypher LOAD CSV (For smaller datasets)

```cypher
// Load Patient nodes
LOAD CSV WITH HEADERS FROM 'file:///patients_nodes.csv' AS row
CREATE (p:Patient {
  patientId: row.`patientId:ID`,
  SEX: row.SEX,
  SEX_LABEL: row.SEX_LABEL
});

// See GRAPH_SCHEMA.md for complete import commands
```

## Graph Schema

### Nodes

- **Patient**: Individual study participants with demographic properties
- **Biomarker**: Types of biomarker tests/measurements
- **Cohort**: Diagnostic groups (PD, HC, Prodromal, SWEDD)
- **GeneticVariant**: Genetic variant profiles (APOE, LRRK2, GBA, etc.)

### Relationships

- **MEASURED**: (Patient)-[MEASURED]->(Biomarker) - Contains measurement values and metadata
- **HAS_COHORT**: (Patient)-[HAS_COHORT]->(Cohort) - Diagnostic classification
- **HAS_GENOTYPE**: (Patient)-[HAS_GENOTYPE]->(GeneticVariant) - Genetic profile

## Example Queries

### Find patients with high alpha-synuclein levels

```cypher
MATCH (p:Patient)-[m:MEASURED]->(b:Biomarker)
WHERE b.biomarkerId CONTAINS 'Alpha-synuclein' 
  AND m.value > 2000
RETURN p.patientId, m.value, m.age
ORDER BY m.value DESC
```

### Compare biomarker levels across cohorts

```cypher
MATCH (p:Patient)-[:HAS_COHORT]->(c:Cohort)
MATCH (p)-[m:MEASURED]->(b:Biomarker {biomarkerId: 'ABeta 1-42'})
RETURN c.cohortId, 
       AVG(m.value) as avg_value,
       STDEV(m.value) as std_value,
       COUNT(m) as n_measurements
ORDER BY avg_value DESC
```

### Find biomarker correlations for PD patients with specific genetic variants

```cypher
MATCH (p:Patient)-[:HAS_COHORT]->(c:Cohort {cohortId: 'PD'})
MATCH (p)-[:HAS_GENOTYPE]->(g:GeneticVariant {APOE: 'e4/e4'})
MATCH (p)-[m:MEASURED]->(b:Biomarker)
WHERE b.biomarkerId IN ['CSF Alpha-synuclein', 'ABeta 1-42', 'pTau']
RETURN p.patientId, b.biomarkerId, AVG(m.value) as avg_value
```

## Data Statistics

Based on the PPMI dataset (September 2025):

- **Patients**: ~2,114 unique participants
- **Biomarkers**: ~261 different biomarker tests
- **Cohorts**: 4 diagnostic groups (PD, HC, Prodromal, SWEDD)
- **Genetic Variants**: ~64 unique genetic profiles
- **Measurements**: ~39,147 biomarker measurements
- **Relationships**: ~80,844 total relationships

## Use Cases

1. **Biomarker Discovery**: Identify novel biomarker correlations using graph traversal
2. **Patient Stratification**: Group patients by genetic and biomarker profiles
3. **Longitudinal Analysis**: Track biomarker changes over time for individuals or cohorts
4. **Multi-hop Queries**: Find complex patterns like "patients with similar genetic profiles who have divergent biomarker trajectories"
5. **Network Analysis**: Analyze the biomarker network structure and identify hubs

## Requirements

- Python 3.7+
- pandas
- numpy
- data_loader module (included in this repository)
- For import: Neo4j 4.0+ or compatible graph database

## Troubleshooting

### CSV Format Issues

If you encounter import errors, ensure:
- CSV files use UTF-8 encoding
- Special characters in headers are properly quoted
- Float values use decimal points (not commas)

### Memory Issues

For large datasets:
- Use `neo4j-admin import` instead of LOAD CSV
- Consider batching the import
- Increase Neo4j heap size in `neo4j.conf`

### Missing Relationships

Some patients may not have:
- Genetic data (will not have HAS_GENOTYPE relationships)
- Cohort assignments (will not have HAS_COHORT relationships)

This is normal and reflects data availability in the source dataset.

## Further Reading

- [PPMI Study Overview](https://www.ppmi-info.org/)
- [Neo4j Import Documentation](https://neo4j.com/docs/operations-manual/current/tools/neo4j-admin/import/)
- [Graph Database Concepts](https://neo4j.com/docs/getting-started/current/graphdb-concepts/)
- Main Dashboard README: [README.md](README.md)

## Support

For issues with:
- **Data preprocessing**: Check `data_loader.py` and ensure data URLs are accessible
- **Graph schema**: Review `graph_data/GRAPH_SCHEMA.md`
- **Neo4j import**: Consult Neo4j documentation or community forums
