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
    loader = PPMIDataLoader()
    merged_data = loader.create_merged_dataset()
    biomarker_summary = loader.get_biomarker_summary()
    key_biomarkers = loader.get_key_biomarkers_data()
    return merged_data, biomarker_summary, key_biomarkers, loader

def create_biomarker_boxplot(data, biomarker, cohorts=None):
    """Create box plot for biomarker levels by diagnosis"""
    if cohorts is None:
        cohorts = ['HC', 'PD', 'Prodromal PD']
    
    plot_data = data[
        (data['TESTNAME'] == biomarker) & 
        (data['COHORT_SIMPLE'].isin(cohorts)) &
        (data['TESTVALUE_NUMERIC'].notna())
    ]
    
    if len(plot_data) == 0:
        st.warning(f"No data available for {biomarker}")
        return None
    
    fig = px.box(
        plot_data,
        x='COHORT_SIMPLE',
        y='TESTVALUE_NUMERIC',
        color='COHORT_SIMPLE',
        title=f'{biomarker} Levels by Diagnosis',
        labels={
            'COHORT_SIMPLE': 'Diagnosis',
            'TESTVALUE_NUMERIC': f'{biomarker} Level'
        },
        color_discrete_map={
            'HC': '#2E8B57',
            'PD': '#DC143C', 
            'Prodromal PD': '#FF8C00',
            'SWEDD': '#9370DB'
        }
    )
    
    fig.update_layout(
        height=500,
        showlegend=True,
        title_x=0.5
    )
    
    # Add statistical annotations
    cohort_data = {}
    for cohort in cohorts:
        cohort_values = plot_data[plot_data['COHORT_SIMPLE'] == cohort]['TESTVALUE_NUMERIC'].dropna()
        if len(cohort_values) > 0:
            cohort_data[cohort] = cohort_values
    
    # Perform statistical tests between groups
    if len(cohort_data) >= 2:
        cohort_names = list(cohort_data.keys())
        for i in range(len(cohort_names)):
            for j in range(i+1, len(cohort_names)):
                if cohort_names[i] in cohort_data and cohort_names[j] in cohort_data:
                    stat, p_value = stats.mannwhitneyu(
                        cohort_data[cohort_names[i]], 
                        cohort_data[cohort_names[j]], 
                        alternative='two-sided'
                    )
                    significance = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else "ns"
                    st.write(f"{cohort_names[i]} vs {cohort_names[j]}: p={p_value:.4f} {significance}")
    
    return fig

def create_biomarker_violinplot(data, biomarker, cohorts=None):
    """Create violin plot for biomarker levels by diagnosis"""
    if cohorts is None:
        cohorts = ['HC', 'PD', 'Prodromal PD']
    
    plot_data = data[
        (data['TESTNAME'] == biomarker) & 
        (data['COHORT_SIMPLE'].isin(cohorts)) &
        (data['TESTVALUE_NUMERIC'].notna())
    ]
    
    if len(plot_data) == 0:
        st.warning(f"No data available for {biomarker}")
        return None
    
    fig = px.violin(
        plot_data,
        x='COHORT_SIMPLE',
        y='TESTVALUE_NUMERIC',
        color='COHORT_SIMPLE',
        box=True,  # Show box plot inside violin
        title=f'{biomarker} Levels by Diagnosis (Violin Plot)',
        labels={
            'COHORT_SIMPLE': 'Diagnosis',
            'TESTVALUE_NUMERIC': f'{biomarker} Level'
        },
        color_discrete_map={
            'HC': '#2E8B57',
            'PD': '#DC143C', 
            'Prodromal PD': '#FF8C00',
            'SWEDD': '#9370DB'
        }
    )
    
    fig.update_layout(
        height=500,
        showlegend=True,
        title_x=0.5
    )
    
    # Add statistical annotations
    cohort_data = {}
    for cohort in cohorts:
        cohort_values = plot_data[plot_data['COHORT_SIMPLE'] == cohort]['TESTVALUE_NUMERIC'].dropna()
        if len(cohort_values) > 0:
            cohort_data[cohort] = cohort_values
    
    # Perform statistical tests between groups
    if len(cohort_data) >= 2:
        cohort_names = list(cohort_data.keys())
        for i in range(len(cohort_names)):
            for j in range(i+1, len(cohort_names)):
                if cohort_names[i] in cohort_data and cohort_names[j] in cohort_data:
                    stat, p_value = stats.mannwhitneyu(
                        cohort_data[cohort_names[i]], 
                        cohort_data[cohort_names[j]], 
                        alternative='two-sided'
                    )
                    significance = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else "ns"
                    st.write(f"{cohort_names[i]} vs {cohort_names[j]}: p={p_value:.4f} {significance}")
    
    return fig

