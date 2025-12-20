# PPMI Parkinson's Disease Biomarker Dashboard 🧠

An interactive Streamlit dashboard for exploring biomarker relationships in Parkinson's Disease progression using data from the Parkinson's Progression Markers Initiative (PPMI).

## Overview

This dashboard focuses on key Parkinson's disease biomarkers implicated in Lewy body pathology:
- **Alpha-synuclein** (total, seeding-competent, RT-QuIC assays)
- **Tau proteins** (total tau, phosphorylated tau at different sites)
- **Amyloid-beta** (Aβ42, Aβ40 ratios)
- **Other biomarkers** from PPMI focus projects

## Key Features

### 1. 📊 Biomarker Levels by Diagnosis
- **Box/Violin plots** comparing biomarker levels across diagnostic groups:
  - Healthy Controls (HC)
  - Parkinson's Disease (PD) 
  - Prodromal PD
  - SWEDD (without evidence of dopaminergic deficit)
- **Statistical testing** with Mann-Whitney U tests between groups
- **Interactive filtering** by demographics and genetics

### 2. 📈 Longitudinal Analysis
- **Age-related changes** in biomarker levels over time
- **Trend analysis** with regression lines by diagnostic group
- **Correlation analysis** between age and biomarker levels
- Helps identify progression patterns

### 3. 🔗 Correlation Analysis
- **Biomarker-to-biomarker** correlations (e.g., α-syn vs tau)
- **Biomarker-to-clinical** correlations (e.g., α-syn vs UPDRS scores)
- **Scatter plots** with regression lines and confidence intervals
- Statistical significance testing

### 4. 🌡️ Multi-variable Heatmaps
- **Comprehensive correlation matrices** between multiple biomarkers
- **Clinical score integration** (UPDRS motor scores, cognitive assessments)
- **Visual pattern identification** across disease states

### 5. 🔍 Advanced Filtering
- **Demographic filters**: Age, sex, ethnicity
- **Genetic stratification**: APOE genotype, pathogenic variants (LRRK2, GBA, etc.)
- **Risk group classification**: High vs standard genetic risk
- **Real-time plot updates** based on selected criteria

## Focus Projects from PPMI

The dashboard prioritizes data from these core biomarker projects:

- **Project 124**: Total alpha-synuclein in CSF
- **Project 125**: Amyloid-beta, tau, p-tau (longitudinal cohort)
- **Project 159**: Expanded Aβ, tau, p-tau analysis  
- **Project 172**: Alpha-synuclein RT-QuIC seeding assay
- **Project 173**: Seeding-competent alpha-synuclein for prodromal PD
- **Project 207**: Seed Amplification Assay (SAA) for alpha-synuclein aggregates

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Access to PPMI dataset files

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Data Setup
Ensure your PPMI data directory structure matches:
```
PPMI Various Datasets/
├── Biospecimen Analysis Results (The Biomarkers We're Focusing On)/
│   ├── Current_Biospecimen_Analysis_Results_18Sep2025.csv
│   ├── SAA_Biospecimen_Analysis_Results_18Sep2025.csv
│   └── ...
├── Core Patient & Visit Information (Essential for Linking All Data)/
│   ├── Demographics_18Sep2025.csv
│   ├── Age_at_visit_18Sep2025.csv
│   └── ...
├── Clinical & Motor Assessments(...)/
│   ├── Medical History/
│   ├── ALL Motor : MDS-UPDRS/
│   └── ...
├── Genetic Data (For Context and Stratification)/
│   └── Genetic Data - Consensus APOE Genotype and Pathogenic Variants...csv
└── ...
```

