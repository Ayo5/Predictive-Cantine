import streamlit as st
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import os.path

from config import *
from utils import setup_page_style
from data_loader import load_data, prepare_dataset
from menu_generator import calcul_menus, get_current_menu
from components.menu_display import display_menu_section
from components.budget_display import display_budget_section
from components.waste_display import display_waste_section
from components.upload_csv import upload_csv_section

setup_page_style()
st.image("./images/logo.png", width=100)
st.markdown("<h1 class='main-header'>Vision Food</h1>", unsafe_allow_html=True)


st.sidebar.markdown("<h2 class='sidebar-title'>Navigation</h2>", unsafe_allow_html=True)

pages = ["Home", "Menu semaine", "Gaspillage", "Affluence", "Importation", "Contact"]

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

for p in pages:
    if st.sidebar.button(p, key=f"nav_{p}"):
        st.session_state.current_page = p

page = st.session_state.current_page


def select_date_and_week():
    try:
        csv_data = pd.read_csv(CSV_PREDICTIONS)
        available_dates = pd.to_datetime(csv_data["Date"]).sort_values().unique()

        if len(available_dates) > 0:
            min_date = available_dates[0]
            max_date = available_dates[-1]
            default_date = min_date
        else:
            today = datetime.now()
            min_date = today - timedelta(days=today.weekday())
            max_date = min_date + timedelta(days=NUM_WEEKS * 7)
            default_date = min_date

        selected_date = st.date_input(
            "Sélectionnez une date",
            value=default_date,
            min_value=min_date,
            max_value=max_date,
        )

        selected_date_dt = datetime.combine(selected_date, datetime.min.time())
        days_diff = (
            selected_date_dt - datetime.combine(min_date, datetime.min.time())
        ).days
        current_week = days_diff // 7

        week_start = selected_date - timedelta(days=selected_date.weekday())
        week_end = week_start + timedelta(days=4)
        st.info(
            f"Semaine du {week_start.strftime('%d/%m/%Y')} au {week_end.strftime('%d/%m/%Y')}"
        )

        return current_week
    except Exception as e:
        st.error(f"Erreur lors de la sélection de date: {str(e)}")
        return 0


if page == "Home":
    st.markdown(
        """
    ### Bienvenue sur Vision Food! 🎉
    
    Vision Food est votre assistant intelligent pour la gestion des menus de restauration collective.
    
    #### Fonctionnalités principales :
    
    1. 📊 **Analyse prédictive**
       - Prévision des taux de participation
       - Estimation du gaspillage alimentaire
    
    2. 🍽️ **Optimisation des menus**
       - Suggestions de menus équilibrés
       - Rotation optimale des plats
    
    3. 💰 **Gestion budgétaire**
       - Suivi des coûts
       - Optimisation des dépenses
    """
    )

    st.image(
        "./images/dashboard.png", caption="Aperçu du tableau de bord Vision Food (Beta)"
    )

elif page == "Menu semaine":
    data_file_exists = os.path.isfile(CSV_PREDICTIONS)

    if not data_file_exists and "Repas semaine" not in st.session_state:
        st.info(
            "Pour visualiser les menus, veuillez d'abord importer un fichier CSV dans la section 'Importation'."
        )
    else:
        if "Repas semaine" not in st.session_state:
            with st.spinner("Calcul en cours..."):
                dataset = load_data()
                final_dataset = prepare_dataset(dataset, 16)
                st.session_state["Repas semaine"] = final_dataset

        try:
            current_week = select_date_and_week()

            if "menus" not in st.session_state:
                sorted_results = st.session_state["Repas semaine"].sort_values(
                    "Taux gaspillage", ascending=True
                )
                st.session_state["menus"] = calcul_menus(sorted_results, NUM_WEEKS)

            if "skips" not in st.session_state:
                st.session_state["skips"] = {}
            display_menu_section(st, current_week)

        except Exception as e:
            st.error(f"Erreur lors du chargement des données: {str(e)}")
            st.info(
                "Veuillez vérifier votre fichier CSV ou en importer un nouveau dans la section 'Importation'."
            )

elif page == "Gaspillage":
    if "Repas semaine" not in st.session_state:
        st.info(
            "Pour visualiser les statistiques de gaspillage, veuillez d'abord importer un fichier CSV dans la section 'Importation'."
        )
    else:
        st.markdown(
            "<h2 class='section-header'>Sélection de la période</h2>",
            unsafe_allow_html=True,
        )
        current_week = select_date_and_week()
        display_waste_section(st, current_week)

elif page == "Affluence":
    if "Repas semaine" not in st.session_state:
        st.info(
            "Pour visualiser les statistiques d'affluence, veuillez d'abord importer un fichier CSV dans la section 'Importation'."
        )
    else:
        st.markdown(
            "<h2 class='section-header'>Sélection de la période</h2>",
            unsafe_allow_html=True,
        )
        current_week = select_date_and_week()
        display_budget_section(st, current_week)

elif page == "Importation":
    uploaded_data = upload_csv_section()

    if uploaded_data is not None and not uploaded_data.empty:
        st.session_state["Repas semaine"] = uploaded_data
        if "menus" in st.session_state:
            del st.session_state["menus"]

        st.subheader("Analyse des prédictions")

        avg_waste = uploaded_data["Taux gaspillage"].mean() * 100
        st.metric("Taux de gaspillage moyen", f"{avg_waste:.2f}%")

        avg_participation = uploaded_data["Taux participation"].mean() * 100
        st.metric("Taux de participation moyen", f"{avg_participation:.2f}%")

        st.subheader("Distribution des taux de gaspillage")
        st.bar_chart(uploaded_data["Taux gaspillage"] * 100)

        if st.button("Voir les menus optimisés"):
            st.set_query_params(tab="dashboard")
            st.rerun()
