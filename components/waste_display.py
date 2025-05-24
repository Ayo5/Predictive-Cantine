import streamlit as st
import pandas as pd
import altair as alt
from config import WEEKDAYS, DEFAULT_DELAY_MAIN_DISH, DEFAULT_DELAY_MENU, PREDICTIONS
from menu_generator import get_current_menu
import os


def display_waste_section(col, current_week):
    """Display the waste and CO2 section"""

    week_menus, prix_semaine, co2 = get_current_menu(current_week)

    gaspillage_initial = []
    gaspillage_prevu = []

    for menu in week_menus:
        if "Taux gaspillage" in menu and pd.notna(menu["Taux gaspillage"]):
            gaspillage_initial.append(float(menu["Taux gaspillage"]) * 100)
        else:
            gaspillage_initial.append(20.0)

        if "Taux gaspillage prédit" in menu and pd.notna(
            menu["Taux gaspillage prédit"]
        ):
            gaspillage_prevu.append(float(menu["Taux gaspillage prédit"]) * 100)
        else:
            gaspillage_prevu.append(20.0)

    while len(gaspillage_initial) < 5:
        gaspillage_initial.append(20.0)
    while len(gaspillage_prevu) < 5:
        gaspillage_prevu.append(20.0)

    gaspillage_initial = gaspillage_initial[:5]
    gaspillage_prevu = gaspillage_prevu[:5]

    col.markdown(
        "<h2 class='section-header'>Gaspillage et CO2</h2>", unsafe_allow_html=True
    )

    gaspillage_moyen_initial = (
        sum(gaspillage_initial) / len(gaspillage_initial) if gaspillage_initial else 0
    )
    gaspillage_moyen_prevu = (
        sum(gaspillage_prevu) / len(gaspillage_prevu) if gaspillage_prevu else 0
    )
    reduction_gaspillage = gaspillage_moyen_initial - gaspillage_moyen_prevu

    if co2 <= 0:
        co2 = 0
        for menu in week_menus:
            co2 += 2.0  # Valeur de base par repas

            if "Plat" in menu and pd.notna(menu["Plat"]):
                plat = str(menu["Plat"]).lower()
                if any(viande in plat for viande in ["bœuf", "steak", "veau"]):
                    co2 += 5.0
                elif any(viande in plat for viande in ["porc", "jambon"]):
                    co2 += 2.0
                elif any(viande in plat for viande in ["poulet", "volaille", "dinde"]):
                    co2 += 1.5
                elif any(poisson in plat for poisson in ["poisson", "saumon", "thon"]):
                    co2 += 1.8

    cols3_1_metrics = col.columns(3)
    cols3_1_metrics[0].metric(
        "Gaspillage initial", f"{gaspillage_moyen_initial:.1f}%", delta=None
    )

    cols3_1_metrics[1].metric(
        "Gaspillage prévu",
        f"{gaspillage_moyen_prevu:.1f}%",
        (
            f"-{reduction_gaspillage:.1f}%"
            if reduction_gaspillage > 0
            else f"+{-reduction_gaspillage:.1f}%"
        ),
        delta_color="inverse",
    )

    cols3_1_metrics[2].metric(
        "Empreinte CO2",
        f"{co2:.1f} kg",
        f"{co2/5:.2f} kg/jour" if len(week_menus) > 0 else "0.00 kg/jour",
    )

    col.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    display_waste_chart(col, gaspillage_initial, gaspillage_prevu)
    display_bio_products(col, week_menus)
    display_parameters(col)

    if col.button("📄 Générer le rapport PDF de la semaine"):
        try:
            from components.report_generator import generate_weekly_report

            filename = generate_weekly_report(
                week_menus, prix_semaine, co2, gaspillage_initial, gaspillage_prevu
            )
            with open(filename, "rb") as pdf_file:
                col.download_button(
                    label="📥 Télécharger le rapport PDF",
                    data=pdf_file,
                    file_name=os.path.basename(filename),
                    mime="application/pdf",
                )
        except Exception as e:
            col.error(f"Erreur lors de la génération du rapport : {str(e)}")


