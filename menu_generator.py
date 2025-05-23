import re
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import numpy as np
from config import CSV_CO2_COUTS, DEFAULT_DELAY_MAIN_DISH, DEFAULT_DELAY_MENU

delay_main_dish = DEFAULT_DELAY_MAIN_DISH
delay_menu = DEFAULT_DELAY_MENU


def calcul_menus(sorted_results, num_weeks):
    """Calculate menus for all weeks"""
    menus = {}
    unique_dates = sorted(pd.to_datetime(sorted_results["Date"].unique()))

    for date in unique_dates:
        str_date = date.strftime("%d-%m-%Y")
        date_for_filter = date.strftime("%Y-%m-%d")
        date_data = (
            sorted_results[sorted_results["Date"] == date_for_filter]
            .iloc[:50, :]
            .to_dict("records")
        )

        for item in date_data:
            item["Date"] = date

        menus[str_date] = date_data

    return menus


def get_current_menu(week_number):
    """Get menu for the current week with price and CO2 calculations"""
    week_menus = []
    price = 0
    co2 = 0

    co2_couts = pd.read_csv(CSV_CO2_COUTS)
    co2_couts["Nom"] = co2_couts["Nom"].str.lower()
    co2_couts["Nom"] = co2_couts["Nom"].str.replace(r"(^\s+|\s+$)", "")  # Remove spaces
    co2_couts["Nom"] = co2_couts["Nom"].str.replace(r"s$", "")  # Remove plural

    menus = st.session_state["menus"]
    all_dates = sorted([datetime.strptime(date, "%d-%m-%Y") for date in menus.keys()])

    if len(all_dates) > 0:
        start_idx = week_number * 5
        if start_idx < len(all_dates):
            week_start = all_dates[start_idx]

            week_dates = []
            current_idx = start_idx
            while len(week_dates) < 5 and current_idx < len(all_dates):
                week_dates.append(all_dates[current_idx])
                current_idx += 1

            for current_date in week_dates:
                str_date = current_date.strftime("%d-%m-%Y")

                try:
                    if str_date in menus and len(menus[str_date]) > 0:
                        row = menus[str_date][0]
                        if str_date in st.session_state["skips"]:
                            skip_index = st.session_state["skips"][str_date]
                            if skip_index >= len(menus[str_date]):
                                skip_index = 0
                                st.session_state["skips"][str_date] = 0
                            row = menus[str_date][skip_index]

                        if dish_found(row, current_date, menus) or menu_found(
                            row, current_date, menus
                        ):
                            skip_index = st.session_state["skips"].get(str_date, 0) + 1
                            if skip_index >= len(menus[str_date]):
                                skip_index = 0
                            st.session_state["skips"][str_date] = skip_index
                            row = menus[str_date][skip_index]

                        week_menus.append(row)
                        price, co2 = calculate_menu_cost_and_co2(
                            row, co2_couts, price, co2
                        )
                    else:
                        row = create_default_menu_item(current_date)
                        week_menus.append(row)

                except Exception as e:
                    print(f"Error processing menu for {str_date}: {e}")
                    row = create_default_menu_item(current_date)
                    week_menus.append(row)
        else:
            for i in range(5):
                current_date = datetime.now() + timedelta(days=i)
                row = create_default_menu_item(current_date)
                week_menus.append(row)
    else:
        for i in range(5):
            current_date = datetime.now() + timedelta(days=i)
            row = create_default_menu_item(current_date)
            week_menus.append(row)

    return week_menus, price, co2


def dish_found(row, current_date, menus):
    """Check if dish has been served in the last delay_main_dish days"""
    found = False
    previous_dates = sorted(
        [
            datetime.strptime(x, "%d-%m-%Y")
            for x in menus.keys()
            if datetime.strptime(x, "%d-%m-%Y") < current_date
        ]
    )[-delay_main_dish:]

    previous_menus = [
        menus[d.strftime("%d-%m-%Y")][
            st.session_state["skips"].get(d.strftime("%d-%m-%Y"), 0)
        ]
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
    previous_dates = sorted(
        [
            datetime.strptime(x, "%d-%m-%Y")
            for x in menus.keys()
            if datetime.strptime(x, "%d-%m-%Y") < current_date
        ]
    )[-delay_menu:]

    previous_menus = [
        menus[d.strftime("%d-%m-%Y")][
            st.session_state["skips"].get(d.strftime("%d-%m-%Y"), 0)
        ]
        for d in previous_dates
    ]

    for prev_menu in previous_menus:
        if (
            str(row["Entrée"]).lower() in str(prev_menu["Entrée"]).lower()
            and str(row["Plat"]).lower() in str(prev_menu["Plat"]).lower()
            and str(row["Dessert"]).lower() in str(prev_menu["Dessert"]).lower()
        ):
            found = True
            break
    return found


def calculate_menu_cost_and_co2(row, co2_couts, price, co2):
    """Calculate cost and CO2 for a menu"""
    for dish in ["Entrée", "Plat", "Légumes", "Dessert", "Laitage"]:
        if pd.isna(row[dish]):
            continue

        composants = [
            re.sub(r"(^\s+|\s+$)", "", re.sub(r"\s$", "", x.lower()))
            for x in str(row[dish]).split()
        ]

        for comp in composants:
            for _, food_item in co2_couts.iterrows():
                try:
                    if comp in food_item["Nom"] or food_item["Nom"] in comp:
                        price += float(food_item["Prix"]) * 0.1
                        co2 += float(food_item["CO2"]) * 0.1
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
        "Taux participation": 0.8,
        "Taux gaspillage": 0.3,
        "Code_entrée": "",
        "Code_plat": "",
        "Code_légumes": "",
        "Code_dessert": "",
        "Code_laitage": "",
        "Taux gaspillage prédit": 0.0,
        "Taux participation prédit": 0.0,
    }
