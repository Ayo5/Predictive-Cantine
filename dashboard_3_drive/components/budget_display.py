import streamlit as st
import pandas as pd
import numpy as np
from config import WEEKDAYS
from menu_generator import get_current_menu

def display_budget_section(col, current_week):
    """Display the budget section"""
    # Get data
    week_menus, prix_semaine, _ = get_current_menu(current_week)
    participations = [row["Taux de participation"] * 100 for row in week_menus]
    
    # Budget section
    col.markdown("<h2 class='section-header'>Budget</h2>", unsafe_allow_html=True)
    
    # Settings
    cols2_2 = col.columns(2)
    num_students = cols2_2[0].number_input("Nombre d'élèves inscrits à la cantine :", min_value=0, max_value=5000, value=150)
    show_percent = cols2_2[1].checkbox("Afficher en pourcentages", value=False)
    
    # Add some space
    col.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    # Budget metrics
    cols2_1_metrics = col.columns(3)
    cout_semaine = prix_semaine * num_students
    cout_standard = 4.5 * 5 * num_students  # 4.5€ par repas standard, 5 jours
    economies = cout_standard - cout_semaine if cout_standard > cout_semaine else 0
    
    cols2_1_metrics[0].metric(
        "Coût par enfant",
        f"{prix_semaine:.2f}€",
        f"{(prix_semaine/5):.2f}€/jour"
    )
    cols2_1_metrics[1].metric(
        "Coût total semaine",
        f"{cout_semaine:.2f}€",
        f"{num_students} enfants"
    )
    cols2_1_metrics[2].metric(
        "Économies réalisées",
        f"{economies:.2f}€",
        f"{(economies/cout_standard*100):.1f}%" if cout_standard > 0 else "0%",
        delta_color="normal" if economies > 0 else "off"
    )
    
    # Add some space
    col.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    # Participation chart
    col.markdown("<h2 class='section-header'>Affluence</h2>", unsafe_allow_html=True)
    
    chart_data = pd.DataFrame(
        np.array([[round(x * 10) / 10 if show_percent else round(x / 100 * num_students)] for x in participations]),
        index=[f"{i+1} - {w}" for i, w in enumerate(WEEKDAYS)],
        columns=["Taux de participation" if show_percent else "Nombre de participants"]
    )
    
    col.bar_chart(
        data=chart_data,
        y="Taux de participation" if show_percent else "Nombre de participants",
        use_container_width=True
    )