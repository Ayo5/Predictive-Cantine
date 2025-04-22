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

st.markdown("<h1 class='main-header'>🍽️ Vision Food</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Workspace", "Dashboard", "Importer CSV"])

with tab1:
    st.markdown("""
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
    
    #### Pour commencer :
    
    1. Allez dans l'onglet **Importer CSV**
    2. Téléchargez votre fichier de menus
    3. Consultez les analyses dans l'onglet **Dashboard**
    """)
    
    st.image("./images/dashboard.png", 
             caption="Aperçu du tableau de bord Vision Food")

with tab2:
    data_file_exists = os.path.isfile(CSV_PREDICTIONS)
    
    if not data_file_exists and "Repas semaine" not in st.session_state:
        st.info("Bienvenue sur Vision Food! Pour commencer, veuillez importer un fichier CSV dans l'onglet 'Importer CSV'.")
        
        st.markdown("""
        ### Comment utiliser cette application:
        
        1. Allez dans l'onglet **Importer CSV**
        2. Téléchargez votre fichier de données au format CSV
        3. Le système générera des prédictions sur le taux de gaspillage et de participation
        4. Revenez sur cet onglet pour visualiser les menus optimisés
        
        ### Format requis du fichier CSV:
        
        Votre fichier doit contenir les colonnes suivantes:
        - **Date**: au format YYYY-MM-DD
        - **Entrée**: le nom de l'entrée
        - **Plat**: le plat principal
        - **Légumes**: l'accompagnement
        - **Dessert**: le dessert
        - **Laitage**: le produit laitier
        """)
        
        # Logo 
        # st.image("https://via.placeholder.com/800x400?text=Vision+Food+Dashboard", 
                #  caption="Aperçu du tableau de bord après importation des données")
    else:
        if "Repas semaine" not in st.session_state:
            with st.spinner('Calcul en cours...'):
                dataset = load_data()
                final_dataset = prepare_dataset(dataset, 16)
                st.session_state["Repas semaine"] = final_dataset

        if "Repas semaine" in st.session_state:
            try:
                csv_data = pd.read_csv(CSV_PREDICTIONS)
                available_dates = pd.to_datetime(csv_data['Date']).sort_values().unique()

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
                    "Sélectionnez une date pour voir le menu de la semaine correspondante",
                    value=default_date,
                    min_value=min_date,
                    max_value=max_date
                )

                selected_date_dt = datetime.combine(selected_date, datetime.min.time())
                days_diff = (selected_date_dt - datetime.combine(min_date, datetime.min.time())).days
                current_week = days_diff // 7

                week_start = selected_date - timedelta(days=selected_date.weekday())
                week_end = week_start + timedelta(days=4)
                st.info(f"Prédictions pour la semaine du {week_start.strftime('%d/%m/%Y')} au {week_end.strftime('%d/%m/%Y')}")

                sorted_results = st.session_state["Repas semaine"].sort_values("Taux de gaspillage", ascending=True)

                if "menus" not in st.session_state:
                    st.session_state["menus"] = calcul_menus(sorted_results, NUM_WEEKS)
                    
                if "skips" not in st.session_state:
                    st.session_state["skips"] = {}

                col1, col2, col3 = st.columns(3)

                display_menu_section(col1, current_week)
                display_budget_section(col2, current_week)
                display_waste_section(col3, current_week)
            except Exception as e:
                st.error(f"Erreur lors du chargement des données: {str(e)}")
                st.info("Veuillez vérifier votre fichier CSV ou en importer un nouveau dans l'onglet 'Importer CSV'.")

with tab3:
    uploaded_data = upload_csv_section()
    
    if uploaded_data is not None and not uploaded_data.empty:
        st.session_state["Repas semaine"] = uploaded_data

        if "menus" in st.session_state:
            del st.session_state["menus"]
        
        st.subheader("Analyse des prédictions")
        
        avg_waste = uploaded_data['Taux de gaspillage'].mean() * 100
        st.metric("Taux de gaspillage moyen", f"{avg_waste:.2f}%")
        
        avg_participation = uploaded_data['Taux de participation'].mean() * 100
        st.metric("Taux de participation moyen", f"{avg_participation:.2f}%")
        
        st.subheader("Distribution des taux de gaspillage")
        st.bar_chart(uploaded_data['Taux de gaspillage'] * 100)
        
        if st.button("Voir les menus optimisés"):
            st.set_query_params(tab="dashboard")
            st.experimental_rerun()