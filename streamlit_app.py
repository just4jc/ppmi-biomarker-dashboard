#!/usr/bin/env python3
"""
PPMI Parkinson's Disease Biomarker Dashboard
Interactive Streamlit dashboard for exploring PPMI biomarker data

Features:
- Biomarker levels by diagnosis (Box/Violin plots)
- Longitudinal biomarker changes (Line plots)
- Correlation analysis (Scatter plots with regression)
- Heatmaps for multi-biomarker correlations
- Filtering by demographics, genetics, medication
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import warnings
warnings.filterwarnings('ignore')

# Import our data loader
from data_loader import PPMIDataLoader

# Configure Streamlit page
st.set_page_config(
    page_title="PPMI Biomarker Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .reportview-container {
        margin-top: -2em;
    }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    .main .block-container {
        padding-top: 1rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_ppmi_data():
    """Load and cache PPMI data"""
    try:
        loader = PPMIDataLoader()
        merged_data = loader.load_merged_data()
        biomarker_summary = loader.get_biomarker_summary()
        key_biomarkers = loader.get_key_biomarkers()
        return merged_data, biomarker_summary, key_biomarkers, loader
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

def create_biomarker_boxplot(data, biomarker, cohorts=None):
    """Create box plot for biomarker levels by diagnosis"""
    if cohorts:
        filtered_data = data[data['COHORT'].isin(cohorts)]
    else:
        filtered_data = data
    
    biomarker_data = filtered_data[filtered_data['TESTNAME'] == biomarker]
    
    if biomarker_data.empty:
        st.warning(f"No data available for {biomarker}")
        return None
    
    # Remove outliers for better visualization
    Q1 = biomarker_data['TESTVALUE'].quantile(0.25)
    Q3 = biomarker_data['TESTVALUE'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    cleaned_data = biomarker_data[
        (biomarker_data['TESTVALUE'] >= lower_bound) & 
        (biomarker_data['TESTVALUE'] <= upper_bound)
    ]
    
    fig = px.box(
        cleaned_data, 
        x='APPRDX', 
        y='TESTVALUE',
        color='APPRDX',
        title=f'{biomarker} Levels by Diagnosis',
        labels={'TESTVALUE': f'{biomarker} Level', 'APPRDX': 'Diagnosis'}
    )
    
    fig.update_layout(
        height=500,
        showlegend=False,
        xaxis_title="Diagnosis",
        yaxis_title=f"{biomarker} Level"
    )
    
    return fig

def create_biomarker_violinplot(data, biomarker, cohorts=None):
    """Create violin plot for biomarker levels by diagnosis"""
    if cohorts:
        filtered_data = data[data['COHORT'].isin(cohorts)]
    else:
        filtered_data = data
    
    biomarker_data = filtered_data[filtered_data['TESTNAME'] == biomarker]
    
    if biomarker_data.empty:
        st.warning(f"No data available for {biomarker}")
        return None
    
    fig = px.violin(
        biomarker_data, 
        x='APPRDX', 
        y='TESTVALUE',
        color='APPRDX',
        title=f'{biomarker} Distribution by Diagnosis',
        labels={'TESTVALUE': f'{biomarker} Level', 'APPRDX': 'Diagnosis'},
        box=True
    )
    
    fig.update_layout(
        height=500,
        showlegend=False,
        xaxis_title="Diagnosis",
        yaxis_title=f"{biomarker} Level"
    )
    
    return fig

def create_longitudinal_plot(data, biomarker, cohorts=None):
    """Create longitudinal plot showing biomarker changes over time"""
    if cohorts:
        filtered_data = data[data['COHORT'].isin(cohorts)]
    else:
        filtered_data = data
    
    biomarker_data = filtered_data[filtered_data['TESTNAME'] == biomarker]
    
    if biomarker_data.empty:
        st.warning(f"No data available for {biomarker}")
        return None
    
    # Group by patient and visit to track longitudinal changes
    longitudinal_data = biomarker_data.groupby(['PATNO', 'APPRDX', 'EVENT_ID']).agg({
        'TESTVALUE': 'mean',
        'AGE': 'first'
    }).reset_index()
    
    fig = px.line(
        longitudinal_data, 
        x='AGE', 
        y='TESTVALUE',
        color='APPRDX',
        line_group='PATNO',
        title=f'{biomarker} Longitudinal Changes by Age',
        labels={'TESTVALUE': f'{biomarker} Level', 'AGE': 'Age (years)'}
    )
    
    fig.update_traces(opacity=0.6)
    fig.update_layout(
        height=500,
        xaxis_title="Age (years)",
        yaxis_title=f"{biomarker} Level"
    )
    
    return fig

def create_correlation_plot(data, biomarker_x, biomarker_y, clinical_score=None):
    """Create correlation plot between two biomarkers or biomarker and clinical score"""
    
    if clinical_score:
        # Biomarker vs clinical score correlation
        bio_data = data[data['TESTNAME'] == biomarker_x]
        
        if clinical_score in bio_data.columns:
            clean_data = bio_data.dropna(subset=['TESTVALUE', clinical_score])
            
            if clean_data.empty:
                st.warning(f"No overlapping data for {biomarker_x} and {clinical_score}")
                return None
            
            # Calculate correlation
            corr_coef, p_value = pearsonr(clean_data['TESTVALUE'], clean_data[clinical_score])
            
            fig = px.scatter(
                clean_data,
                x='TESTVALUE',
                y=clinical_score,
                color='APPRDX',
                title=f'{biomarker_x} vs {clinical_score} (r={corr_coef:.3f}, p={p_value:.3f})',
                labels={'TESTVALUE': f'{biomarker_x} Level', clinical_score: clinical_score},
                trendline="ols"
            )
            
        else:
            st.warning(f"Clinical score {clinical_score} not found in data")
            return None
    
    else:
        # Biomarker vs biomarker correlation
        bio_x_data = data[data['TESTNAME'] == biomarker_x][['PATNO', 'TESTVALUE', 'APPRDX']].rename(columns={'TESTVALUE': 'X_VALUE'})
        bio_y_data = data[data['TESTNAME'] == biomarker_y][['PATNO', 'TESTVALUE']].rename(columns={'TESTVALUE': 'Y_VALUE'})
        
        merged_bio = pd.merge(bio_x_data, bio_y_data, on='PATNO', how='inner')
        
        if merged_bio.empty:
            st.warning(f"No overlapping data for {biomarker_x} and {biomarker_y}")
            return None
        
        # Calculate correlation
        corr_coef, p_value = pearsonr(merged_bio['X_VALUE'], merged_bio['Y_VALUE'])
        
        fig = px.scatter(
            merged_bio,
            x='X_VALUE',
            y='Y_VALUE',
            color='APPRDX',
            title=f'{biomarker_x} vs {biomarker_y} (r={corr_coef:.3f}, p={p_value:.3f})',
            labels={'X_VALUE': f'{biomarker_x} Level', 'Y_VALUE': f'{biomarker_y} Level'},
            trendline="ols"
        )
    
    fig.update_layout(height=500)
    return fig

def create_correlation_heatmap(data, biomarkers):
    """Create correlation heatmap for multiple biomarkers"""
    
    # Create a matrix for correlations
    correlation_data = {}
    
    for biomarker in biomarkers:
        bio_data = data[data['TESTNAME'] == biomarker][['PATNO', 'TESTVALUE']].rename(columns={'TESTVALUE': biomarker})
        correlation_data[biomarker] = bio_data.set_index('PATNO')[biomarker]
    
    correlation_df = pd.DataFrame(correlation_data)
    
    if correlation_df.empty:
        st.warning("No data available for correlation heatmap")
        return None
    
    # Calculate correlation matrix
    corr_matrix = correlation_df.corr()
    
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        title="Biomarker Correlation Heatmap",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1
    )
    
    fig.update_layout(height=500)
    return fig

def main():
    """Main dashboard function"""
    
    # Title and description
    st.title("🧠 PPMI Parkinson's Disease Biomarker Dashboard")
    st.markdown("""
    Explore biomarker relationships in Parkinson's Disease progression using data from the 
    Parkinson's Progression Markers Initiative (PPMI).
    
    **Key Biomarkers:** Alpha-synuclein, Tau, P-tau, Amyloid-beta
    **Focus Projects:** 124 (α-syn), 125 (Aβ/tau), 159 (expanded Aβ/tau), 172 (RT-QuIC), 173 (seeding α-syn), 207 (SAA)
    """)
    
    # Load data
    with st.spinner("Loading PPMI data..."):
        merged_data, biomarker_summary, key_biomarkers, loader = load_ppmi_data()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Get available biomarkers
    available_biomarkers = sorted(merged_data['TESTNAME'].unique())
    key_biomarker_names = [
        'Alpha-synuclein', 'Total tau', 'Phospho-tau', 'Amyloid beta 1-42',
        'Amyloid beta 1-40', 'SAA', 'RT-QuIC'
    ]
    
    # Filter by biomarkers
    use_key_biomarkers = st.sidebar.checkbox("Use key biomarkers only", value=True)
    if use_key_biomarkers:
        biomarker_options = [b for b in available_biomarkers if any(key in b for key in key_biomarker_names)]
    else:
        biomarker_options = available_biomarkers
    
    # Cohort filters
    available_cohorts = sorted(merged_data['COHORT'].unique())
    selected_cohorts = st.sidebar.multiselect(
        "Select Cohorts",
        available_cohorts,
        default=available_cohorts
    )
    
    # Diagnosis filters
    available_diagnoses = sorted(merged_data['APPRDX'].unique())
    selected_diagnoses = st.sidebar.multiselect(
        "Select Diagnoses",
        available_diagnoses,
        default=available_diagnoses
    )
    
    # Filter data based on selections
    filtered_data = merged_data[
        (merged_data['COHORT'].isin(selected_cohorts)) &
        (merged_data['APPRDX'].isin(selected_diagnoses))
    ]
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Distribution Analysis", 
        "📈 Longitudinal Trends", 
        "🔗 Correlations", 
        "🌡️ Heatmaps",
        "📋 Data Summary"
    ])
    
    with tab1:
        st.header("Biomarker Distribution Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_biomarker = st.selectbox(
                "Select Biomarker for Analysis",
                biomarker_options,
                key="dist_biomarker"
            )
        
        with col2:
            plot_type = st.radio(
                "Plot Type",
                ["Box Plot", "Violin Plot"],
                key="dist_plot_type"
            )
        
        if selected_biomarker:
            if plot_type == "Box Plot":
                fig = create_biomarker_boxplot(filtered_data, selected_biomarker, selected_cohorts)
            else:
                fig = create_biomarker_violinplot(filtered_data, selected_biomarker, selected_cohorts)
            
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                # Show statistics
                biomarker_stats = filtered_data[filtered_data['TESTNAME'] == selected_biomarker].groupby('APPRDX')['TESTVALUE'].agg(['count', 'mean', 'std', 'median']).round(3)
                st.subheader("Summary Statistics")
                st.dataframe(biomarker_stats)
    
    with tab2:
        st.header("Longitudinal Biomarker Trends")
        
        selected_longitudinal_biomarker = st.selectbox(
            "Select Biomarker for Longitudinal Analysis",
            biomarker_options,
            key="long_biomarker"
        )
        
        if selected_longitudinal_biomarker:
            fig = create_longitudinal_plot(filtered_data, selected_longitudinal_biomarker, selected_cohorts)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("Biomarker Correlations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            biomarker_x = st.selectbox(
                "Select First Biomarker",
                biomarker_options,
                key="corr_bio_x"
            )
        
        with col2:
            biomarker_y = st.selectbox(
                "Select Second Biomarker",
                biomarker_options,
                key="corr_bio_y"
            )
        
        if biomarker_x and biomarker_y and biomarker_x != biomarker_y:
            fig = create_correlation_plot(filtered_data, biomarker_x, biomarker_y)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.header("Multi-Biomarker Correlation Heatmap")
        
        selected_heatmap_biomarkers = st.multiselect(
            "Select Biomarkers for Heatmap",
            biomarker_options,
            default=biomarker_options[:5] if len(biomarker_options) >= 5 else biomarker_options,
            key="heatmap_biomarkers"
        )
        
        if len(selected_heatmap_biomarkers) >= 2:
            fig = create_correlation_heatmap(filtered_data, selected_heatmap_biomarkers)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Please select at least 2 biomarkers for correlation heatmap")
    
    with tab5:
        st.header("Data Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Dataset Overview")
            st.write(f"**Total Records:** {len(filtered_data):,}")
            st.write(f"**Unique Patients:** {filtered_data['PATNO'].nunique():,}")
            st.write(f"**Biomarkers Available:** {filtered_data['TESTNAME'].nunique()}")
            st.write(f"**Cohorts:** {', '.join(selected_cohorts)}")
            
        with col2:
            st.subheader("Diagnosis Distribution")
            diagnosis_counts = filtered_data['APPRDX'].value_counts()
            st.bar_chart(diagnosis_counts)
        
        # Biomarker availability
        st.subheader("Biomarker Data Availability")
        biomarker_counts = filtered_data.groupby('TESTNAME').agg({
            'PATNO': 'nunique',
            'TESTVALUE': 'count'
        }).rename(columns={'PATNO': 'Unique Patients', 'TESTVALUE': 'Total Measurements'})
        st.dataframe(biomarker_counts.sort_values('Unique Patients', ascending=False))

if __name__ == "__main__":
    main()