def display_waste_chart(col, gaspillage_initial, gaspillage_prevu):
    """Display waste comparison charts"""
    jours = [f"{i+1} - {w}" for i, w in enumerate(WEEKDAYS)]
    chart_cols = col.columns(2)

    gaspillage_initial_df = pd.DataFrame(
        {"Jour": jours, "Pourcentage": gaspillage_initial}
    )

    gaspillage_initial_df = gaspillage_initial_df.dropna()

    if not gaspillage_initial_df.empty:
        chart_initial = (
            alt.Chart(gaspillage_initial_df)
            .mark_bar(color="#ff9999")  # Rouge pour initial
            .encode(
                x=alt.X("Jour:N", title="Jour de la semaine"),
                y=alt.Y("Pourcentage:Q", title="Gaspillage (%)"),
                tooltip=["Jour", "Pourcentage"],
            )
            .properties(title="Gaspillage initial")
        )

        # Affichage du graphique initial
        chart_cols[0].altair_chart(chart_initial, use_container_width=True)
    else:
        chart_cols[0].warning("Aucune donnée de gaspillage initial disponible.")

    # Graphique pour le taux de gaspillage prédit
    gaspillage_prevu_df = pd.DataFrame({"Jour": jours, "Pourcentage": gaspillage_prevu})

    # Filtrer les valeurs None ou NaN
    gaspillage_prevu_df = gaspillage_prevu_df.dropna()

    if not gaspillage_prevu_df.empty:
        chart_prevu = (
            alt.Chart(gaspillage_prevu_df)
            .mark_bar(color="#5fa059")  # Vert pour prévu
            .encode(
                x=alt.X("Jour:N", title="Jour de la semaine"),
                y=alt.Y("Pourcentage:Q", title="Gaspillage (%)"),
                tooltip=["Jour", "Pourcentage"],
            )
            .properties(title="Gaspillage prédit")
        )

        # Affichage du graphique prédit
        chart_cols[1].altair_chart(chart_prevu, use_container_width=True)
    else:
        chart_cols[1].warning("Aucune donnée de gaspillage prédit disponible.")


def display_bio_products(col, week_menus):
    """Display bio products section"""
    col.markdown("<h2 class='section-header'></h2>", unsafe_allow_html=True)

    have_bio = False
    bio_items = []

    for row in week_menus:
        cols_codes = [
            "Code_entrée",
            "Code_plat",
            "Code_légumes",
            "Code_laitage",
            "Code_dessert",
        ]
        cols_dish = ["Entrée", "Plat", "Légumes", "Laitage", "Dessert"]

        for code, dish in zip(cols_codes, cols_dish):
            if code in row and dish in row:
                if "AB" in str(row[code]) and not pd.isna(row[dish]):
                    bio_items.append(row[dish])
                    have_bio = True

    if have_bio:
        for item in bio_items:
            col.markdown(
                f"<div style='background-color:#e6f7e6; padding:5px; border-radius:5px; margin-bottom:5px;'>🌱 {item}</div>",
                unsafe_allow_html=True,
            )
    else:
        col.error("Pas de bio cette semaine !")


def display_parameters(col):
    """Display parameters section"""
    col.markdown("<h2 class='section-header'>Paramètres</h2>", unsafe_allow_html=True)

    global delay_main_dish, delay_menu

    delay_main_dish = col.slider(
        "Délai d'apparition entre deux plats identiques (en jours)",
        min_value=1,
        max_value=30,
        value=DEFAULT_DELAY_MAIN_DISH,
        step=1,
    )

    delay_menu = col.slider(
        "Délai d'apparition entre deux menus identiques (en jours)",
        min_value=1,
        max_value=90,
        value=DEFAULT_DELAY_MENU,
        step=1,
    )
