import streamlit as st
import pandas as pd
from config import WEEKDAYS
from menu_generator import get_current_menu
from menu_comments import get_daily_menu_comment, get_weekly_waste_tip


def display_menu_section(col, current_week):
    col.markdown(
        "<h2 class='section-header'>Menu de la semaine</h2>", unsafe_allow_html=True
    )
    week_menus, prix_semaine, _ = get_current_menu(current_week)
    weekly_tip = get_weekly_waste_tip()
    col.info(weekly_tip)

    for i, row in enumerate(week_menus):
        with col.container():
            str_date = row["Date"]
            taux_participation = row.get("Taux participation", 0.8)
            taux_participation_predit = row.get("Taux participation prédit", 0.8)
            taux_gaspillage = row.get("Taux gaspillage", 0.2)
            taux_gaspillage_predit = row.get("Taux gaspillage prédit", 0.2)

            html_content = f"""<div class='menu-day'>
    <h3>{WEEKDAYS[i]} ({str_date})</h3>
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
                delta_calc_participation = (
                    (taux_participation_predit - taux_participation) * 100
                    if not pd.isna(taux_participation)
                    else None
                )
                st.metric(
                    "Taux de participation",
                    f"{taux_participation_predit*100:.1f}%",
                    delta=(
                        f"{delta_calc_participation:+.1f}%"
                        if delta_calc_participation is not None
                        else None
                    ),
                )

            with metrics_cols[1]:
                delta_calc_waste = (
                    (taux_gaspillage_predit - taux_gaspillage) * 100
                    if not pd.isna(taux_gaspillage)
                    else None
                )
                st.metric(
                    "Taux de gaspillage",
                    f"{taux_gaspillage_predit*100:.1f}%",
                    delta=(
                        f"{delta_calc_waste:+.1f}%"
                        if delta_calc_waste is not None
                        else None
                    ),
                    delta_color="inverse",
                )
