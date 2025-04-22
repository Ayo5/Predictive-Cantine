import streamlit as st
import pandas as pd
from config import CSV_PREDICTIONS, WEEKDAYS
from menu_generator import get_current_menu
from menu_comments import get_daily_menu_comment, get_weekly_waste_tip

def display_menu_section(col, current_week):
    col.markdown("<h2 class='section-header'>Menu de la semaine</h2>", unsafe_allow_html=True)
    week_menus, prix_semaine, _ = get_current_menu(current_week)
    weekly_tip = get_weekly_waste_tip()
    col.info(weekly_tip)
    
    csv_data = pd.read_csv(CSV_PREDICTIONS)
    
    for i, row in enumerate(week_menus):
        with col.container():
            st.markdown(f"<div class='menu-day'>", unsafe_allow_html=True)
            
            st.markdown(f"<h3>{WEEKDAYS[row['Date'].weekday()]} ({row['Date'].strftime('%d-%m-%Y')})</h3>", unsafe_allow_html=True)
            
            unique_menus = csv_data.drop_duplicates(subset=['Plat', 'Légumes']).head(10)
            
            menu_options = []
            for j, menu_option in enumerate(unique_menus.iterrows()):
                _, menu_data = menu_option
                plat_desc = f"{menu_data['Plat']}"
                if not pd.isna(menu_data.get('Légumes', '')):
                    plat_desc += f" + {menu_data['Légumes']}"
                menu_options.append(f"Option {j+1}: {plat_desc}")
            
            str_date = row["Date"].strftime("%d-%m-%Y")
            current_index = st.session_state["skips"].get(str_date, 0)
            if current_index >= len(menu_options):
                current_index = 0
                st.session_state["skips"][str_date] = 0
            
            selected_option = st.selectbox(
                "Choisir un menu alternatif:",
                menu_options,
                index=current_index,
                key=f"menu_select_{str_date}"
            )
            
            new_index = menu_options.index(selected_option)
            if new_index != current_index:
                st.session_state["skips"][str_date] = new_index
                st.experimental_rerun()
            
            day_cols = st.columns(3)
            
            with day_cols[0]:
                st.markdown("<b>Entrée</b>", unsafe_allow_html=True)
                st.markdown(f"<div class='menu-item'>{row['Entrée']}</div>", unsafe_allow_html=True)
                if "Code_entrée" in row and "AB" in str(row["Code_entrée"]):
                    st.success("Bio")
            
            with day_cols[1]:
                st.markdown("<b>Plat</b>", unsafe_allow_html=True)
                plat_text = " + ".join([x for x in [row["Plat"], row["Légumes"]] if str(x) != "nan"])
                st.markdown(f"<div class='menu-item'>{plat_text}</div>", unsafe_allow_html=True)
                is_bio = False
                if "Code_plat" in row and "AB" in str(row["Code_plat"]):
                    is_bio = True
                if "Code_légumes" in row and "AB" in str(row["Code_légumes"]):
                    is_bio = True
                if is_bio:
                    st.success("Bio")
            
            with day_cols[2]:
                st.markdown("<b>Dessert</b>", unsafe_allow_html=True)
                dessert_text = " + ".join([x for x in [row["Dessert"], row["Laitage"]] if str(x) != "nan"])
                st.markdown(f"<div class='menu-item'>{dessert_text}</div>", unsafe_allow_html=True)
                is_bio = False
                if "Code_dessert" in row and "AB" in str(row["Code_dessert"]):
                    is_bio = True
                if "Code_laitage" in row and "AB" in str(row["Code_laitage"]):
                    is_bio = True
                if is_bio:
                    st.success("Bio")
            
            # Ajouter un commentaire sur la réduction du gaspillage pour ce menu
            menu_comment = get_daily_menu_comment(row)
            st.markdown(f"<div class='menu-comment'><i>💡 {menu_comment}</i></div>", unsafe_allow_html=True)
            
            # Afficher les indicateurs de gaspillage et participation
            metrics_cols = st.columns(2)
            with metrics_cols[0]:
                participation = row.get('Taux de participation', 0.8) * 100
                st.metric("Participation", f"{participation:.1f}%")
            
            with metrics_cols[1]:
                waste = row.get('Taux de gaspillage', 0.2) * 100
                st.metric("Gaspillage", f"{waste:.1f}%", 
                          delta=f"{-5:.1f}%" if waste < 25 else f"{5:.1f}%",
                          delta_color="inverse")
            
            st.markdown("</div>", unsafe_allow_html=True)