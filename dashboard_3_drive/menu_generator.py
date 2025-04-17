import re
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import numpy as np
from config import WEEKDAYS, DEFAULT_DELAY_MAIN_DISH, DEFAULT_DELAY_MENU

# Global variables
delay_main_dish = DEFAULT_DELAY_MAIN_DISH
delay_menu = DEFAULT_DELAY_MENU

def calcul_menus(sorted_results, num_weeks):
    """Calculate menus for all weeks"""
    menus = {}
    for week in range(num_weeks):
        for i in range(5):
            delta_i = i + week * 5
            current_date = datetime(2023, 1, 2) + timedelta(days=delta_i + (2 * np.floor(delta_i / 5)))
            str_date = current_date.strftime("%d-%m-%Y")
            menus[str_date] = sorted_results[sorted_results["Date"] == current_date].iloc[:50, :].to_dict("records")
    return menus

def get_current_menu(week_number):
    """Get menu for the current week with price and CO2 calculations"""
    week_menus = []
    price = 0  # Total cost for one child
    co2 = 0    # Carbon footprint
    
    # Load CO2 and cost data
    co2_couts = pd.read_csv("data/co2_couts.csv")
    co2_couts["Nom"] = co2_couts["Nom"].str.lower()
    co2_couts["Nom"] = co2_couts["Nom"].str.replace(r"(^\s+|\s+$)", "")  # Remove spaces
    co2_couts["Nom"] = co2_couts["Nom"].str.replace(r"s$", "")  # Remove plural
    
    menus = st.session_state["menus"]
    
    for i in range(5):
        i_week = i + week_number * 5
        current_date = datetime(2023, 1, 2) + timedelta(days=i_week + (2 * np.floor(i_week / 5)))
        str_date = current_date.strftime("%d-%m-%Y")
        
        try:
            row = menus[str_date][0]
            if str_date in st.session_state["skips"]:
                row = menus[str_date][st.session_state["skips"][str_date]]
            
            # Check if dish has been served recently
            if dish_found(row, current_date, menus) or menu_found(row, current_date, menus):
                st.session_state["skips"][str_date] = st.session_state["skips"].get(str_date, 0) + 1
                row = menus[str_date][st.session_state["skips"][str_date]]
            
            week_menus.append(row)
            
            # Calculate menu cost and CO2
            price, co2 = calculate_menu_cost_and_co2(row, co2_couts, price, co2)
            
        except Exception as e:
            st.warning(f"Error processing menu for {str_date}: {e}")
            # Create default menu item
            row = create_default_menu_item(current_date)
            week_menus.append(row)
    
    return week_menus, price, co2

def dish_found(row, current_date, menus):
    """Check if dish has been served in the last delay_main_dish days"""
    found = False
    previous_dates = sorted([
        datetime.strptime(x, "%d-%m-%Y")
        for x in menus.keys()
        if datetime.strptime(x, "%d-%m-%Y") < current_date
    ])[-delay_main_dish:]
    
    previous_menus = [
        menus[d.strftime("%d-%m-%Y")][st.session_state["skips"].get(d.strftime("%d-%m-%Y"), 0)] 
        for d in previous_dates
    ]
    
    for prev_menu in previous_menus:
        if str(row["Plat"]).lower() in str(prev_menu["Plat"]).lower():
            found = True
            break
    return found

def menu_found(row, current_date, menus):
    """Check if entire menu has been served in the last delay_menu days"""
    found = False
    previous_dates = sorted([
        datetime.strptime(x, "%d-%m-%Y")
        for x in menus.keys()
        if datetime.strptime(x, "%d-%m-%Y") < current_date
    ])[-delay_menu:]
    
    previous_menus = [
        menus[d.strftime("%d-%m-%Y")][st.session_state["skips"].get(d.strftime("%d-%m-%Y"), 0)] 
        for d in previous_dates
    ]
    
    for prev_menu in previous_menus:
        if (str(row["Entrée"]).lower() in str(prev_menu["Entrée"]).lower() and
            str(row["Plat"]).lower() in str(prev_menu["Plat"]).lower() and
            str(row["Dessert"]).lower() in str(prev_menu["Dessert"]).lower()):
            found = True
            break
    return found

def calculate_menu_cost_and_co2(row, co2_couts, price, co2):
    """Calculate cost and CO2 for a menu"""
    for dish in ["Entrée", "Plat", "Légumes", "Dessert", "Laitage"]:
        if pd.isna(row[dish]):
            continue
        
        composants = [re.sub(r"(^\s+|\s+$)", "", re.sub(r"\s$", "", x.lower())) 
                      for x in str(row[dish]).split()]
        
        for comp in composants:
            for _, food_item in co2_couts.iterrows():
                try:
                    if comp in food_item["Nom"] or food_item["Nom"] in comp:
                        price += float(food_item["Prix"]) * 0.1  # 100g = 0.1kg
                        co2 += float(food_item["CO2"]) * 0.1  # 100g = 0.1kg
                        break
                except (KeyError, ValueError, TypeError):
                    continue
    
    return price, co2

def create_default_menu_item(current_date):
    """Create a default menu item"""
    return {
        "Date": current_date,
        "Entrée": "Menu par défaut",
        "Plat": "Plat par défaut",
        "Légumes": "Légumes par défaut",
        "Dessert": "Dessert par défaut",
        "Laitage": "Laitage par défaut",
        "Taux de participation": 0.8,
        "Taux de gaspillage": 0.2,
        "Taux gaspillage": 0.3,
        "Code_entrée": "",
        "Code_plat": "",
        "Code_légumes": "",
        "Code_dessert": "",
        "Code_laitage": ""
    }