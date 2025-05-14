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
                st.rerun()

            html_content = f"""<div class='menu-day'>
    <h3>{WEEKDAYS[row['Date'].weekday()]} ({row['Date'].strftime('%d-%m-%Y')})</h3>
    <div class='menu-content'>
        <div class='menu-section'>
            <b>Entrée</b>
            <div class='menu-item'>{row['Entrée']}</div>
            {f"<div class='bio-tag'>Bio</div>" if "Code_entrée" in row and "AB" in str(row["Code_entrée"]) else ""}</div> 
        <div class='menu-section'>
            <b>Plat</b>
            <div class='menu-item'>{" + ".join([x for x in [row["Plat"], row["Légumes"]] if str(x) != "nan"])}</div>
            {f"<div class='bio-tag'>Bio</div>" if ("Code_plat" in row and "AB" in str(row["Code_plat"])) or ("Code_légumes" in row and "AB" in str(row["Code_légumes"])) else ""}</div>
        <div class='menu-section'>
            <b>Dessert</b>
            <div class='menu-item'>{" + ".join([x for x in [row["Dessert"], row["Laitage"]] if str(x) != "nan"])}</div>
            {f"<div class='bio-tag'>Bio</div>" if ("Code_dessert" in row and "AB" in str(row["Code_dessert"])) or ("Code_laitage" in row and "AB" in str(row["Code_laitage"])) else ""}</div>
    </div>
    <div class='menu-comment'>
        <i>💡 {get_daily_menu_comment(row)}</i>
    </div>
    
</div>"""
            
          
            st.markdown(html_content, unsafe_allow_html=True)
            
            metrics_cols = st.columns(2)
            with metrics_cols[0]:
                participation = row.get('Taux de participation', 0.8) * 100
                st.metric("Participation", f"{participation:.1f}%")
            with metrics_cols[1]:
                waste = row.get('Taux de gaspillage', 0.2) * 100
                st.metric(
                    "Gaspillage", f"{waste:.1f}%",
                    delta=f"{-5:.1f}%" if waste < 25 else f"{5:.1f}%",
                    delta_color="inverse"
                )
