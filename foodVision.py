import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import datetime
import random

# Configuration de la page
st.set_page_config(page_title="POC Vision Food", layout="wide")


# Fonction pour prédire le gaspillage alimentaire
def predict_waste(data):
    # Simuler un pourcentage de gaspillage entre 5% et 40% en fonction de certains critères
    # Cette logique sera remplacée par votre modèle ML
    base_waste = 20  # pourcentage de base

    # Facteurs d'influence (simulés)
    plat_factors = {
        "pizza": -10,  # populaire = moins de gaspillage
        "poisson": +8,
        "épinards": +15,
        "frites": -12,
        "pâtes": -8,
        "rôti": -5,
        "lentilles": +10
    }

    # Facteur météo (simulé)
    temp_factor = 0
    if data["Température"] > 25:
        temp_factor = 5  # il fait chaud, moins d'appétit
    elif data["Température"] < 5:
        temp_factor = -5  # il fait froid, plus d'appétit

    # Recherche de mots-clés dans les plats
    plat_factor = 0
    for key, value in plat_factors.items():
        if key in data["Plat"].lower() or key in data["Légumes"].lower():
            plat_factor += value

    # Calcul du gaspillage prédit (avec un peu d'aléatoire pour simulation)
    predicted_waste = base_waste + plat_factor + temp_factor
    predicted_waste += random.uniform(-5, 5)  # variation aléatoire

    # Borner entre 5% et 95%
    return max(5, min(95, predicted_waste))


# Fonction pour prédire le taux de participation
def predict_attendance(data):
    # Simuler un taux de participation entre 50% et 100%
    base_attendance = 85  # pourcentage de base
    
    # Facteurs d'influence (simulés)
    day_factors = {
        "Lundi": -5,
        "Mardi": 0,
        "Mercredi": +2,
        "Jeudi": 0,
        "Vendredi": -8,  # souvent plus d'absences le vendredi
    }
    
    # Facteur météo (simulé)
    weather_factor = 0
    if data["Météo"] == "Pluvieux":
        weather_factor = -3  # moins de présence par temps pluvieux
    elif data["Météo"] == "Neigeux":
        weather_factor = -10  # beaucoup moins de présence par temps neigeux
    
    # Facteur événement spécial
    event_factor = 0
    if "evenement_special" in data and data["evenement_special"]:
        if data["type_evenement"] == "Sortie scolaire partielle":
            event_factor = -15
        elif data["type_evenement"] == "Vacances imminentes":
            event_factor = -10
        elif data["type_evenement"] == "Examen":
            event_factor = +5  # plus de présence les jours d'examen
    
    # Calcul du taux de participation prédit
    day_factor = day_factors.get(data["Jour"], 0)
    predicted_attendance = base_attendance + day_factor + weather_factor + event_factor
    predicted_attendance += random.uniform(-3, 3)  # variation aléatoire
    
    # Borner entre 50% et 100%
    return max(50, min(100, predicted_attendance))


# Titre et description
st.title("POC Vision Food")
st.markdown("""
Cette application est une preuve de concept qui montre comment:
1. Importer des données historiques de repas scolaires
2. Analyser ces données pour comprendre les tendances
3. Prédire le taux de gaspillage pour un futur repas et le taux de participation attendu
""")

# Création des onglets
tab1, tab2, tab3 = st.tabs(["Importation & Analyse", "Prédiction", "Documentation"])

