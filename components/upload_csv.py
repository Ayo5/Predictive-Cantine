import streamlit as st
import pandas as pd
import os
from datetime import datetime
import numpy as np
from data_loader import prepare_dataset
from config import NUM_WEEKS, CSV_PREDICTIONS, CSV_CO2_COUTS


def upload_csv_section():
    st.markdown(
        "<h2 class='section-header'>Importer un fichier CSV</h2>",
        unsafe_allow_html=True,
    )

    csv_tabs = st.tabs(["Données des menus", "Données CO2 et coûts", "Saisie manuelle"])

    with csv_tabs[0]:
        st.subheader("Importer les données des menus")
        uploaded_menu_file = st.file_uploader(
            "Choisissez un fichier CSV pour les menus", type="csv", key="menu_csv"
        )

        if uploaded_menu_file is not None:
            try:
                df = pd.read_csv(uploaded_menu_file)

                st.write("Aperçu des données:")
                st.dataframe(df.head())

                required_columns = [
                    "Date",
                    "Entrée",
                    "Plat",
                    "Légumes",
                    "Dessert",
                    "Laitage",
                ]
                missing_columns = [
                    col for col in required_columns if col not in df.columns
                ]

                if missing_columns:
                    st.error(
                        f"Colonnes manquantes dans le fichier CSV: {', '.join(missing_columns)}"
                    )
                    st.info(
                        "Le fichier CSV doit contenir au minimum les colonnes: Date, Entrée, Plat, Légumes, Dessert, Laitage"
                    )
                    return None

                os.makedirs("uploads", exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"uploads/menu.csv"
                df.to_csv(file_path, index=False)

                data_dir = os.path.dirname(CSV_PREDICTIONS)
                os.makedirs(data_dir, exist_ok=True)
                df.to_csv(CSV_PREDICTIONS, index=False)

                with st.spinner("Traitement des données en cours..."):
                    processed_data = prepare_dataset(df, NUM_WEEKS)

                    st.success("Prédictions générées avec succès!")

                    st.write("Résultats des prédictions:")
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

    with csv_tabs[1]:
        st.subheader("Importer les données CO2 et coûts")
        uploaded_co2_file = st.file_uploader(
            "Choisissez un fichier CSV pour les données CO2 et coûts",
            type="csv",
            key="co2_csv",
        )

        if uploaded_co2_file is not None:
            try:
                co2_df = pd.read_csv(uploaded_co2_file)

                st.write("Aperçu des données CO2 et coûts:")
                st.dataframe(co2_df.head())

                required_columns = [
                    "Nom",
                    "Kg CO2 pour 1 kilo ou 1L",
                    "Prix Unitaire Kg",
                ]
                missing_columns = [
                    col for col in required_columns if col not in co2_df.columns
                ]

                if missing_columns:
                    st.error(
                        f"Colonnes manquantes dans le fichier CSV: {', '.join(missing_columns)}"
                    )
                    st.info(
                        "Le fichier CSV doit contenir au minimum les colonnes: Nom, Kg CO2 pour 1 kilo ou 1L, Prix Unitaire Kg"
                    )
                    return None

                os.makedirs("uploads", exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                co2_file_path = f"uploads/couts.csv"
                co2_df.to_csv(co2_file_path, index=False)

                data_dir = os.path.dirname(CSV_CO2_COUTS)
                os.makedirs(data_dir, exist_ok=True)
                co2_df.to_csv(CSV_CO2_COUTS, index=False)

                st.success("Données CO2 et coûts importées avec succès!")

                st.subheader("Statistiques des données CO2 et coûts")

                avg_co2 = co2_df["Kg CO2 pour 1 kilo ou 1L"].mean()
                max_co2_item = co2_df.loc[co2_df["Kg CO2 pour 1 kilo ou 1L"].idxmax()]

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Émission CO2 moyenne", f"{avg_co2:.2f} kg/kg")
                with col2:
                    st.metric(
                        "Aliment avec le plus d'émissions",
                        f"{max_co2_item['Nom']} ({max_co2_item['Kg CO2 pour 1 kilo ou 1L']:.2f} kg/kg)",
                    )

                st.subheader("Émissions CO2 par aliment")
                chart_data = co2_df.sort_values(
                    "Kg CO2 pour 1 kilo ou 1L", ascending=False
                ).head(10)
                st.bar_chart(chart_data.set_index("Nom")["Kg CO2 pour 1 kilo ou 1L"])

            except Exception as e:
                st.error(f"Erreur lors du traitement du fichier CO2: {str(e)}")

    with csv_tabs[2]:
        st.subheader("Saisie manuelle des données")

        # Saisie des données pour le menu
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
        humidite = st.number_input(
            "Humidité", min_value=0.0, max_value=100.0, value=50.0
        )
        vitesse_vent = st.number_input(
            "Vitesse du vent", min_value=0.0, max_value=10.0, value=5.0
        )
        attente_moyenne = st.number_input(
            "Attente moyenne (minutes)", min_value=0, max_value=120, value=30
        )

        if st.button("Ajouter au CSV des menus"):
            new_data = {
                "Date": date.strftime("%Y-%m-%d"),
                "Entrée": entree,
                "Plat": plat,
                "Légumes": legumes,
                "Dessert": dessert,
                "Laitage": laitage,
                "Gouter": gouter,
                "Température": temperature,
                "Humidité": humidite,
                "Vitesse du vent moyen 10 mn": vitesse_vent,
                "Attente moyenne": attente_moyenne,
            }
            df = pd.DataFrame([new_data])
            df.to_csv(CSV_PREDICTIONS, mode="a", header=False, index=False)
            st.success("Données ajoutées avec succès au CSV des menus!")

        # Saisie des données CO2 et coûts
        st.markdown("### Saisie des données CO2 et coûts")
        nom = st.text_input("Nom de l'aliment")
        co2 = st.number_input("Kg CO2 pour 1 kilo ou 1L", min_value=0.0)
        prix = st.number_input("Prix Unitaire Kg", min_value=0.0)

        if st.button("Ajouter au CSV CO2 et coûts"):
            new_co2_data = {
                "Nom": nom,
                "Kg CO2 pour 1 kilo ou 1L": co2,
                "Portion 100g": co2 / 10,
                "Prix Unitaire Kg": prix,
            }
            co2_df = pd.DataFrame([new_co2_data])
            co2_df.to_csv(CSV_CO2_COUTS, mode="a", header=False, index=False)
            st.success("Données ajoutées avec succès au CSV CO2 et coûts!")

    return None
