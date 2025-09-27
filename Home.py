import streamlit as st

st.set_page_config(
    page_title="PPMI Biomarker Dashboard - Home",
    page_icon="🏠",
    layout="wide",
)

st.title("Welcome to the PPMI Biomarker Dashboard!")
st.sidebar.success("Select a page above.")

st.markdown(
    """
    This interactive dashboard provides a comprehensive platform for exploring the Parkinson's Progression Markers Initiative (PPMI) dataset. It is designed to help researchers, clinicians, and data scientists visualize and analyze the complex relationships between biomarkers, clinical assessments, and patient demographics in Parkinson's disease.

    ### How to Use This Dashboard
    Use the sidebar to navigate to the **Dashboard** page. There, you will find several tabs, each offering a unique perspective on the data:

    - **Longitudinal Biomarker Trends**: Track the levels of specific biomarkers over time for different patient cohorts. This is crucial for understanding disease progression.
    - **Correlation Analysis**: Explore the relationships between different biomarkers and clinical scores. This can help identify potential surrogate markers.
    - **Patient Cohort Explorer**: Filter and examine the data for specific patient groups based on demographics, genetic risk factors, and clinical status.
    - **PD-ProS Analysis**: Investigate the PD Proteomic Score (PD-ProS), a 14-protein panel that shows promise in tracking Parkinson's disease progression.

    ### About the Data
    The data used in this dashboard is a curated subset of the PPMI database, a landmark observational study that has collected a vast repository of data from thousands of participants. The goal of PPMI is to identify biomarkers of Parkinson's disease progression to accelerate the development of new treatments.

    **We hope this tool facilitates new discoveries and a deeper understanding of Parkinson's disease.**
    """
)
