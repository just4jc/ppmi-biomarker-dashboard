# PPMI Biomarker Dashboard v0.1

**Parkinson's Progression Markers Initiative (PPMI) Interactive Biomarker Analysis Dashboard**

![Version](https://img.shields.io/badge/version-0.1-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28%2B-red.svg)
![License](https://img.shields.io/badge/license-Private-yellow.svg)

## 🧠 Overview

An interactive Streamlit dashboard for exploring biomarker relationships in Parkinson's Disease progression using data from the Parkinson's Progression Markers Initiative (PPMI). This dashboard focuses on key biomarkers implicated in Lewy body pathology: alpha-synuclein, tau proteins, and amyloid-beta.

## ✨ Features

### Core Visualizations
- 📊 **Biomarker Levels by Diagnosis**: Box/violin plots comparing CSF α-synuclein, tau, p-tau across HC, PD, Prodromal PD groups
- 📈 **Longitudinal Analysis**: Age-related biomarker changes with trend lines and statistical correlations  
- 🔗 **Correlation Analysis**: Biomarker-to-biomarker and biomarker-to-clinical scatter plots with regression lines
- 🌡️ **Multi-variable Heatmaps**: Comprehensive correlation matrices between biomarkers and clinical variables

### Interactive Filtering
- 🔍 **Demographics**: Age range, sex selection
- 🧬 **Genetic Stratification**: APOE genotype, pathogenic variants (LRRK2, GBA, SNCA, etc.)
- 🏥 **Clinical Groups**: HC, PD, Prodromal PD, SWEDD cohorts
- ⚡ **Real-time Updates**: All visualizations update dynamically based on applied filters

## 🔬 Focus Projects (PPMI)

- **Project 124**: Total alpha-synuclein in CSF
- **Project 125**: Amyloid-beta, tau, p-tau (longitudinal cohort)
- **Project 159**: Expanded Aβ, tau, p-tau analysis  
- **Project 172**: Alpha-synuclein RT-QuIC seeding assay
- **Project 173**: Seeding-competent alpha-synuclein for prodromal PD
- **Project 207**: Seed Amplification Assay (SAA) for alpha-synuclein aggregates

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Access to PPMI dataset (not included - requires PPMI Data Use Agreement)

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd ppmi-biomarker-dashboard

# Install dependencies
pip install -r requirements.txt

# Run tests (optional but recommended)
python test_dashboard.py

# Launch dashboard
streamlit run streamlit_app.py
# OR use the launch script
./launch_dashboard.sh
```

### Access
Once launched, visit: `http://localhost:8501`

## 📁 Project Structure

```
ppmi-biomarker-dashboard/
├── streamlit_app.py              # Main Streamlit application
├── data_loader.py             # Data preprocessing and loading utilities
├── requirements.txt           # Python dependencies
├── launch_dashboard.sh        # Quick launch script
├── test_dashboard.py          # Comprehensive test suite
├── test_correlation_fix.py    # Specific correlation testing
├── data_exploration.py        # Data exploration utilities
├── README.md                  # This file
├── QUICK_START_GUIDE.md       # Detailed usage guide
├── FIX_DUPLICATE_LABELS.md    # Technical fix documentation
└── .gitignore                 # Git ignore rules
```

## 📊 Data Overview (Sample Dataset)

- **36,775 biomarker records** from 2,114 unique patients
- **256 unique biomarker tests** including key α-syn, tau, Aβ markers
- **7,489 patient demographics** with genetic data
- **34,628 MDS-UPDRS motor assessments**
- **6,265 genetic profiles** with APOE, LRRK2, GBA variants

### Cohort Distribution
- **Healthy Controls (HC)**: 208 patients
- **Parkinson's Disease (PD)**: 702 patients  
- **Prodromal PD**: Multiple visit records
- **SWEDD**: Scans without evidence of dopaminergic deficit

## 🛠️ Technical Features

### Statistical Methods
- Non-parametric group comparisons (Mann-Whitney U)
- Pearson correlation analysis with significance testing
- Linear regression with confidence intervals
- Multiple biomarker correlation matrices
- Age-adjusted trend analysis

### Performance Optimizations
- Streamlit caching for fast data loading
- Efficient pandas operations for large datasets
- Interactive Plotly visualizations
- Memory-efficient data aggregation

### Data Quality
- Automatic handling of duplicate patient measurements
- Missing data management
- Numeric data validation
- Statistical significance reporting

## 📝 Version History

### v0.1 (September 18, 2025)
- ✅ Initial release with core functionality
- ✅ Interactive biomarker visualization dashboard
- ✅ Statistical analysis and correlation features
- ✅ Multi-cohort filtering and comparison
- ✅ Genetic risk stratification
- ✅ Fixed duplicate labels error in correlation matrices
- ✅ Comprehensive test suite
- ✅ Complete documentation

## 🔒 Data Privacy & Ethics

**⚠️ IMPORTANT**: This repository contains **NO PATIENT DATA**. 

- All PPMI data files are excluded via `.gitignore`
- Only analysis code and documentation are version controlled
- Users must obtain PPMI data separately through proper channels
- Compliance with PPMI Data Use Agreement required
- All data must remain de-identified and secure

## 📋 Requirements

```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
scipy>=1.10.0
seaborn>=0.12.0
matplotlib>=3.7.0
openpyxl>=3.1.0
```

## 🧪 Testing

Run the complete test suite:
```bash
python test_dashboard.py
```

Test specific correlation functionality:
```bash
python test_correlation_fix.py
```

All tests should pass before using the dashboard for analysis.

## 🐛 Known Issues & Fixes

- ✅ **Fixed**: `ValueError: cannot reindex on an axis with duplicate labels` 
  - **Solution**: Implemented proper aggregation of duplicate patient measurements
  - **Details**: See `FIX_DUPLICATE_LABELS.md`

## 📚 Documentation

- `README.md` - This overview and setup guide
- `QUICK_START_GUIDE.md` - Detailed usage instructions and scientific applications
- `FIX_DUPLICATE_LABELS.md` - Technical documentation of correlation fix
- Inline code documentation and comments throughout

## 🤝 Contributing

This is a private research tool. For modifications or enhancements:

1. Create feature branch from `main`
2. Implement changes with appropriate tests
3. Update documentation as needed  
4. Ensure all tests pass
5. Submit pull request with detailed description

## 📄 License

Private research tool. Not for public distribution.

## 📞 Support

For technical issues or questions about the dashboard functionality, refer to:
- Documentation files in this repository
- Inline code comments and docstrings
- PPMI official documentation for data-related questions

## 🙏 Acknowledgments

- **PPMI Study**: Parkinson's Progression Markers Initiative
- **Funding**: Michael J. Fox Foundation and pharmaceutical partners
- **Data Contributors**: PPMI study participants and research sites worldwide

---

**Built for advancing Parkinson's disease biomarker research** 🧬🔬📊