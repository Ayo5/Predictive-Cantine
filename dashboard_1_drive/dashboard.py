import pandas as pd
import numpy as np
import streamlit as st
import datarobot as dr
from datarobot import AUTOPILOT_MODE
#import altair as alt
import requests
import warnings

from datetime import date, datetime, timedelta

warnings.filterwarnings("ignore", category=DeprecationWarning)

# TODO : Remplacer les valeurs suivantes
API_TOKEN = 'NjdmMGYxNzMyNDY3ZGYzODRjOTliODdkOmpYZ1oyQ0xIRk9rR1l4QXR0cWRQQXhELzArRkNkd25lbXVRS2Z5Sy9ZWVU9'
# PROJECT_ID_PARTICIPATION ='***'
# MODEL_ID_PARTICIPATION = '***'
# PROJECT_ID_GASPILLAGE ='***'
# MODEL_ID_GASPILLAGE = '***'

NUM_WEEKS = 16  # Sur combien de semaines on réalise les prédictions
delay_main_dish = 7  # Par défaut, un plat ne peut pas réapparaître en moins de 7 jours
delay_menu = 30  # Par défaut, un menu entier (entrée, plat, dessert) ne peut pas réapparaître en moins de 30 jours

WEEKDAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

dr.Client(endpoint='https://app.eu.datarobot.com/api/v2', token=API_TOKEN)

st.set_page_config(layout="wide", page_title="Predictive Cantine")

st.write("# Predictive Cantine")

if "Repas semaine" not in st.session_state:
	with st.spinner('Calcul en cours...'):
		dataset = pd.read_csv("data/data-meteo.csv")
		
		# Il faut prédire pour des plats qui ont été servis que lorsque la cantine est ouverte
		dataset = dataset[
			(dataset["Commentaire semaine"] != "VACANCES SCOLAIRES") &
			(dataset["Commentaire semaine"] != "FERIE") &
			(dataset["Commentaire semaine"] != "FÉRIÉ") &
			(dataset["Commentaire semaine"] != "FERIÉ") &
			(dataset["Commentaire semaine"] != "PAS DE CENTRE") &
			(dataset["Commentaire semaine"] != "CENTRE FERMÉ") &
			(dataset["Commentaire semaine"] != "CENTRE FERME") &
			(dataset["Commentaire jour"] != "VACANCES SCOLAIRES") &
			(dataset["Commentaire jour"] != "FERIE") &
			(dataset["Commentaire jour"] != "FÉRIÉ") &
			(dataset["Commentaire jour"] != "FERIÉ") &
			(dataset["Commentaire jour"] != "PAS DE CENTRE") &
			(dataset["Commentaire jour"] != "CENTRE FERMÉ") &
			(dataset["Commentaire jour"] != "CENTRE FERME")
		]
		
		final_dataset = None
		for i in range(NUM_WEEKS * 5):
			partial_dataset = dataset.copy()
			# On ajoute à chaque fois une journée en retirant les samedi et dimanche
			partial_dataset.loc[:, "Date"] = datetime(2023, 1, 2) + timedelta(days=i + (2 * np.floor(i / 5)))
			if final_dataset is None:
				final_dataset = partial_dataset.sample(n=500)
			else:
				final_dataset = pd.concat((final_dataset, partial_dataset.sample(n=500)))
				
		# Initialisation à 0 des deux colonnes de prédiction
		final_dataset.loc[:, "Taux de gaspillage"] = 0
		final_dataset.loc[:, "Taux de participation"] = 0

		# Prédiction des gaspillages
		# TODO : En utilisant l'API DataRobot, effectuer les prédictions de gaspillage et de participation
		# https://datarobot-public-api-client.readthedocs-hosted.com/en/early-access/reference/predictions/batch_predictions.html
		results = []
		# TODO : à compléter
		final_dataset.loc[:, "Taux de gaspillage"] = results
		
		# Prédiction des participations
		results = []
		# TODO : à compléter
		final_dataset.loc[:, "Taux de participation"] = results
		st.session_state["Repas semaine"] = final_dataset

# ######## Début du Dashboarding
	
current_week = int(st.selectbox(
	"Choix de la semaine",
	[f"Semaine {i+1}" for i in range(NUM_WEEKS)],
	index=0
).split(" ")[-1]) - 1
		
# On a toutes les prédictions dans st.session_state["Repas semaine"], maintenant il faut construire les menus de chaque semaine
# en prenant en compte les règles métiers
sorted_results = st.session_state["Repas semaine"].sort_values("Taux de gaspillage", ascending=True)

def calcul_menus():
	# Cette fonction va calculer tous les menus des prochaines semaines en appliquant les règles métiers
	menus = {}
	for week in range(NUM_WEEKS):
		for i in range(5):
			delta_i = i + week * 5
			current_date = datetime(2023, 1, 2) + timedelta(days=delta_i + (2 * np.floor(delta_i / 5)))
			str_date = current_date.strftime("%d-%m-%Y")
			menus[str_date] = sorted_results[sorted_results["Date"] == current_date].iloc[:50, :].to_dict("records")
	return menus

col1, col2, col3 = st.columns(3)

menus = calcul_menus()

if "skips" not in st.session_state:
	st.session_state["skips"] = {}

with col1:
	st.write("### Menu de la semaine")
	
with col2:
	col2.write("### Affluence")
	cols2_2 = col2.columns(2)
	num_students = cols2_2[0].number_input("Nombre d'élèves inscrits à la cantine :", min_value=0, max_value=1500, value=150)
	show_percent = cols2_2[1].checkbox("Afficher en pourcentages", value=False)
	
	participations = []
	for i in range(5):
		current_date = datetime(2023, 1, 2) + timedelta(days=i + (2 * np.floor(i / 5)))  # Cela évite de tomber sur des week-ends
		week_menu = sorted_results[sorted_results["Date"] == current_date].iloc[1, :]
		participations.append(week_menu["Taux de participation"] * 100)
	
	# TODO
	# Dessiner un bar_chart pour afficher le taux de participation chaque jour de la semaine
	
with col3:
	col3.write("### Gaspillage")
	
	col3.write("### Produits Bio de la semaine")
	
	col3.write("### Paramètres")
	
