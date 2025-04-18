import streamlit as st
import pandas as pd
from config import CSV_PREDICTIONS, WEEKDAYS
from menu_generator import get_current_menu

def display_menu_section(col, current_week):
    """Display the menu section"""
    col.markdown("<h2 class='section-header'>Menu de la semaine</h2>", unsafe_allow_html=True)
    week_menus, prix_semaine, _ = get_current_menu(current_week)
    
    # Charger les données du CSV pour avoir des options de menu alternatives
    csv_data = pd.read_csv(CSV_PREDICTIONS)
    
    for i, row in enumerate(week_menus):
        # Create a container for each day's menu
        with col.container():
            st.markdown(f"<div class='menu-day'>", unsafe_allow_html=True)
            
            # Day header with date
            st.markdown(f"<h3>{WEEKDAYS[row['Date'].weekday()]} ({row['Date'].strftime('%d-%m-%Y')})</h3>", unsafe_allow_html=True)
            
            # Get menu options from CSV
            # Filtrer pour obtenir des menus différents (en utilisant différentes combinaisons plat/légumes)
            unique_menus = csv_data.drop_duplicates(subset=['Plat', 'Légumes']).head(10)
            
            # Créer les options de menu
            menu_options = []
            for j, menu_option in enumerate(unique_menus.iterrows()):
                _, menu_data = menu_option
                plat_desc = f"{menu_data['Plat']}"
                if not pd.isna(menu_data.get('Légumes', '')):
                    plat_desc += f" + {menu_data['Légumes']}"
                menu_options.append(f"Option {j+1}: {plat_desc}")
            
            # Current selection
            str_date = row["Date"].strftime("%d-%m-%Y")
            current_index = st.session_state["skips"].get(str_date, 0)
            if current_index >= len(menu_options):
                current_index = 0
                st.session_state["skips"][str_date] = 0
            
            # Create the selector
            selected_option = st.selectbox(
                "Choisir un menu alternatif:",
                menu_options,
                index=current_index,
                key=f"menu_select_{str_date}"
            )
            
            # Update the selection if changed
            new_index = menu_options.index(selected_option)
            if new_index != current_index:
                st.session_state["skips"][str_date] = new_index
                # Try a refresh
                #st.experimental_rerun()
            
            # Menu items in columns
            day_cols = st.columns(3)
            
            # Entrée
            with day_cols[0]:
                st.markdown("<b>Entrée</b>", unsafe_allow_html=True)
                st.markdown(f"<div class='menu-item'>{row['Entrée']}</div>", unsafe_allow_html=True)
                # Check if the column exists before trying to access it
                if "Code_entrée" in row and "AB" in str(row["Code_entrée"]):
                    st.success("Bio")
            
            # Plat
            with day_cols[1]:
                st.markdown("<b>Plat</b>", unsafe_allow_html=True)
                plat_text = " + ".join([x for x in [row["Plat"], row["Légumes"]] if str(x) != "nan"])
                st.markdown(f"<div class='menu-item'>{plat_text}</div>", unsafe_allow_html=True)
                # Check if columns exist before trying to access them
                is_bio = False
                if "Code_plat" in row and "AB" in str(row["Code_plat"]):
                    is_bio = True
                if "Code_légumes" in row and "AB" in str(row["Code_légumes"]):
                    is_bio = True
                if is_bio:
                    st.success("Bio")
            
            # Dessert
            with day_cols[2]:
                st.markdown("<b>Dessert</b>", unsafe_allow_html=True)
                dessert_text = " + ".join([x for x in [row["Dessert"], row["Laitage"]] if str(x) != "nan"])
                st.markdown(f"<div class='menu-item'>{dessert_text}</div>", unsafe_allow_html=True)
                # Check if columns exist before trying to access them
                is_bio = False
                if "Code_dessert" in row and "AB" in str(row["Code_dessert"]):
                    is_bio = True
                if "Code_laitage" in row and "AB" in str(row["Code_laitage"]):
                    is_bio = True
                if is_bio:
                    st.success("Bio")
            
            st.markdown("</div>", unsafe_allow_html=True)