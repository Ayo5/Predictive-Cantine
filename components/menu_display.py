import streamlit as st
import pandas as pd
from config import PREDICTIONS, WEEKDAYS
from menu_generator import get_current_menu
from menu_comments import get_daily_menu_comment, get_weekly_waste_tip


def display_menu_section(col, current_week):
    col.markdown(
        "<h2 class='section-header'>Menu de la semaine</h2>", unsafe_allow_html=True
    )
    week_menus, prix_semaine, _ = get_current_menu(current_week)
    print("la variable bizarre _ :", _)
    print("la varibale prix semaine :", prix_semaine)
    print
    weekly_tip = get_weekly_waste_tip()
    col.info(weekly_tip)

    csv_data = pd.read_csv(PREDICTIONS)
    print("csv_data :", csv_data)
    print(csv_data.columns)

    colonnes_a_convertir = [
        "Taux participation prédit",
        "Taux participation",
        "Taux gaspillage prédit",
        "Taux gaspillage",
    ]

    for colonne in colonnes_a_convertir:
        if colonne in csv_data.columns:
            csv_data[colonne] = pd.to_numeric(csv_data[colonne], errors="coerce")

    for i, row in enumerate(week_menus):
        with col.container():
            str_date = row["Date"].strftime("%d-%m-%Y")

            # Trouver la ligne correspondante dans csv_data en fonction du Plat et des Légumes
            matched_row = csv_data[
                (csv_data["Plat"] == row["Plat"])
                & (csv_data["Légumes"] == row["Légumes"])
            ]

            if not matched_row.empty:
                matched_row = matched_row.iloc[0]
            else:
                matched_row = None

            unique_menus = csv_data.drop_duplicates(subset=["Plat", "Légumes"]).head(10)
            menu_options = []
            for j, menu_option in enumerate(unique_menus.iterrows()):
                _, menu_data = menu_option
                plat_desc = f"{menu_data['Plat']}"
                if not pd.isna(menu_data.get("Légumes", "")):
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
                key=f"menu_select_{str_date}",
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
                participation = 0.8  # Valeur par défaut
                if matched_row is not None:
                    if "Taux participation prédit" in matched_row and not pd.isna(
                        matched_row["Taux participation prédit"]
                    ):
                        participation = matched_row["Taux participation prédit"]
                    elif "Taux participation" in matched_row and not pd.isna(
                        matched_row["Taux participation"]
                    ):
                        participation = matched_row["Taux participation"]
                st.metric("Participation", f"{participation*100:.1f}%")

            with metrics_cols[1]:
                waste = 0.2  # Valeur par défaut
                if matched_row is not None:
                    if "Taux gaspillage prédit" in matched_row and not pd.isna(
                        matched_row["Taux gaspillage prédit"]
                    ):
                        waste = matched_row["Taux gaspillage prédit"]
                    elif "Taux gaspillage" in matched_row and not pd.isna(
                        matched_row["Taux gaspillage"]
                    ):
                        waste = matched_row["Taux gaspillage"]
                st.metric(
                    "Gaspillage",
                    f"{waste*100:.1f}%",
                    delta=f"{-5:.1f}%" if waste < 0.25 else f"{5:.1f}%",
                    delta_color="inverse",
                )