with tab1:
    st.header("Importation et analyse des données")

    # Champs qui permet d'envoyer un CSV
    upload_csv = st.file_uploader("Importer un fichier CSV de données historiques", type="csv")

    if upload_csv:
        try:
            df = pd.read_csv(upload_csv)
            st.success(f"✅ Fichier importé avec succès: {len(df)} entrées chargées")

            # Affichage des données
            st.subheader("Aperçu des données")
            st.dataframe(df.head())

            # Exploration statistique
            st.subheader("Exploration statistique")
            col1, col2 = st.columns(2)

            with col1:
                if st.checkbox("Afficher statistiques descriptives"):
                    st.write(df.describe())

            with col2:
                if st.checkbox("Afficher informations sur les données"):
                    buffer = df.info(buf=None)
                    st.text(str(df.dtypes))

            # Visualisation
            st.subheader("Visualisation des données")

            viz_col1, viz_col2 = st.columns(2)

            with viz_col1:
                num_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
                if num_columns:
                    y_column = st.selectbox("Choisir une colonne pour l'axe Y", num_columns, key="y_axis")

                    if "Date" in df.columns:
                        if st.button("Générer graphique temporel"):
                            fig = px.line(df, x="Date", y=y_column, title=f"Évolution de {y_column} dans le temps")
                            st.plotly_chart(fig, use_container_width=True)

            with viz_col2:
                column = st.selectbox("Choisir une colonne pour l'analyse", df.columns)
                chart_type = st.radio("Type de graphique", ["Barres", "Camembert", "Histogramme"])

                if st.button("Générer le graphique"):
                    if chart_type == "Barres":
                        value_counts = df[column].value_counts().reset_index()
                        fig = px.bar(value_counts, x='index', y=column, title=f"Distribution de {column}")
                        st.plotly_chart(fig, use_container_width=True)
                    elif chart_type == "Camembert":
                        value_counts = df[column].value_counts().reset_index()
                        fig = px.pie(value_counts, names='index', values=column, title=f"Répartition de {column}")
                        st.plotly_chart(fig, use_container_width=True)
                    else:  # Histogramme
                        fig = px.histogram(df, x=column, title=f"Histogramme de {column}")
                        st.plotly_chart(fig, use_container_width=True)

            # Entraînement du modèle (simulation)
            st.subheader("Entraînement du modèle")
            if st.button("Entraîner le modèle sur ces données"):
                with st.spinner("Entraînement du modèle en cours..."):
                    # Simuler un temps d'entraînement
                    import time

                    time.sleep(2)
                    st.success("✅ Modèle entraîné avec succès! R² simulé: 0.78")

                    # Afficher une matrice de corrélation simulée
                    st.subheader("Corrélations entre les variables")
                    if len(df.select_dtypes(include=['float64', 'int64']).columns) > 1:
                        corr_matrix = df.select_dtypes(include=['float64', 'int64']).corr()
                        fig = px.imshow(corr_matrix,
                                        text_auto=True,
                                        aspect="auto",
                                        color_continuous_scale='RdBu_r')
                        st.plotly_chart(fig, use_container_width=True)

            # Téléchargement des données
            st.download_button("Télécharger les données", df.to_csv(index=False), "data_edited.csv")

        except Exception as e:
            st.error(f"Erreur lors de l'importation du fichier: {e}")

