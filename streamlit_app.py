import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import PPMIDataLoader
import numpy as np

# --- Page Configuration ---
st.set_page_config(
    page_title="PPMI Biomarker Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
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
    loader = PPMIDataLoader()
    merged_data = loader.create_merged_dataset()
    if merged_data is None or merged_data.empty:
        return pd.DataFrame(), pd.DataFrame(), []
    merged_data = loader.calculate_pd_pros(merged_data)
    biomarker_summary = loader.get_biomarker_summary()
    all_biomarkers = merged_data['TESTNAME'].dropna().unique()
    key_biomarkers = sorted([
        'CSF Alpha-synuclein', 'ABeta 1-42', 'pTau', 'tTau', 
        'ABeta42', 'ABeta40', 'pTau181', 'NEFL', 'GFAP', 'UCHL1'
    ])
    available_key_biomarkers = [b for b in key_biomarkers if b in all_biomarkers]
    return merged_data, biomarker_summary, available_key_biomarkers

# --- Plotting Functions ---
def create_violin_plot(data, biomarker, cohorts):
    plot_data = data[data['TESTNAME'] == biomarker].dropna(subset=['TESTVALUE_NUMERIC', 'COHORT_SIMPLE'])
    if plot_data.empty: return None
    return px.violin(plot_data, x='COHORT_SIMPLE', y='TESTVALUE_NUMERIC', color='COHORT_SIMPLE',
                   box=True,  # Show box plot inside violin
                   title=f'Distribution of {biomarker} by Diagnosis',
                   labels={'COHORT_SIMPLE': 'Cohort', 'TESTVALUE_NUMERIC': 'Biomarker Level'},
                   category_orders={'COHORT_SIMPLE': cohorts})

def create_longitudinal_plot(data, biomarker):
    plot_data = data[data['TESTNAME'] == biomarker].dropna(subset=['AGE_AT_BIOMARKER', 'TESTVALUE_NUMERIC'])
    if plot_data.empty: return None
    return px.scatter(plot_data, x='AGE_AT_BIOMARKER', y='TESTVALUE_NUMERIC', color='COHORT_SIMPLE',
                      trendline='ols', title=f'Longitudinal Trend of {biomarker}',
                      labels={'AGE_AT_BIOMARKER': 'Age at Visit', 'TESTVALUE_NUMERIC': 'Biomarker Level'})

def create_correlation_plot(data, x_var, y_var):
    if x_var not in data.columns or y_var not in data.columns: return None
    plot_data = data.dropna(subset=[x_var, y_var])
    if plot_data.empty: return None
    return px.scatter(plot_data, x=x_var, y=y_var, color='COHORT_SIMPLE', trendline='ols',
                      title=f'Correlation between {x_var} and {y_var}',
                      labels={x_var: x_var, y_var: y_var})

# --- UI Sections ---
def show_home_page():
    st.title("Welcome to the PPMI Biomarker Dashboard!")
    st.markdown("""
    This interactive dashboard provides a comprehensive platform for exploring the Parkinson's Progression Markers Initiative (PPMI) dataset. It is designed to help researchers, clinicians, and data scientists visualize and analyze the complex relationships between biomarkers, clinical assessments, and patient demographics in Parkinson's disease.

    ### How to Use This Dashboard
    Select the **Dashboard** from the sidebar to begin exploring the data. You will find several tabs, each offering a unique perspective:

    - **Biomarker Distribution**: Compare biomarker levels across different diagnostic groups (Parkinson's, Healthy Control, etc.).
    - **Longitudinal Analysis**: Track how biomarkers change over time for individuals or cohorts.
    - **Correlation Analysis**: Explore the relationships between different biomarkers or between biomarkers and clinical scores.
    - **PD Proteomic Score (PD-ProS)**: Investigate a promising 14-protein panel for tracking disease progression.
    - **Data Explorer**: View the raw data table with the applied filters.

    ### About the Data
    The data is a curated subset of the PPMI database, a landmark study to identify biomarkers of Parkinson's disease progression.
    """)

def show_dashboard_page():
    st.title("🧠 PPMI Advanced Biomarker Dashboard")
    data, summary, key_biomarkers = load_data()

    if data.empty:
        st.error("Failed to load data. Please check the data files and `data_loader.py`.")
        return

    st.sidebar.header("Global Filters")
    cohort_options = data['COHORT_SIMPLE'].dropna().unique()
    selected_cohorts = st.sidebar.multiselect("Filter by Cohort", cohort_options, default=list(cohort_options))
    
    min_age, max_age = int(data['AGE_AT_BIOMARKER'].min()), int(data['AGE_AT_BIOMARKER'].max())
    age_range = st.sidebar.slider("Filter by Age", min_age, max_age, (min_age, max_age))
    
    risk_options = data['RISK_GROUP'].dropna().unique()
    if len(risk_options) > 0:
        selected_risk = st.sidebar.multiselect("Filter by Genetic Risk", risk_options, default=list(risk_options))
    else:
        selected_risk = []

    # Apply filters
    filtered_data = data[
        (data['COHORT_SIMPLE'].isin(selected_cohorts)) & 
        (data['AGE_AT_BIOMARKER'].between(age_range[0], age_range[1])) &
        (data['RISK_GROUP'].isin(selected_risk if selected_risk else data['RISK_GROUP'].unique()))
    ]

    tab_titles = ["Biomarker Distribution", "Longitudinal Analysis", "Correlation Analysis", "PD Proteomic Score (PD-ProS)", "Data Explorer"]
    tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_titles)

    with tab1:
        st.header("Biomarker Distribution by Cohort")
        biomarker_to_plot = st.selectbox("Select a Biomarker", key_biomarkers)
        if biomarker_to_plot:
            fig = create_violin_plot(filtered_data, biomarker_to_plot, selected_cohorts)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"No data available for {biomarker_to_plot} with the current filters.")

    with tab2:
        st.header("Longitudinal Biomarker Trends")
        long_biomarker = st.selectbox("Select a Biomarker for Longitudinal View", key_biomarkers)
        if long_biomarker:
            fig = create_longitudinal_plot(filtered_data, long_biomarker)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"No longitudinal data for {long_biomarker}.")

    with tab3:
        st.header("Biomarker vs. Biomarker Correlation")
        col1, col2 = st.columns(2)
        x_biomarker = col1.selectbox("X-axis Biomarker", key_biomarkers, index=0)
        y_biomarker = col2.selectbox("Y-axis Biomarker", key_biomarkers, index=1)
        
        if x_biomarker and y_biomarker:
            if x_biomarker == y_biomarker:
                st.warning("Please select different biomarkers for the X and Y axes.")
            else:
                pivot_x = filtered_data[filtered_data['TESTNAME'] == x_biomarker].groupby('PATNO')['TESTVALUE_NUMERIC'].mean().rename(x_biomarker)
                pivot_y = filtered_data[filtered_data['TESTNAME'] == y_biomarker].groupby('PATNO')['TESTVALUE_NUMERIC'].mean().rename(y_biomarker)
                corr_data = pd.concat([pivot_x, pivot_y], axis=1).dropna()
                
                if not corr_data.empty:
                    cohort_info = filtered_data[['PATNO', 'COHORT_SIMPLE']].drop_duplicates('PATNO').set_index('PATNO')
                    corr_data = corr_data.join(cohort_info)
                    fig = create_correlation_plot(corr_data, x_biomarker, y_biomarker)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Not enough data to plot correlation.")
                else:
                    st.warning("Not enough data to plot correlation.")

    with tab4:
        st.header("PD Proteomic Score (PD-ProS) Analysis")
        if 'PD_PROS' not in filtered_data.columns or filtered_data['PD_PROS'].isna().all():
            st.warning("PD-ProS score could not be calculated. Ensure the required proteins are in the dataset.")
        else:
            fig_pros_violin = px.violin(filtered_data.dropna(subset=['PD_PROS']), x='COHORT_SIMPLE', y='PD_PROS', color='COHORT_SIMPLE', box=True, title='Distribution of PD-ProS by Cohort')
            st.plotly_chart(fig_pros_violin, use_container_width=True)

    with tab5:
        st.header("Data Explorer")
        st.dataframe(filtered_data.head(1000))

# --- Main App ---
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Dashboard"])

    if page == "Home":
        show_home_page()
    elif page == "Dashboard":
        show_dashboard_page()

if __name__ == "__main__":
    main()