def create_longitudinal_plot(data, biomarker, cohorts=None):
    """Create longitudinal plot showing biomarker changes over time"""
    if cohorts is None:
        cohorts = ['HC', 'PD', 'Prodromal PD']
    
    plot_data = data[
        (data['TESTNAME'] == biomarker) & 
        (data['COHORT_SIMPLE'].isin(cohorts)) &
        (data['TESTVALUE_NUMERIC'].notna()) &
        (data['AGE_AT_BIOMARKER'].notna())
    ]
    
    if len(plot_data) == 0:
        st.warning(f"No longitudinal data available for {biomarker}")
        return None
    
    fig = px.scatter(
        plot_data,
        x='AGE_AT_BIOMARKER',
        y='TESTVALUE_NUMERIC',
        color='COHORT_SIMPLE',
        trendline='ols',
        title=f'{biomarker} Levels vs Age',
        labels={
            'AGE_AT_BIOMARKER': 'Age at Biomarker Collection',
            'TESTVALUE_NUMERIC': f'{biomarker} Level',
            'COHORT_SIMPLE': 'Diagnosis'
        },
        color_discrete_map={
            'HC': '#2E8B57',
            'PD': '#DC143C', 
            'Prodromal PD': '#FF8C00',
            'SWEDD': '#9370DB'
        }
    )
    
    fig.update_layout(
        height=500,
        title_x=0.5
    )
    
    # Calculate correlations for each cohort
    correlations = {}
    for cohort in cohorts:
        cohort_data = plot_data[plot_data['COHORT_SIMPLE'] == cohort]
        if len(cohort_data) > 5:  # Need minimum data points for correlation
            age_vals = cohort_data['AGE_AT_BIOMARKER'].values
            biomarker_vals = cohort_data['TESTVALUE_NUMERIC'].values
            
            # Remove any remaining NaN values
            mask = ~(np.isnan(age_vals) | np.isnan(biomarker_vals))
            if np.sum(mask) > 5:
                corr, p_val = pearsonr(age_vals[mask], biomarker_vals[mask])
                correlations[cohort] = (corr, p_val)
    
    # Display correlation results
    if correlations:
        st.write("**Age Correlations:**")
        for cohort, (corr, p_val) in correlations.items():
            significance = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
            st.write(f"{cohort}: r={corr:.3f}, p={p_val:.4f} {significance}")
    
    return fig

def create_correlation_plot(data, biomarker_x, biomarker_y, clinical_score=None):
    """Create correlation plot between biomarkers or biomarker vs clinical score"""
    
    if clinical_score:
        # Biomarker vs clinical score correlation
        bio_data = data[
            (data['TESTNAME'] == biomarker_x) & 
            (data['TESTVALUE_NUMERIC'].notna()) &
            (data[clinical_score].notna())
        ]
        
        if len(bio_data) == 0:
            st.warning(f"No data available for {biomarker_x} vs {clinical_score}")
            return None
        
        # Handle duplicates by aggregating per patient
        bio_agg = bio_data.groupby(['PATNO', 'COHORT_SIMPLE']).agg({
            'TESTVALUE_NUMERIC': 'mean',
            clinical_score: 'mean'
        }).reset_index()
        
        fig = px.scatter(
            bio_agg,
            x='TESTVALUE_NUMERIC',
            y=clinical_score,
            color='COHORT_SIMPLE',
            trendline='ols',
            title=f'{biomarker_x} vs {clinical_score}',
            labels={
                'TESTVALUE_NUMERIC': f'{biomarker_x} Level',
                clinical_score: clinical_score,
                'COHORT_SIMPLE': 'Diagnosis'
            },
            color_discrete_map={
                'HC': '#2E8B57',
                'PD': '#DC143C', 
                'Prodromal PD': '#FF8C00',
                'SWEDD': '#9370DB'
            }
        )
        
        # Calculate correlation
        x_vals = bio_agg['TESTVALUE_NUMERIC'].values
        y_vals = bio_agg[clinical_score].values
        mask = ~(np.isnan(x_vals) | np.isnan(y_vals))
        if np.sum(mask) > 5:
            corr, p_val = pearsonr(x_vals[mask], y_vals[mask])
            st.write(f"**Correlation:** r={corr:.3f}, p={p_val:.4f}")
        
    else:
        # Biomarker vs biomarker correlation
        bio1_data = data[
            (data['TESTNAME'] == biomarker_x) & 
            (data['TESTVALUE_NUMERIC'].notna())
        ][['PATNO', 'TESTVALUE_NUMERIC', 'COHORT_SIMPLE']].rename(
            columns={'TESTVALUE_NUMERIC': 'biomarker_x'}
        )
        
        bio2_data = data[
            (data['TESTNAME'] == biomarker_y) & 
            (data['TESTVALUE_NUMERIC'].notna())
        ][['PATNO', 'TESTVALUE_NUMERIC']].rename(
            columns={'TESTVALUE_NUMERIC': 'biomarker_y'}
        )
        
        # Handle duplicates by taking mean values per patient
        bio1_agg = bio1_data.groupby(['PATNO', 'COHORT_SIMPLE'])['biomarker_x'].mean().reset_index()
        bio2_agg = bio2_data.groupby('PATNO')['biomarker_y'].mean().reset_index()
        
        merged_bio = bio1_agg.merge(bio2_agg, on='PATNO')
        
        if len(merged_bio) == 0:
            st.warning(f"No paired data available for {biomarker_x} vs {biomarker_y}")
            return None
        
        fig = px.scatter(
            merged_bio,
            x='biomarker_x',
            y='biomarker_y',
            color='COHORT_SIMPLE',
            trendline='ols',
            title=f'{biomarker_x} vs {biomarker_y}',
            labels={
                'biomarker_x': f'{biomarker_x} Level',
                'biomarker_y': f'{biomarker_y} Level',
                'COHORT_SIMPLE': 'Diagnosis'
            },
            color_discrete_map={
                'HC': '#2E8B57',
                'PD': '#DC143C', 
                'Prodromal PD': '#FF8C00',
                'SWEDD': '#9370DB'
            }
        )
        
        # Calculate correlation
        x_vals = merged_bio['biomarker_x'].values
        y_vals = merged_bio['biomarker_y'].values
        mask = ~(np.isnan(x_vals) | np.isnan(y_vals))
        if np.sum(mask) > 5:
            corr, p_val = pearsonr(x_vals[mask], y_vals[mask])
            st.write(f"**Correlation:** r={corr:.3f}, p={p_val:.4f}")
    
    fig.update_layout(height=500, title_x=0.5)
    return fig

