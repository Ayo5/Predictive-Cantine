import streamlit as st
from datetime import datetime
import numpy as np

# Import modules
from config import *
from utils import setup_page_style
from data_loader import load_data, prepare_dataset
from menu_generator import calcul_menus, get_current_menu
from components.menu_display import display_menu_section
from components.budget_display import display_budget_section
from components.waste_display import display_waste_section

# Setup page
setup_page_style()

# Main dashboard
st.markdown("<h1 class='main-header'>🍽️ Predictive Cantine</h1>", unsafe_allow_html=True)

# Load data if not already in session state
if "Repas semaine" not in st.session_state:
    with st.spinner('Calcul en cours...'):
        # Load and prepare dataset
        dataset = load_data()
        final_dataset = prepare_dataset(dataset, NUM_WEEKS)
        st.session_state["Repas semaine"] = final_dataset

# Week selection
current_week = int(st.selectbox(
    "Choix de la semaine",
    [f"Semaine {i+1}" for i in range(NUM_WEEKS)],
    index=0
).split(" ")[-1]) - 1

# Sort results by waste rate
sorted_results = st.session_state["Repas semaine"].sort_values("Taux de gaspillage", ascending=True)

# Initialize menus and skips
if "menus" not in st.session_state:
    st.session_state["menus"] = calcul_menus(sorted_results, NUM_WEEKS)
    
if "skips" not in st.session_state:
    st.session_state["skips"] = {}

# Create layout
col1, col2, col3 = st.columns(3)

# Display sections
with col1:
    display_menu_section(col1, current_week)

with col2:
    display_budget_section(col2, current_week)

with col3:
    display_waste_section(col3, current_week)