import streamlit as st
import pandas as pd
import os
from datetime import datetime
import numpy as np
from data_loader import prepare_dataset
from config import NUM_WEEKS, CSV_PREDICTIONS, CSV_CO2_COUTS, TRAIN_DATA


def validate_columns(df, required_columns, file_type):
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(
            f"Colonnes manquantes dans le fichier CSV: {', '.join(missing_columns)}"
        )
        st.info(
            f"Le fichier CSV doit contenir au minimum les colonnes: {', '.join(required_columns)}"
        )
        return False
    return True


def save_file(df, directory, filename, copy_path=None):
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)
    df.to_csv(file_path, index=False)

    if copy_path:
        os.makedirs(os.path.dirname(copy_path), exist_ok=True)
        df.to_csv(copy_path, index=False)


def process_menu_file(uploaded_file):
    if uploaded_file is None:
        return None

    try:
        df = pd.read_csv(uploaded_file)
        st.write("Aperçu des données:")
        st.dataframe(df.head())

        required_columns = ["Date", "Entrée", "Plat", "Légumes", "Dessert", "Laitage"]
        if not validate_columns(df, required_columns, "menu"):
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_file(df, "uploads", "menu.csv", CSV_PREDICTIONS)

        with st.spinner("Traitement des données en cours..."):
            processed_data = prepare_dataset(df, NUM_WEEKS)
            st.success("Prédictions générées avec succès!")

            results_df = processed_data[
                [
                    "Date",
                    "Entrée",
                    "Plat",
                    "Légumes",
                    "Dessert",
                    "Laitage",
                    "Taux gaspillage",
                    "Taux participation",
                ]
            ]
            st.dataframe(results_df)

            csv = results_df.to_csv(index=False)
            st.download_button(
                label="Télécharger les résultats",
                data=csv,
                file_name=f"predictions_{timestamp}.csv",
                mime="text/csv",
            )
            return processed_data

    except Exception as e:
        st.error(f"Erreur lors du traitement du fichier: {str(e)}")
        return None


def process_co2_file(uploaded_file):
    if uploaded_file is None:
        return None

    try:
        df = pd.read_csv(uploaded_file)
        st.write("Aperçu des données CO2 et coûts:")
        st.dataframe(df.head())

        required_columns = ["Nom", "Kg CO2 pour 1 kilo ou 1L", "Prix Unitaire Kg"]
        if not validate_columns(df, required_columns, "co2"):
            return None

        save_file(df, "uploads", "couts.csv", CSV_CO2_COUTS)
        st.success("Données CO2 et coûts importées avec succès!")

        display_co2_statistics(df)

    except Exception as e:
        st.error(f"Erreur lors du traitement du fichier CO2: {str(e)}")


def process_train_file(uploaded_file):
    if uploaded_file is None:
        return None

    try:
        df = pd.read_csv(uploaded_file)
        st.write("Aperçu des données d'entraînement:")
        st.dataframe(df.head())

        required_columns = [
            "Date",
            "Entrée",
            "Plat",
            "Légumes",
            "Laitage",
            "Dessert",
            "Gouter",
            "Taux participation",
            "Température",
            "Humidité",
            "Vitesse du vent moyen 10 mn",
            "Taux gaspillage",
            "Attente moyenne",
        ]
        if not validate_columns(df, required_columns, "train"):
            return None

        save_file(df, "data", "train_data.csv", TRAIN_DATA)
        st.success("Données d'entraînement importées avec succès!")

    except Exception as e:
        st.error(f"Erreur lors du traitement du fichier d'entraînement: {str(e)}")


def display_co2_statistics(df):
    st.subheader("Statistiques des données CO2 et coûts")

    avg_co2 = df["Kg CO2 pour 1 kilo ou 1L"].mean()
    max_co2_item = df.loc[df["Kg CO2 pour 1 kilo ou 1L"].idxmax()]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Émission CO2 moyenne", f"{avg_co2:.2f} kg/kg")
    with col2:
        st.metric(
            "Aliment avec le plus d'émissions",
            f"{max_co2_item['Nom']} ({max_co2_item['Kg CO2 pour 1 kilo ou 1L']:.2f} kg/kg)",
        )

    st.subheader("Émissions CO2 par aliment")
    chart_data = df.sort_values("Kg CO2 pour 1 kilo ou 1L", ascending=False).head(10)
    st.bar_chart(chart_data.set_index("Nom")["Kg CO2 pour 1 kilo ou 1L"])


def upload_csv_section():
    st.markdown(
        "<h2 class='section-header'>Importer un fichier CSV</h2>",
        unsafe_allow_html=True,
    )

    csv_tabs = st.tabs(
        ["Données des menus", "Données CO2 et coûts", "Entrainement", "Saisie manuelle"]
    )

    with csv_tabs[0]:
        st.subheader("Importer les données des menus")
        process_menu_file(
            st.file_uploader(
                "Choisissez un fichier CSV pour les menus", type="csv", key="menu_csv"
            )
        )

    with csv_tabs[1]:
        st.subheader("Importer les données CO2 et coûts")
        process_co2_file(
            st.file_uploader(
                "Choisissez un fichier CSV pour les données CO2 et coûts",
                type="csv",
                key="co2_csv",
            )
        )

    with csv_tabs[2]:
        st.subheader("Importer les données d'entraînement")
        process_train_file(
            st.file_uploader(
                "Choisissez un fichier CSV pour les données d'entraînement",
                type="csv",
                key="data_train_csv",
            )
        )

    with csv_tabs[3]:
        st.subheader("Saisie manuelle des données")
        manual_data_entry()


def manual_data_entry():
    st.markdown("### Saisie des données du menu")
    date = st.date_input("Date")
    entree = st.text_input("Entrée")
    plat = st.text_input("Plat")
    legumes = st.text_input("Légumes")
    dessert = st.text_input("Dessert")
    laitage = st.text_input("Laitage")
    gouter = st.text_input("Gouter")
    temperature = st.number_input(
        "Température", min_value=-20.0, max_value=40.0, value=20.0
    )
    humidite = st.number_input("Humidité", min_value=0.0, max_value=100.0, value=50.0)
    vitesse_vent = st.number_input(
        "Vitesse du vent", min_value=0.0, max_value=100.0, value=10.0
    )
    taux_participation = st.number_input(
        "Taux de participation", min_value=0.0, max_value=1.0, value=0.8
    )
    taux_gaspillage = st.number_input(
        "Taux de gaspillage", min_value=0.0, max_value=1.0, value=0.2
    )
    attente_moyenne = st.number_input(
        "Attente moyenne", min_value=0, max_value=60, value=15
    )

    if st.button("Enregistrer les données"):
        data = {
            "Date": [date],
            "Entrée": [entree],
            "Plat": [plat],
            "Légumes": [legumes],
            "Dessert": [dessert],
            "Laitage": [laitage],
            "Gouter": [gouter],
            "Température": [temperature],
            "Humidité": [humidite],
            "Vitesse du vent moyen 10 mn": [vitesse_vent],
            "Taux participation": [taux_participation],
            "Taux gaspillage": [taux_gaspillage],
            "Attente moyenne": [attente_moyenne],
        }
        df = pd.DataFrame(data)
        save_file(df, "data", "train_data.csv", TRAIN_DATA)
        st.success("Données enregistrées avec succès!")