### 3. Launch Dashboard
```bash
streamlit run streamlit_app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

### 🔐 Configure Authentication (recommended)

This app supports simple authentication. In Streamlit Cloud, set the following secrets (App → Settings → Secrets):

```
app_user: admin
app_password: ppmi2025
```

For local development, you can alternatively use environment variables:

```bash
export APP_USER=admin
export APP_PASSWORD=ppmi2025
streamlit run streamlit_app.py
```

If no secrets or env vars are provided, the app falls back to the default credentials shown above and displays a hint on the login screen.

## Usage Guide

### Getting Started
1. **Load the dashboard** - Data loads automatically with caching for performance
2. **Apply filters** - Use the sidebar to filter by cohort, age, genetics, and project (defaults to Project 177)
3. **Explore tabs** - Navigate through different analysis types
4. **Interact with plots** - Hover, zoom, and select data points

### Sidebar Controls
- **Project filter**: Defaults to Project 177; select additional projects as needed
- **Biomarker list**: Toggle between *Key* biomarkers and *All*; when Project 177 is active, the list defaults to *All*
- **Cohort, age, genetic risk**: Apply global filters that propagate to all tabs

### Analysis Workflow
1. **Start with Biomarker Levels** - Compare groups for individual biomarkers
2. **Check Longitudinal Patterns** - Look for age-related changes
3. **Examine Correlations** - Identify biomarker relationships
4. **Use Heatmaps** - Get overview of all correlations
5. **Review Data Summary** - Understand your filtered dataset

### Interpretation Tips
- **Statistical significance**: * p<0.05, ** p<0.01, *** p<0.001
- **Effect sizes**: Consider both statistical and clinical significance
- **Sample sizes**: Check data summary for adequate power
- **Missing data**: Review data quality metrics

## Technical Details

### Data Processing
- **Automatic data loading** with Streamlit caching
- **Numeric conversion** of biomarker values with error handling  
- **Date parsing** for longitudinal analysis
- **Missing data handling** with appropriate exclusions
- **Statistical testing** using scipy.stats

### Performance Optimizations
- **Cached data loading** prevents repeated file reads
- **Efficient filtering** using pandas operations
- **Interactive plots** with Plotly for smooth user experience
- **Memory management** for large datasets

### Statistical Methods
- **Mann-Whitney U test** for non-parametric group comparisons
- **Pearson correlation** for linear relationships
- **Linear regression** with confidence intervals
- **Multiple testing correction** considerations

## Data Sources & Citations

This dashboard analyzes data from the Parkinson's Progression Markers Initiative (PPMI):

> PPMI – a public-private partnership – is funded by the Michael J. Fox Foundation for Parkinson's Research funding partners Abbott, Acumen Pharmaceuticals, Allergan, Amathus Therapeutics, AskBio, Avid Radiopharmaceuticals, BIAL, Biogen, Biohaven, BioLegend, Bristol-Myers Squibb, Calico Labs, Celgene, Cerevel Therapeutics, Coave Therapeutics, DaCapo Brainscience, Denali, Edmond J. Safra Foundation, GE Healthcare, Genentech, GSK, Golub Capital, Handl Therapeutics, Insitro, Janssen Neuroscience, Lilly, Lundbeck, Merck, Meso Scale Discovery, Neurocrine Biosciences, Pfizer, Piramal, Prevail Therapeutics, Roche, Sanofi, Servier, Takeda, Teva, UCB, Verily, Voyager Therapeutics, and Yumanity Therapeutics.

## Key Biomarkers & Clinical Relevance

### Alpha-synuclein
- **Clinical significance**: Central protein in Lewy body formation
- **Assay types**: Total α-syn (ELISA), seeding assays (RT-QuIC, SAA)
- **Expected patterns**: Lower CSF levels in PD, increased seeding activity

### Tau Proteins
- **Total tau (tTau)**: General neuronal damage marker
- **Phospho-tau (p-tau)**: Specific tau pathology markers
- **Sites measured**: p-tau181, p-tau217 (newer, more specific)
- **Clinical utility**: Disease progression, cognitive decline

### Amyloid-beta
- **Aβ42**: Primary amyloid species, decreased in AD
- **Aβ40**: Reference amyloid, ratio Aβ42/Aβ40 informative
- **PD relevance**: Comorbid pathology, cognitive symptoms

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure all requirements are installed
2. **File not found**: Check data file paths in `data_loader.py`
3. **Memory issues**: Consider filtering data more restrictively
4. **Slow loading**: First run takes longer due to data processing

### Performance Tips
- **Filter early**: Apply demographic/genetic filters to reduce data size
- **Use key biomarkers**: Focus on main biomarkers for faster loading
- **Clear cache**: Use Streamlit's "Clear cache" option if data updates

## Contributing

To enhance the dashboard:
1. **Add new biomarkers**: Update `key_biomarker_names` in dashboard
2. **New visualizations**: Create functions following existing patterns
3. **Statistical methods**: Add to correlation/testing functions
4. **UI improvements**: Enhance Streamlit interface

## License & Ethical Use

- **Data usage**: Must comply with PPMI Data Use Agreement
- **Publication**: Follow PPMI publication guidelines
- **Patient privacy**: All data must remain de-identified
- **Research ethics**: Use only for approved research purposes

## Contact & Support

For questions about:
- **Dashboard functionality**: Check code comments and documentation
- **PPMI data access**: Visit PPMI website (ppmi-info.org)
- **Statistical methods**: Refer to scientific literature on biomarker analysis
- **Clinical interpretation**: Consult with domain experts

---

**Version**: 1.0  
**Last Updated**: September 2025  
**Tested with**: Python 3.9+, Streamlit 1.28+