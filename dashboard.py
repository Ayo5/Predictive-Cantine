import streamlit as st
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

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
st.markdown("<h1 class='main-header'>🍽️ Vision Food</h1>", unsafe_allow_html=True)


if "Repas semaine" not in st.session_state:
    with st.spinner('Calcul en cours...'):
        # Load and prepare dataset
        dataset = load_data()
        final_dataset = prepare_dataset(dataset, NUM_WEEKS)
        st.session_state["Repas semaine"] = final_dataset

# Date selection with calendar
# Charger le CSV pour obtenir les dates disponibles
csv_data = pd.read_csv(CSV_PREDICTIONS)
available_dates = pd.to_datetime(csv_data['Date']).sort_values().unique()

if len(available_dates) > 0:
    min_date = available_dates[0]
    max_date = available_dates[-1]
    default_date = min_date
else:
    # Fallback si aucune date n'est disponible
    today = datetime.now()
    min_date = today - timedelta(days=today.weekday())
    max_date = min_date + timedelta(days=NUM_WEEKS * 7)
    default_date = min_date

selected_date = st.date_input(
    "Sélectionnez une date pour voir le menu de la semaine correspondante",
    value=default_date,
    min_value=min_date,
    max_value=max_date
)

# Calculer le numéro de semaine à partir de la date sélectionnée
selected_date_dt = datetime.combine(selected_date, datetime.min.time())
days_diff = (selected_date_dt - datetime.combine(min_date, datetime.min.time())).days
current_week = days_diff // 7

# Afficher la semaine sélectionnée
week_start = selected_date - timedelta(days=selected_date.weekday())
week_end = week_start + timedelta(days=4)  # Vendredi
st.info(f"Prédictions pour la semaine du {week_start.strftime('%d/%m/%Y')} au {week_end.strftime('%d/%m/%Y')}")

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
display_menu_section(col1, current_week)
display_budget_section(col2, current_week)
display_waste_section(col3, current_week)