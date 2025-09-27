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
import plotly.express as px
from data_loader import PPMIDataLoader
import numpy as np
from scipy.stats import mannwhitneyu, pearsonr

# --- Custom CSS ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    .st-emotion-cache-16txtl3 {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data():
    """Load, merge, and cache data to prevent reloading on every interaction."""
    print("--- Initializing Data Loading Process ---")
    loader = PPMIDataLoader()
    merged_data = loader.create_merged_dataset()
    
    if merged_data is None or merged_data.empty:
        print("ERROR: Merged data is empty. Dashboard cannot proceed.")
        return pd.DataFrame(), pd.DataFrame(), []

    # Calculate PD-ProS score
    merged_data = loader.calculate_pd_pros(merged_data)
    
    biomarker_summary = loader.get_biomarker_summary()
    
    # Define key biomarkers after data is loaded
    all_biomarkers = merged_data['TESTNAME'].dropna().unique()
    key_biomarkers = [
        'CSF Alpha-synuclein', 'ABeta 1-42', 'pTau', 'tTau', 
        'ABeta42', 'ABeta40', 'pTau181', 'NEFL', 'GFAP', 'UCHL1'
    ]
    available_key_biomarkers = [b for b in key_biomarkers if b in all_biomarkers]
    
    print("--- Data Loading and Preprocessing Complete ---")
    return merged_data, biomarker_summary, available_key_biomarkers

# --- Plotting Functions ---
def create_boxplot(data, biomarker, cohorts):
    """Generate a box plot for a selected biomarker across cohorts."""
    plot_data = data[data['TESTNAME'] == biomarker].dropna(subset=['TESTVALUE_NUMERIC', 'COHORT_SIMPLE'])
    if plot_data.empty:
        return None
    
    fig = px.box(
        plot_data,
        x='COHORT_SIMPLE',
        y='TESTVALUE_NUMERIC',
        color='COHORT_SIMPLE',
        title=f'Distribution of {biomarker} by Diagnosis',
        labels={'COHORT_SIMPLE': 'Cohort', 'TESTVALUE_NUMERIC': 'Biomarker Level'},
        category_orders={'COHORT_SIMPLE': cohorts}
    )
    return fig

def create_longitudinal_plot(data, biomarker):
    """Generate a scatter plot showing biomarker levels over time."""
    plot_data = data[data['TESTNAME'] == biomarker].dropna(subset=['AGE_AT_BIOMARKER', 'TESTVALUE_NUMERIC'])
    if plot_data.empty:
        return None
        
    fig = px.scatter(
        plot_data,
        x='AGE_AT_BIOMARKER',
        y='TESTVALUE_NUMERIC',
        color='COHORT_SIMPLE',
        trendline='ols',
        title=f'Longitudinal Trend of {biomarker}',
        labels={'AGE_AT_BIOMARKER': 'Age at Visit', 'TESTVALUE_NUMERIC': 'Biomarker Level'}
    )
    return fig

def create_correlation_plot(data, x_var, y_var):
    """Generate a scatter plot to show correlation between two variables."""
    if x_var not in data.columns or y_var not in data.columns:
        st.warning(f"One or both variables ({x_var}, {y_var}) not found in the data.")
        return None

    plot_data = data.dropna(subset=[x_var, y_var])
    if plot_data.empty:
        return None
        
    fig = px.scatter(
        plot_data,
        x=x_var,
        y=y_var,
        color='COHORT_SIMPLE',
        trendline='ols',
        title=f'Correlation between {x_var} and {y_var}',
        labels={x_var: x_var, y_var: y_var}
    )
    return fig

