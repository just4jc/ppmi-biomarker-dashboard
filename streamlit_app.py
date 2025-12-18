import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import PPMIDataLoader
import numpy as np
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="PPMI Biomarker Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Authentication ---
# Credentials are sourced from Streamlit Secrets if available, with env vars as fallback.
# Define in Streamlit Cloud → App → Settings → Secrets:
#   app_user: your_username
#   app_password: your_password
DEFAULT_USERNAME = st.secrets.get("app_user", os.getenv("APP_USER", "admin"))
DEFAULT_PASSWORD = st.secrets.get("app_password", os.getenv("APP_PASSWORD", "ppmi2025"))

def check_password():
    """Returns `True` if the user has entered the correct password."""
    # IMPORTANT: This is not secure for production!
    # For production, use Streamlit Secrets Management
    if (st.session_state.get("username") == DEFAULT_USERNAME and 
        st.session_state.get("password") == DEFAULT_PASSWORD):
        st.session_state["authenticated"] = True
    else:
        st.session_state["authenticated"] = False
        if "password" in st.session_state and st.session_state["password"]:
            st.error("😕 User not known or password incorrect")

def login_form():
    """Displays the login form."""
    st.title("🧠 PPMI Biomarker Dashboard Login")
    st.markdown("Please log in to access the dashboard.")
    
    with st.form("login"):
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.form_submit_button("Log in", on_click=check_password)

    # Only display default hint when not using Secrets or env overrides
    if ("app_user" not in st.secrets and "app_password" not in st.secrets
        and os.getenv("APP_USER") is None and os.getenv("APP_PASSWORD") is None):
        st.info("💡 Default credentials: Username: `admin` / Password: `ppmi2025`")

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
                   box=True, points=False, # Show box plot inside violin
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
    # Early return if variables are the same to prevent duplicate column error
    if x_var == y_var:
        return None
    
    if x_var not in data.columns or y_var not in data.columns: 
        return None
    
    plot_data = data.dropna(subset=[x_var, y_var])
    if plot_data.empty: 
        return None
    
    # Additional safety check for duplicate column names
    if data.columns.duplicated().any():
        print(f"Warning: DataFrame has duplicate columns: {data.columns.tolist()}")
        return None
    
    return px.scatter(plot_data, x=x_var, y=y_var, color='COHORT_SIMPLE', trendline='ols',
                      title=f'Correlation between {x_var} and {y_var}',
                      labels={x_var: x_var, y_var: y_var})