with tab2:
    st.header("Prédiction du gaspillage alimentaire et du taux de participation")

    # Créer une disposition en colonnes
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Informations sur le repas")
        date = st.date_input("Date du repas", datetime.date.today())
        entree = st.text_input("Entrée", "Pamplemousse")
        plat = st.text_input("Plat principal", "Rôti de Poulet au jus")
        legumes = st.text_input("Accompagnement", "Lentilles")
        laitage = st.text_input("Laitage", "Crème au chocolat")
        gouter = st.text_input("Goûter", "Pain/confiture d'abricots/lait")

    with col2:
        st.subheader("Paramètres contextuels")
        allergies = st.slider("Taux d'allergies (%)", 0, 30, 2, format="%d%%") / 100
        taux_participation = st.slider("Taux d'absences prévues (%)", 0, 50, 10, format="%d%%") / 100

        st.subheader("Conditions météorologiques")
        temperature = st.slider("Température prévue (°C)", -10, 40, 15)
        humidite = st.slider("Humidité prévue (%)", 0, 100, 58)
        vent = st.slider("Vitesse du vent prévue (km/h)", 0, 100, 15)

        meteo = st.selectbox("Conditions météo", ["Ensoleillé", "Nuageux", "Pluvieux", "Neigeux"])

    # Paramètres supplémentaires
    st.subheader("Autres paramètres")
    col3, col4 = st.columns(2)

    with col3:
        attente = st.slider("Temps d'attente moyen prévu (min)", 0, 30, 5)
        jour_semaine = date.strftime("%A")  # Jour de la semaine

        if jour_semaine == "Monday":
            jour_semaine = "Lundi"
        elif jour_semaine == "Tuesday":
            jour_semaine = "Mardi"
        elif jour_semaine == "Wednesday":
            jour_semaine = "Mercredi"
        elif jour_semaine == "Thursday":
            jour_semaine = "Jeudi"
        elif jour_semaine == "Friday":
            jour_semaine = "Vendredi"
        elif jour_semaine == "Saturday":
            jour_semaine = "Samedi"
        else:
            jour_semaine = "Dimanche"

        st.info(f"Jour de la semaine: {jour_semaine}")

    with col4:
        evenement_special = st.checkbox("Événement spécial ce jour-là?")
        type_evenement = None
        if evenement_special:
            type_evenement = st.selectbox("Type d'événement",
                                          ["Journée thématique", "Sortie scolaire partielle",
                                           "Vacances imminentes", "Examen"])

    # Bouton de prédiction
    if st.button("Prédire le taux de gaspillage et la participation", key="predict_button"):
        with st.spinner("Calcul des prédictions en cours..."):
            # Simuler un délai de calcul
            import time

            time.sleep(1)

            # Créer un dictionnaire des données entrées
            data = {
                "Date": date,
                "Entrée": entree,
                "Plat": plat,
                "Légumes": legumes,
                "Laitage": laitage,
                "Goûter": gouter,
                "Allergies": allergies,
                "Taux participation": taux_participation,
                "Température": temperature,
                "Humidité": humidite,
                "Vitesse du vent": vent,
                "Attente moyenne": attente,
                "Jour": jour_semaine,
                "Météo": meteo,
                "evenement_special": evenement_special,
                "type_evenement": type_evenement
            }

            # Obtenir les prédictions
            waste_prediction = predict_waste(data)
            attendance_prediction = predict_attendance(data)

            # Afficher les résultats
            st.success(f"Prédictions calculées!")
            
            # Créer deux colonnes pour afficher les résultats
            res_col1, res_col2 = st.columns(2)
            
            with res_col1:
                st.subheader("Prédiction du gaspillage alimentaire")
                # Créer une jauge pour afficher le résultat du gaspillage
                fig1 = px.pie(values=[waste_prediction, 100 - waste_prediction],
                             names=["Gaspillage prévu", "Consommation prévue"],
                             hole=0.7,
                             color_discrete_sequence=["#EF553B", "#00CC96"])
                fig1.update_layout(annotations=[dict(text=f"{waste_prediction:.1f}%",
                                                    x=0.5, y=0.5, font_size=30, showarrow=False)])
                st.plotly_chart(fig1, use_container_width=True)

                # Déterminer le niveau de risque pour le gaspillage
                if waste_prediction < 15:
                    risk_color = "#00CC96"  # vert
                    risk_text = "Faible gaspillage prévu"
                    st.success(f"✅ {risk_text} : Ce repas devrait être bien accepté par les élèves.")
                elif waste_prediction < 30:
                    risk_color = "#FFA15A"  # orange
                    risk_text = "Gaspillage modéré prévu"
                    st.warning(f"⚠️ {risk_text} : Certains élèves risquent de ne pas finir leur repas.")
                else:
                    risk_color = "#EF553B"  # rouge
                    risk_text = "Gaspillage élevé prévu"
                    st.error(f"❌ {risk_text} : Ce menu risque de générer beaucoup de déchets.")
            
            with res_col2:
                st.subheader("Prédiction du taux de participation")
                # Créer une jauge pour afficher le résultat de la participation
                fig2 = px.pie(values=[attendance_prediction, 100 - attendance_prediction],
                             names=["Présence prévue", "Absence prévue"],
                             hole=0.7,
                             color_discrete_sequence=["#636EFA", "#FECB52"])
                fig2.update_layout(annotations=[dict(text=f"{attendance_prediction:.1f}%",
                                                    x=0.5, y=0.5, font_size=30, showarrow=False)])
                st.plotly_chart(fig2, use_container_width=True)
                
                # Déterminer le niveau pour la participation
                if attendance_prediction > 85:
                    st.success(f"✅ Participation élevée prévue : {attendance_prediction:.1f}% des élèves devraient être présents.")
                elif attendance_prediction > 70:
                    st.info(f"ℹ️ Participation moyenne prévue : {attendance_prediction:.1f}% des élèves devraient être présents.")
                else:
                    st.warning(f"⚠️ Participation faible prévue : Seulement {attendance_prediction:.1f}% des élèves devraient être présents.")

            # Recommandations
            st.subheader("Recommandations")
            recommendations = []

            if "lentilles" in legumes.lower():
                recommendations.append(
                    "Considérez remplacer les lentilles par des pâtes ou du riz qui sont généralement mieux acceptés.")

            if temperature > 25 and "soupe" in entree.lower():
                recommendations.append(
                    "Par temps chaud, la soupe est souvent moins appréciée. Envisagez une entrée froide.")

            if temperature < 5 and "salade" in entree.lower():
                recommendations.append("Par temps froid, les entrées chaudes sont généralement préférées aux salades.")

            if waste_prediction > 30:
                recommendations.append("Envisagez de modifier ce menu ou d'ajuster les portions à la baisse.")

            if meteo == "Pluvieux" and attente > 10:
                recommendations.append(
                    "Réduisez le temps d'attente les jours de pluie pour éviter que les élèves ne s'impatientent.")
                    
            if attendance_prediction < 70:
                recommendations.append(
                    f"Prévoyez moins de repas ce jour-là ({attendance_prediction:.1f}% de présence prévue).")
                    
            if jour_semaine == "Vendredi" and attendance_prediction < 80:
                recommendations.append(
                    "Les vendredis ont généralement un taux de présence plus faible. Ajustez les quantités en conséquence.")

            if not recommendations:
                recommendations.append("Ce menu semble bien adapté aux conditions prévues.")

            for rec in recommendations:
                st.markdown(f"- {rec}")

with tab3:
    st.header("Documentation")

    st.subheader("À propos de Vision Food")
    st.markdown("""
    Vision Food est une application qui utilise l'intelligence artificielle pour prédire le taux de gaspillage alimentaire dans les cantines scolaires.

    ### Comment ça marche?

    1. **Importation des données** : L'application utilise des données historiques sur les repas servis, les conditions météorologiques et le taux de participation pour entraîner un modèle prédictif.

    2. **Analyse** : Le système analyse les corrélations entre les différents facteurs (type de plat, météo, jour de la semaine, etc.) et le taux de gaspillage observé.

    3. **Prédiction** : En se basant sur les différentes données notre modèle va donner son estimation de ce que vous pouvez gachez pour un repas servi""")