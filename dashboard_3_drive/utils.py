import streamlit as st
import warnings
import datarobot as dr
from config import ENDPOINT, API_TOKEN

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def setup_page_style():
    """Setup page configuration and CSS styling"""
    # Set page configuration
    st.set_page_config(
        layout="wide", 
        page_title="Predictive Cantine",
        page_icon="🍽️"
    )
    
    # Add custom CSS
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E88E5;
            text-align: center;
            margin-bottom: 1rem;
        }
        .section-header {
            color: #0D47A1;
            font-size: 1.5rem;
            padding-top: 1rem;
        }
        .menu-day {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
        }
        .menu-item {
            margin-bottom: 5px;
        }
        .bio-tag {
            color: green;
            font-weight: bold;
        }
        .divider {
            margin-top: 10px;
            margin-bottom: 10px;
            border-bottom: 1px solid #e0e0e0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize DataRobot client
    try:
        dr.Client(endpoint=ENDPOINT, token=API_TOKEN)
    except Exception as e:
        st.error(f"Error initializing DataRobot client: {e}")