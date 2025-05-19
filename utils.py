import streamlit as st
import warnings
import datarobot as dr
from config import ENDPOINT, API_TOKEN

warnings.filterwarnings("ignore", category=DeprecationWarning)


def setup_page_style():
    """Setup page configuration and CSS styling"""
    st.set_page_config(layout="wide", page_title="Vision Food", page_icon="🍽️")

    with open("styles/main.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    try:
        dr.Client(endpoint=ENDPOINT, token=API_TOKEN)
    except Exception as e:
        st.error(f"Error initializing DataRobot client: {e}")