# --- Main Dashboard UI ---
def main():
    st.title("🧠 PPMI Advanced Biomarker Dashboard")
    st.markdown("An interactive tool for exploring Parkinson's disease biomarker data from the PPMI study.")

    # Load data
    data, summary, key_biomarkers = load_data()

    if data.empty:
        st.error("Failed to load data. Please check the data files and paths in `data_loader.py`.")
        st.info("Expected files:\n- `Current_Biospecimen_Analysis_Results_18Sep2025.csv`\n- `Demographics_18Sep2025.csv`\n- `Participant_Genetic_Status_for_Selected_PD-Associated_Variants.csv`\n- Neuropsychiatric and UPDRS data files.")
        return

    # --- Sidebar Filters ---
    st.sidebar.header("Global Filters")
    
    # Cohort Filter
    cohort_options = data['COHORT_SIMPLE'].dropna().unique()
    selected_cohorts = st.sidebar.multiselect("Filter by Cohort", cohort_options, default=cohort_options)
    
    # Age Filter
    min_age, max_age = int(data['AGE_AT_BIOMARKER'].min()), int(data['AGE_AT_BIOMARKER'].max())
    age_range = st.sidebar.slider("Filter by Age", min_age, max_age, (min_age, max_age))
    
    # Genetic Risk Filter
    risk_options = data['RISK_GROUP'].dropna().unique()
    selected_risk = st.sidebar.multiselect("Filter by Genetic Risk", risk_options, default=risk_options)

    # Apply filters
    filtered_data = data[
        (data['COHORT_SIMPLE'].isin(selected_cohorts)) &
        (data['AGE_AT_BIOMARKER'].between(age_range[0], age_range[1])) &
        (data['RISK_GROUP'].isin(selected_risk))
    ]

    # --- Dashboard Tabs ---
    tab_titles = [
        "Biomarker Distribution", 
        "Longitudinal Analysis", 
        "Correlation Analysis",
        "Neuropsychiatric & Motor Scores",
        "PD Proteomic Score (PD-ProS)",
        "Data Explorer"
    ]
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tab_titles)

    # --- Tab 1: Biomarker Distribution ---
    with tab1:
        st.header("Biomarker Distribution by Cohort")
        biomarker_to_plot = st.selectbox("Select a Biomarker", key_biomarkers)
        if biomarker_to_plot:
            fig = create_boxplot(filtered_data, biomarker_to_plot, selected_cohorts)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"No data available for {biomarker_to_plot} with the current filters.")

    # --- Tab 2: Longitudinal Analysis ---
    with tab2:
        st.header("Longitudinal Biomarker Trends")
        long_biomarker = st.selectbox("Select a Biomarker for Longitudinal View", key_biomarkers)
        if long_biomarker:
            fig = create_longitudinal_plot(filtered_data, long_biomarker)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"No longitudinal data for {long_biomarker}.")

    # --- Tab 3: Correlation Analysis ---
    with tab3:
        st.header("Biomarker vs. Biomarker Correlation")
        col1, col2 = st.columns(2)
        with col1:
            x_biomarker = st.selectbox("X-axis Biomarker", key_biomarkers, index=0)
        with col2:
            y_biomarker = st.selectbox("Y-axis Biomarker", key_biomarkers, index=1)
        
        # Pivot data for correlation
        if x_biomarker and y_biomarker:
            if x_biomarker == y_biomarker:
                st.warning("Please select different biomarkers for the X and Y axes.")
            else:
                pivot_x = filtered_data[filtered_data['TESTNAME'] == x_biomarker].groupby('PATNO')['TESTVALUE_NUMERIC'].mean().rename(x_biomarker)
                pivot_y = filtered_data[filtered_data['TESTNAME'] == y_biomarker].groupby('PATNO')['TESTVALUE_NUMERIC'].mean().rename(y_biomarker)
                corr_data = pd.concat([pivot_x, pivot_y], axis=1).dropna()
                
                # Add cohort info back
                cohort_info = filtered_data[['PATNO', 'COHORT_SIMPLE']].drop_duplicates('PATNO').set_index('PATNO')
                corr_data = corr_data.join(cohort_info)

                fig = create_correlation_plot(corr_data, x_biomarker, y_biomarker)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Not enough data to plot correlation.")

    # --- Tab 4: Neuropsychiatric & Motor Scores ---
    with tab4:
        st.header("Neuropsychiatric and Motor Score Analysis")
        score_options = ['GDSTOTAL', 'STAI_S_TOT', 'STAI_T_TOT', 'QUIP_TOT', 'ICD_PRESENT', 'NP3TOT', 'NP3BRADY']
        available_scores = [s for s in score_options if s in filtered_data.columns and filtered_data[s].notna().any()]
        
        if not available_scores:
            st.warning("No neuropsychiatric or motor score data available with current filters.")
        else:
            selected_score = st.selectbox("Select a Score to Analyze", available_scores)
            
            # Box plot for the score
            fig = px.box(
                filtered_data.dropna(subset=[selected_score]),
                x='COHORT_SIMPLE',
                y=selected_score,
                color='COHORT_SIMPLE',
                title=f'Distribution of {selected_score} by Cohort'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Correlation with a biomarker
            st.subheader(f"Correlation between {selected_score} and a Biomarker")
            corr_biomarker = st.selectbox("Select Biomarker for Correlation", key_biomarkers, key='neuro_corr')
            
            pivot_score = filtered_data.groupby('PATNO')[selected_score].mean()
            pivot_biomarker = filtered_data[filtered_data['TESTNAME'] == corr_biomarker].groupby('PATNO')['TESTVALUE_NUMERIC'].mean().rename(corr_biomarker)
            
            corr_data_neuro = pd.concat([pivot_score, pivot_biomarker], axis=1).dropna()
            cohort_info = filtered_data[['PATNO', 'COHORT_SIMPLE']].drop_duplicates('PATNO').set_index('PATNO')
            corr_data_neuro = corr_data_neuro.join(cohort_info)

            fig_corr = create_correlation_plot(corr_data_neuro, selected_score, corr_biomarker)
            if fig_corr:
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.warning("Not enough data for correlation plot.")

    # --- Tab 5: PD Proteomic Score (PD-ProS) ---
    with tab5:
        st.header("PD Proteomic Score (PD-ProS) Analysis")
        if 'PD_PROS' not in filtered_data.columns or filtered_data['PD_PROS'].isna().all():
            st.warning("PD-ProS score could not be calculated. Ensure the required proteins are in the dataset: NEFL, GFAP, UCHL1, etc.")
        else:
            # Box plot for PD-ProS
            fig_pros_box = px.box(
                filtered_data.dropna(subset=['PD_PROS']),
                x='COHORT_SIMPLE',
                y='PD_PROS',
                color='COHORT_SIMPLE',
                title='Distribution of PD-ProS by Cohort'
            )
            st.plotly_chart(fig_pros_box, use_container_width=True)

            # Correlation with UPDRS total score
            st.subheader("PD-ProS Correlation with Motor Severity (NP3TOT)")
            if 'NP3TOT' in filtered_data.columns and filtered_data['NP3TOT'].notna().any():
                pros_corr_data = filtered_data.groupby('PATNO').agg({
                    'PD_PROS': 'mean',
                    'NP3TOT': 'mean',
                    'COHORT_SIMPLE': 'first'
                }).dropna()

                fig_pros_corr = create_correlation_plot(pros_corr_data, 'PD_PROS', 'NP3TOT')
                if fig_pros_corr:
                    st.plotly_chart(fig_pros_corr, use_container_width=True)
                else:
                    st.warning("Not enough data to plot PD-ProS vs NP3TOT correlation.")
            else:
                st.warning("NP3TOT (UPDRS Part III Total) data not available for correlation.")

    # --- Tab 6: Data Explorer ---
    with tab6:
        st.header("Data Explorer")
        st.dataframe(filtered_data.head(1000))
        st.subheader("Data Summary")
        st.dataframe(summary)

if __name__ == "__main__":
    main()
