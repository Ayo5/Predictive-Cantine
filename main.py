import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import streamlit as st

# Charger les données
data_meteo = pd.read_csv("data-meteo.csv")
data_meteo["Date"] = pd.to_datetime(data_meteo["Date"])
data_meteo["Year"] = data_meteo["Date"].dt.year
data_meteo["Month"] = data_meteo["Date"].dt.month
data_meteo["Day"] = data_meteo["Date"].dt.day
data_meteo["Taux gaspillage"] = pd.to_numeric(data_meteo["Taux gaspillage"], errors="coerce")
data_meteo = data_meteo.dropna()

# One-hot encode the categorical columns
columns_to_encode = ["Entrée", "Dessert", "Laitage", "Légumes", "Plat", "Secteur", "Allergies", "Gouter", "Gouter_02"]
existing_columns = [col for col in columns_to_encode if col in data_meteo.columns]
data_meteo = pd.get_dummies(data_meteo, columns=existing_columns)

# Définir la variable cible et les caractéristiques
y = data_meteo["Taux gaspillage"]
X = data_meteo.drop(columns=["Taux gaspillage", "Date", "Commentaire semaine", "Commentaire jour",
                             "Code_gouter", "Code_gouter_02", "Gouter_02", "Code_entrée", "Code_plat",
                             "Code_légumes", "Code_laitage", "Code_dessert"])

# Diviser les données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Créer et entraîner le modèle
model = LinearRegression()
model.fit(X_train, y_train)

# Interface utilisateur Streamlit
st.title("Prédiction du Taux de Gaspillage")

# Saisie des nouvelles observations
year = st.number_input("Année", min_value=2000, max_value=2100, value=2023)
month = st.number_input("Mois", min_value=1, max_value=12, value=1)
day = st.number_input("Jour", min_value=1, max_value=31, value=1)
entree = st.text_input("Entrée", "Pamplemousse")
plat = st.text_input("Plat", "Rôti de porc au jus")
legumes = st.text_input("Légumes", "Lentilles")
laitage = st.text_input("Laitage", "Crème au chocolat")
gouter = st.text_input("Goûter", "Pain/ confiture d'abricots/ lait")
allergies = st.number_input("Allergies", min_value=0.0, max_value=1.0, value=0.02)
taux_participation = st.number_input("Taux de participation", min_value=0.0, max_value=1.0, value=0.01)
temperature = st.number_input("Température", value=10.7)
humidite = st.number_input("Humidité", value=58)
vent = st.number_input("Vitesse du vent moyen 10 mn", value=4.5)
attente = st.number_input("Attente moyenne", value=0)

# Créer un DataFrame pour la nouvelle observation
nouvelle_observation = {
    "Year": year,
    "Month": month,
    "Day": day,
    "Entrée": entree,
    "Plat": plat,
    "Légumes": legumes,
    "Laitage": laitage,
    "Gouter": gouter,
    "Allergies": allergies,
    "Taux participation": taux_participation,
    "Température": temperature,
    "Humidité": humidite,
    "Vitesse du vent moyen 10 mn": vent,
    "Attente moyenne": attente,
    # Ajouter ici toutes les valeurs des variables catégorielles (avec one-hot encoding)
}

nouveau_df = pd.DataFrame([nouvelle_observation])
nouveau_df = nouveau_df.reindex(columns=X_train.columns, fill_value=0)

# Prédiction
if st.button("Prédire"):
    prediction = model.predict(nouveau_df)
    st.write(f"Prédiction du taux de gaspillage : {prediction[0]:.2f}%")