def create_correlation_heatmap(data, biomarkers, clinical_scores=None):
    """Create correlation heatmap between multiple biomarkers and clinical variables"""
    
    # Create correlation matrix data
    correlation_data = {}
    
    # Add biomarker data
    for biomarker in biomarkers:
        bio_data = data[
            (data['TESTNAME'] == biomarker) & 
            (data['TESTVALUE_NUMERIC'].notna())
        ][['PATNO', 'TESTVALUE_NUMERIC']].rename(
            columns={'TESTVALUE_NUMERIC': biomarker}
        )
        
        if len(bio_data) > 0:
            # Handle duplicate patients by taking mean values
            bio_data_agg = bio_data.groupby('PATNO')[biomarker].mean()
            correlation_data[biomarker] = bio_data_agg
    
    # Add clinical scores if provided
    if clinical_scores:
        for score in clinical_scores:
            if score in data.columns:
                score_data = data[data[score].notna()][['PATNO', score]].drop_duplicates('PATNO')
                if len(score_data) > 0:
                    correlation_data[score] = score_data.set_index('PATNO')[score]
    
    if len(correlation_data) < 2:
        st.warning("Insufficient data for correlation heatmap")
        return None
    
    # Create DataFrame for correlation
    corr_df = pd.DataFrame(correlation_data)
    
    # Calculate correlation matrix
    corr_matrix = corr_df.corr()
    
    # Create heatmap
    fig = px.imshow(
        corr_matrix,
        title="Biomarker and Clinical Score Correlations",
        color_continuous_scale="RdBu_r",
        aspect="auto",
        text_auto=True
    )
    
    fig.update_layout(
        height=600,
        title_x=0.5,
        xaxis_title="Variables",
        yaxis_title="Variables"
    )
    
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
        'CSF Alpha-synuclein',
        'ABeta 1-42',
        'pTau',
        'tTau',
        'ABeta42',
        'ABeta40',
        'pTau181'
    ]
    # Filter to only available key biomarkers
    available_key_biomarkers = [b for b in key_biomarker_names if b in available_biomarkers]
    
    # Cohort filter
    cohorts = st.sidebar.multiselect(
        "Select Cohorts",
        options=['HC', 'PD', 'Prodromal PD', 'SWEDD'],
        default=['HC', 'PD', 'Prodromal PD']
    )
    
    # Age filter
    age_range = st.sidebar.slider(
        "Age Range",
        min_value=30,
        max_value=90,
        value=(40, 80),
        step=5
    )
    
    # Sex filter
    sex_options = merged_data['SEX_LABEL'].dropna().unique()
    selected_sex = st.sidebar.multiselect(
        "Select Sex",
        options=sex_options,
        default=list(sex_options)
    )
    
    # Genetic risk filter
    risk_groups = merged_data['RISK_GROUP'].dropna().unique()
    selected_risk = st.sidebar.multiselect(
        "Genetic Risk Groups",
        options=risk_groups,
        default=list(risk_groups)
    )
    
    # Apply filters
    filtered_data = merged_data[
        (merged_data['COHORT_SIMPLE'].isin(cohorts)) &
        (merged_data['AGE_AT_BIOMARKER'].between(age_range[0], age_range[1])) &
        (merged_data['SEX_LABEL'].isin(selected_sex)) &
        (merged_data['RISK_GROUP'].isin(selected_risk))
    ]
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Biomarker Levels", 
        "📈 Longitudinal Analysis", 
        "🔗 Correlations", 
        "🌡️ Heatmaps",
        "📋 Data Summary"
    ])
    
    with tab1:
        st.header("Biomarker Levels by Diagnosis")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            selected_biomarker = st.selectbox(
                "Select Biomarker",
                options=available_key_biomarkers,
                index=0 if available_key_biomarkers else None
            )
            
            plot_type = st.radio("Plot Type", ["Box Plot", "Violin Plot"])
        
        with col1:
            if selected_biomarker:
                if plot_type == "Box Plot":
                    fig = create_biomarker_boxplot(filtered_data, selected_biomarker, cohorts)
                else:  # Violin Plot
                    fig = create_biomarker_violinplot(filtered_data, selected_biomarker, cohorts)
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Longitudinal Biomarker Changes")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            long_biomarker = st.selectbox(
                "Select Biomarker",
                options=available_key_biomarkers,
                key="longitudinal",
                index=0 if available_key_biomarkers else None
            )
        
        with col1:
            if long_biomarker:
                fig = create_longitudinal_plot(filtered_data, long_biomarker, cohorts)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("Biomarker Correlations")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            correlation_type = st.radio(
                "Correlation Type",
                ["Biomarker vs Biomarker", "Biomarker vs Clinical Score"]
            )
            
            if correlation_type == "Biomarker vs Biomarker":
                biomarker_x = st.selectbox("X-axis Biomarker", available_key_biomarkers, key="corr_x")
                biomarker_y = st.selectbox("Y-axis Biomarker", available_key_biomarkers, key="corr_y", index=1 if len(available_key_biomarkers) > 1 else 0)
                clinical_score = None
            else:
                biomarker_x = st.selectbox("Biomarker", available_key_biomarkers, key="corr_bio")
                biomarker_y = None
                clinical_scores = ['NP3TOT', 'NP3BRADY', 'NP3RIGN', 'NP3PTRMR', 'NP3PTRML']
                available_clinical = [s for s in clinical_scores if s in merged_data.columns]
                clinical_score = st.selectbox("Clinical Score", available_clinical) if available_clinical else None
        
        with col1:
            if correlation_type == "Biomarker vs Biomarker" and biomarker_x and biomarker_y:
                fig = create_correlation_plot(filtered_data, biomarker_x, biomarker_y)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            elif correlation_type == "Biomarker vs Clinical Score" and biomarker_x and clinical_score:
                fig = create_correlation_plot(filtered_data, biomarker_x, None, clinical_score)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.header("Correlation Heatmaps")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            selected_biomarkers_heatmap = st.multiselect(
                "Select Biomarkers",
                options=available_key_biomarkers,
                default=available_key_biomarkers[:4] if len(available_key_biomarkers) >= 4 else available_key_biomarkers
            )
            
            clinical_scores = ['NP3TOT', 'NP3BRADY', 'NP3RIGN', 'NP3PTRMR', 'NP3PTRML']
            available_clinical = [s for s in clinical_scores if s in merged_data.columns]
            selected_clinical = st.multiselect(
                "Include Clinical Scores",
                options=available_clinical,
                default=available_clinical[:2] if len(available_clinical) >= 2 else available_clinical
            )
        
        with col1:
            if len(selected_biomarkers_heatmap) >= 2:
                fig = create_correlation_heatmap(filtered_data, selected_biomarkers_heatmap, selected_clinical)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.header("Data Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Dataset Overview")
            st.write(f"**Total Records:** {len(filtered_data):,}")
            st.write(f"**Unique Patients:** {filtered_data['PATNO'].nunique():,}")
            st.write(f"**Unique Biomarkers:** {filtered_data['TESTNAME'].nunique()}")
            
            st.subheader("Cohort Distribution")
            cohort_counts = filtered_data['COHORT_SIMPLE'].value_counts()
            st.write(cohort_counts)
        
        with col2:
            st.subheader("Available Biomarkers")
            biomarker_counts = filtered_data['TESTNAME'].value_counts().head(10)
            st.write(biomarker_counts)
            
            st.subheader("Data Quality")
            missing_values = filtered_data['TESTVALUE_NUMERIC'].isna().sum()
            st.write(f"**Missing Values:** {missing_values:,} ({missing_values/len(filtered_data)*100:.1f}%)")

if __name__ == "__main__":
    main()