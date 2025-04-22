import streamlit as st
import pandas as pd
import numpy as np
from config import WEEKDAYS, CSV_CO2_COUTS
from menu_generator import get_current_menu

def display_budget_section(col, current_week):
    """Display the budget section"""
    week_menus, prix_semaine, _ = get_current_menu(current_week)
    participations = [row["Taux de participation"] * 100 for row in week_menus]
    
    col.markdown("<h2 class='section-header'>Budget</h2>", unsafe_allow_html=True)
    
    cols2_2 = col.columns(2)
    num_students = cols2_2[0].number_input("Nombre d'élèves inscrits à la cantine :", min_value=0, max_value=5000, value=150)
    show_percent = cols2_2[1].checkbox("Afficher en pourcentages", value=False)
    
    col.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    if prix_semaine <= 0:
        try:
            co2_couts = pd.read_csv(CSV_CO2_COUTS)
            co2_couts["Nom"] = co2_couts["Nom"].str.lower().str.strip()
            
            prix_semaine = 0
            for menu in week_menus:
                prix_jour = 0
                for item_type in ["Entrée", "Plat", "Légumes", "Laitage", "Dessert"]:
                    if item_type in menu and pd.notna(menu[item_type]):
                        item_name = str(menu[item_type]).lower().strip()
                        matches = co2_couts[co2_couts["Nom"].str.contains(item_name, case=False, na=False)]
                        if not matches.empty:
                            prix_str = matches.iloc[0]["Prix Unitaire Kg"]
                            if isinstance(prix_str, str):
                                prix_str = prix_str.replace("€", "").strip()
                            prix_item = float(prix_str) * 0.1  
                            prix_jour += prix_item
                        else:
                            prix_jour += 0.5
                            print(f"Prix non trouvé pour {item_name}")
                prix_semaine += prix_jour
            
            if prix_semaine <= 0:
                prix_semaine = 3.5 * 5  
        except Exception as e:
            print(f"Erreur lors du calcul du prix: {e}")
            prix_semaine = 3.5 * 5  
    
    cols2_1_metrics = col.columns(3)
    cout_semaine = prix_semaine * num_students
    cout_standard = 4.5 * 5 * num_students  
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
    
    col.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
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