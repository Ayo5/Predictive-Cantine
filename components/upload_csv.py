import streamlit as st
import pandas as pd
import os
from datetime import datetime
import numpy as np
from data_loader import prepare_dataset
from config import NUM_WEEKS, CSV_PREDICTIONS, CSV_CO2_COUTS

def upload_csv_section():
    st.markdown("<h2 class='section-header'>Importer un fichier CSV</h2>", unsafe_allow_html=True)
    
    csv_tabs = st.tabs(["Données des menus", "Données CO2 et coûts"])
    
    with csv_tabs[0]:
        st.subheader("Importer les données des menus")
        uploaded_menu_file = st.file_uploader("Choisissez un fichier CSV pour les menus", type="csv", key="menu_csv")
        
        if uploaded_menu_file is not None:
            try:
                df = pd.read_csv(uploaded_menu_file)
                
                st.write("Aperçu des données:")
                st.dataframe(df.head())
                
                required_columns = ["Date", "Entrée", "Plat", "Légumes", "Dessert", "Laitage"]
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"Colonnes manquantes dans le fichier CSV: {', '.join(missing_columns)}")
                    st.info("Le fichier CSV doit contenir au minimum les colonnes: Date, Entrée, Plat, Légumes, Dessert, Laitage")
                    return None
                
                os.makedirs("uploads", exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"uploads/uploaded_{timestamp}.csv"
                df.to_csv(file_path, index=False)
                
                data_dir = os.path.dirname(CSV_PREDICTIONS)
                os.makedirs(data_dir, exist_ok=True)
                df.to_csv(CSV_PREDICTIONS, index=False)
                
                with st.spinner('Traitement des données en cours...'):
                    processed_data = prepare_dataset(df, NUM_WEEKS)
                    
                    st.success("Prédictions générées avec succès!")
                    
                    st.write("Résultats des prédictions:")
                    results_df = processed_data[['Date', 'Entrée', 'Plat', 'Légumes', 'Dessert', 'Laitage', 'Taux de gaspillage', 'Taux de participation']]
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
        uploaded_co2_file = st.file_uploader("Choisissez un fichier CSV pour les données CO2 et coûts", type="csv", key="co2_csv")
        
        if uploaded_co2_file is not None:
            try:
                co2_df = pd.read_csv(uploaded_co2_file)
                
                st.write("Aperçu des données CO2 et coûts:")
                st.dataframe(co2_df.head())
                
                required_columns = ["Nom", "Kg CO2 pour 1 kilo ou 1L", "Prix Unitaire Kg"]
                missing_columns = [col for col in required_columns if col not in co2_df.columns]
                
                if missing_columns:
                    st.error(f"Colonnes manquantes dans le fichier CSV: {', '.join(missing_columns)}")
                    st.info("Le fichier CSV doit contenir au minimum les colonnes: Nom, Kg CO2 pour 1 kilo ou 1L, Prix Unitaire Kg")
                    return None
                
                os.makedirs("uploads", exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                co2_file_path = f"uploads/co2_couts_{timestamp}.csv"
                co2_df.to_csv(co2_file_path, index=False)
                
                # Save as the main CO2 data source
                data_dir = os.path.dirname(CSV_CO2_COUTS)
                os.makedirs(data_dir, exist_ok=True)
                co2_df.to_csv(CSV_CO2_COUTS, index=False)
                
                st.success("Données CO2 et coûts importées avec succès!")
                
                # Display some statistics
                st.subheader("Statistiques des données CO2 et coûts")
                
                avg_co2 = co2_df["Kg CO2 pour 1 kilo ou 1L"].mean()
                max_co2_item = co2_df.loc[co2_df["Kg CO2 pour 1 kilo ou 1L"].idxmax()]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Émission CO2 moyenne", f"{avg_co2:.2f} kg/kg")
                with col2:
                    st.metric("Aliment avec le plus d'émissions", 
                             f"{max_co2_item['Nom']} ({max_co2_item['Kg CO2 pour 1 kilo ou 1L']:.2f} kg/kg)")
                
                # Create a bar chart of CO2 emissions
                st.subheader("Émissions CO2 par aliment")
                chart_data = co2_df.sort_values("Kg CO2 pour 1 kilo ou 1L", ascending=False).head(10)
                st.bar_chart(chart_data.set_index("Nom")["Kg CO2 pour 1 kilo ou 1L"])
                
            except Exception as e:
                st.error(f"Erreur lors du traitement du fichier CO2: {str(e)}")
    
    return None