# --- UI Sections ---
def show_home_page():
    st.title("🧠 Welcome to the PPMI Biomarker Dashboard!")
    
    st.markdown("""
    This interactive dashboard provides a comprehensive platform for exploring the **Parkinson's Progression Markers Initiative (PPMI)** dataset. 
    It is designed to help researchers, clinicians, and data scientists visualize and analyze the complex relationships between 
    biomarkers, clinical assessments, and patient demographics in Parkinson's disease.
    """)
    
    st.markdown("---")
    
    st.header("📊 Dashboard Features")
    st.markdown("""
    Select the **Dashboard** from the sidebar to begin exploring the data. You will find several tabs, each offering a unique analytical perspective:
    """)
    
    # Create expandable sections for each tab
    with st.expander("🔍 **Biomarker Distribution** - Compare diagnostic groups"):
        st.markdown("""
        **Purpose**: Compare biomarker levels across different diagnostic groups (Parkinson's Disease, Healthy Controls, etc.).
        
        **What you can do**:
        - Select any biomarker from the dropdown menu
        - View box plots showing the distribution of biomarker levels by cohort
        - Identify potential diagnostic differences between groups
        - Apply global filters to focus on specific age ranges or genetic risk groups
        
        **Key biomarkers available**: CSF Alpha-synuclein, Amyloid Beta (ABeta 1-42), phosphorylated Tau (pTau), total Tau (tTau), and more.
        """)
    
    with st.expander("📈 **Longitudinal Analysis** - Track changes over time"):
        st.markdown("""
        **Purpose**: Track how biomarkers change over time for individuals or cohorts (longitudinal donor analysis).
        
        **What you can do**:
        - Select a biomarker to analyze its temporal trends
        - View scatter plots with trend lines showing biomarker changes with age
        - Compare trajectories between different diagnostic groups
        - Identify potential biomarkers that show disease progression patterns
        
        **Insights**: This analysis helps identify biomarkers that may be useful for tracking disease progression over time.
        """)
    
    with st.expander("🔗 **Correlation Analysis** - Explore biomarker relationships"):
        st.markdown("""
        **Purpose**: Explore relationships between different biomarkers or between biomarkers and clinical scores.
        
        **What you can do**:
        - Select two different biomarkers for X and Y axes
        - View scatter plots with correlation trend lines
        - Examine how biomarkers relate to each other across different cohorts
        - Identify potential biomarker networks or pathways
        
        **Note**: Choose different biomarkers for meaningful correlation analysis. The dashboard will warn you if you select the same biomarker for both axes.
        """)
    
    with st.expander("🧬 **PD Proteomic Score (PD-ProS)** - Disease progression tracker"):
        st.markdown("""
        **Purpose**: Investigate the PD Proteomic Score, a promising 14-protein panel for tracking disease progression.
        
        **What you can do**:
        - View the distribution of PD-ProS scores across different cohorts
        - Compare how this composite score differs between Parkinson's patients and healthy controls
        - Understand how multiple biomarkers can be combined into a single prognostic score
        
        **Scientific Background**: The PD-ProS score combines 14 specific proteins into a single metric that may be more powerful than individual biomarkers for tracking disease progression.
        """)
    
    with st.expander("📋 **Data Explorer** - Raw data access"):
        st.markdown("""
        **Purpose**: View and explore the raw data table with applied filters.
        
        **What you can do**:
        - Browse the underlying dataset (first 1000 rows)
        - See all available columns and data points
        - Understand the data structure and patient demographics
        - Verify specific data points or explore data quality
        
        **Tip**: Use the global filters in the sidebar to narrow down the data before exploring.
        """)
    
    st.markdown("---")
    
    st.header("🧭 Global Filters")
    st.markdown("""
    The sidebar contains **Global Filters** that apply to all tabs:
    
    - **Filter by Cohort**: Select specific diagnostic groups (PD, Healthy Controls, etc.)
    - **Filter by Age**: Narrow analysis to specific age ranges
    - **Filter by Genetic Risk**: Focus on patients with specific genetic risk profiles
    
    These filters help you focus your analysis on specific patient populations of interest.
    """)
    
    st.markdown("---")
    
    st.header("📚 About the PPMI Data")
    st.markdown("""
    The **Parkinson's Progression Markers Initiative (PPMI)** is a landmark longitudinal study designed to identify biomarkers 
    of Parkinson's disease progression. This dataset represents a curated subset of the PPMI database, containing:
    
    - **Biomarker measurements**: CSF proteins, blood-based markers
    - **Clinical assessments**: UPDRS scores, cognitive evaluations  
    - **Patient demographics**: Age, sex, genetic information
    - **Longitudinal data**: Multiple visits per patient over time
    
    The goal is to identify reliable biomarkers that can track disease progression, predict outcomes, and potentially serve as endpoints for clinical trials.
    """)
    
    st.markdown("---")
    
    st.info("💡 **Getting Started**: Click on 'Dashboard' in the sidebar to begin your analysis!")
    

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
        
        if len(key_biomarkers) < 2:
            st.warning("At least 2 biomarkers are required for correlation analysis.")
            st.info("Please ensure the dataset contains multiple biomarkers.")
        else:
            col1, col2 = st.columns(2)
            # Ensure different defaults, but handle edge cases
            default_y_index = 1 if len(key_biomarkers) > 1 else 0
            x_biomarker = col1.selectbox("X-axis Biomarker", key_biomarkers, index=0)
            y_biomarker = col2.selectbox("Y-axis Biomarker", key_biomarkers, index=default_y_index)
            
            if x_biomarker and y_biomarker:
                if x_biomarker == y_biomarker:
                    st.warning("Please select different biomarkers for the X and Y axes.")
                    st.info("💡 **Tip**: Choose different biomarkers to explore correlations between different measurements.")
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
    # Check authentication first
    if not st.session_state.get("authenticated", False):
        login_form()
        return
    
    # Add logout button in sidebar
    if st.sidebar.button("🚪 Logout"):
        st.session_state["authenticated"] = False
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Dashboard"])

    if page == "Home":
        show_home_page()
    elif page == "Dashboard":
        show_dashboard_page()

if __name__ == "__main__":
    main()
