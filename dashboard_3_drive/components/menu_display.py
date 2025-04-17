import streamlit as st
from config import WEEKDAYS
from menu_generator import get_current_menu

def display_menu_section(col, current_week):
    """Display the menu section"""
    col.markdown("<h2 class='section-header'>Menu de la semaine</h2>", unsafe_allow_html=True)
    week_menus, prix_semaine, _ = get_current_menu(current_week)
    
    for i, row in enumerate(week_menus):
        # Create a container for each day's menu
        with col.container():
            st.markdown(f"<div class='menu-day'>", unsafe_allow_html=True)
            
            # Day header with date
            st.markdown(f"<h3>{WEEKDAYS[row['Date'].weekday()]} ({row['Date'].strftime('%d-%m-%Y')})</h3>", unsafe_allow_html=True)
            
            # Button to change menu
            btn = st.button("Changer de menu", key=f"redo_{row['Date']}")
            if btn:
                str_date = row["Date"].strftime("%d-%m-%Y")
                st.session_state["skips"][str_date] = st.session_state["skips"].get(str_date, 0) + 1
                week_menus, prix_semaine, _ = get_current_menu(current_week)
                row = week_menus[i]
            
            # Menu items in columns
            day_cols = st.columns(3)
            
            # Entrée
            with day_cols[0]:
                st.markdown("<b>Entrée</b>", unsafe_allow_html=True)
                st.markdown(f"<div class='menu-item'>{row['Entrée']}</div>", unsafe_allow_html=True)
                if "AB" in str(row["Code_entrée"]):
                    st.success("Bio")
            
            # Plat
            with day_cols[1]:
                st.markdown("<b>Plat</b>", unsafe_allow_html=True)
                plat_text = " + ".join([x for x in [row["Plat"], row["Légumes"]] if str(x) != "nan"])
                st.markdown(f"<div class='menu-item'>{plat_text}</div>", unsafe_allow_html=True)
                if "AB" in str(row["Code_plat"]) or "AB" in str(row["Code_légumes"]):
                    st.success("Bio")
            
            # Dessert
            with day_cols[2]:
                st.markdown("<b>Dessert</b>", unsafe_allow_html=True)
                dessert_text = " + ".join([x for x in [row["Dessert"], row["Laitage"]] if str(x) != "nan"])
                st.markdown(f"<div class='menu-item'>{dessert_text}</div>", unsafe_allow_html=True)
                if "AB" in str(row["Code_dessert"]) or "AB" in str(row["Code_laitage"]):
                    st.success("Bio")
            
            st.markdown("</div>", unsafe_allow_html=True)