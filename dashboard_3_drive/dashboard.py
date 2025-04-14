import re
import pandas as pd
import numpy as np
import streamlit as st
import datarobot as dr
import altair as alt
import requests
import warnings

from datetime import datetime, timedelta

warnings.filterwarnings("ignore", category=DeprecationWarning)

# TODO : Remplacer les valeurs suivantes
API_TOKEN = "NjdmZDQwYzJkODMzODZiY2Y0MTk5NjI1Ok1tbVZrSUtyeDdINGFiNVo3amZKMEJaMzJhVXI2aGNmK0lrek9mRlJ0a0E9"
PROJECT_ID_PARTICIPATION ="67fd3bea98b547d51db6629e"
MODEL_ID_PARTICIPATION = "67fd3c9c28612c6236b2a9bb"

API_TOKEN_GASP = "NjdmZDQxYjRmMzIzNmJiMGZjMTk5NTVmOiswNzVTNFZGZzFJMTBGVWc0dTFFVWZ1aWtHMHZ4YUtNU2RSSTVZWWxaaDg9"
PROJECT_ID_GASPILLAGE ="67fd2e75a0da87f6f4503261"
MODEL_ID_GASPILLAGE = "67fd35bb84cb9ee67965e9eb"
ENDPOINT = "https://app.datarobot.com/api/v2"

NUM_WEEKS = 16  # Sur combien de semaines on réalise les prédictions
delay_main_dish = 7  # Par défaut, un plat ne peut pas réapparaître en moins de 7 jours
delay_menu = 30  # Par défaut, un menu entier (entrée, plat, dessert) ne peut pas réapparaître en moins de 30 jours

WEEKDAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

# Initialize DataRobot client with error handling
try:
    dr.Client(endpoint=ENDPOINT, token=API_TOKEN)
except Exception as e:
    st.error(f"Error initializing DataRobot client: {e}")

# Set page configuration with a more professional look
st.set_page_config(
    layout="wide", 
    page_title="Predictive Cantine",
    page_icon="🍽️"
)

# Add custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .section-header {
        color: #0D47A1;
        font-size: 1.5rem;
        padding-top: 1rem;
    }
    .menu-day {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .menu-item {
        margin-bottom: 5px;
    }
    .bio-tag {
        color: green;
        font-weight: bold;
    }
    .divider {
        margin-top: 10px;
        margin-bottom: 10px;
        border-bottom: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Main title with better styling
st.markdown("<h1 class='main-header'>🍽️ Predictive Cantine</h1>", unsafe_allow_html=True)

st.write("# Predictive Cantine")

if "Repas semaine" not in st.session_state:
	with st.spinner('Calcul en cours...'):
		dataset = pd.read_csv("./data/data-meteo.csv")
		
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
		
		try:
			# Prédiction des gaspillages
			# Fix the client initialization - don't nest Client calls
			dr.Client(endpoint=ENDPOINT, token=API_TOKEN_GASP)
			results = []
			project = dr.Project.get(PROJECT_ID_GASPILLAGE)
			model = dr.Model.get(PROJECT_ID_GASPILLAGE, MODEL_ID_GASPILLAGE)
			
			pred_data = final_dataset.copy()
			pred_dataset = project.upload_dataset(pred_data)
			pred_job = model.request_predictions(pred_dataset.id)
			predictions = pred_job.get_result_when_complete(max_wait=3600)
			
			for row in predictions.iterrows():
				results.append(row[1]["prediction"])
			final_dataset.loc[:, "Taux de gaspillage"] = results
			
			# Reset client for participation prediction
			dr.Client(endpoint=ENDPOINT, token=API_TOKEN)
			# Prédiction des participations
			results = []
			project = dr.Project.get(PROJECT_ID_PARTICIPATION)
			model = dr.Model.get(PROJECT_ID_PARTICIPATION, MODEL_ID_PARTICIPATION)
			
			# Create a separate copy for participation prediction
			pred_data = final_dataset.copy()
			if "Taux de gaspillage" in pred_data.columns:
				pred_data = pred_data.drop("Taux de gaspillage", axis=1)
				
			pred_dataset = project.upload_dataset(pred_data)
			pred_job = model.request_predictions(pred_dataset.id)
			predictions = pred_job.get_result_when_complete(max_wait=3600)
			
			for row in predictions.iterrows():
				results.append(row[1]["prediction"])
			
			final_dataset.loc[:, "Taux de participation"] = results
		except Exception as e:
			st.error(f"Error during prediction: {str(e)}")
			# Fallback to random values if prediction fails
			final_dataset.loc[:, "Taux de gaspillage"] = np.random.uniform(0.05, 0.35, size=len(final_dataset))
			final_dataset.loc[:, "Taux de participation"] = np.random.uniform(0.65, 0.95, size=len(final_dataset))
		
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

co2_couts = pd.read_csv("data/co2_couts.csv")
co2_couts["Nom"] = co2_couts["Nom"].str.lower()
co2_couts["Nom"] = co2_couts["Nom"].str.replace(r"(^\s+|\s+$)", "")  # On supprime les espaces au début et à la fin
co2_couts["Nom"] = co2_couts["Nom"].str.replace(r"s$", "")  # On supprime le pluriel
menus = calcul_menus()

if "skips" not in st.session_state:
	st.session_state["skips"] = {}
	
def get_current_menu(week_number):
	week_menus = []
	price = 0 # Coût total de la semaine pour un enfant
	co2 = 0 # Empreinte carbonne
	
	for i in range(5):
		i_week = i + week_number * 5
		current_date = datetime(2023, 1, 2) + timedelta(days=i_week + (2 * np.floor(i_week / 5)))
		str_date = current_date.strftime("%d-%m-%Y")
		
		try:
			row = menus[str_date][0]
			if str_date in st.session_state["skips"]:
				row = menus[str_date][st.session_state["skips"][str_date]]
				
			# Si le plat a déjà été proposé au cours des x derniers jours, on en choisit un autre
			def dish_found():
				found = False
				previous_dates = sorted([
					datetime.strptime(x, "%d-%m-%Y")
					for x in menus.keys()
					if datetime.strptime(x, "%d-%m-%Y") < current_date
				])[-delay_main_dish:]
				previous_menus = [
					menus[d.strftime("%d-%m-%Y")][st.session_state["skips"].get(d.strftime("%d-%m-%Y"), 0)] for d in previous_dates
				]
				
				for prev_menu in previous_menus:
					if str(row["Plat"]).lower() in str(prev_menu["Plat"]).lower():
						found = True
						break
				return found
				
			def menu_found():
				found = False
				previous_dates = sorted([
					datetime.strptime(x, "%d-%m-%Y")
					for x in menus.keys()
					if datetime.strptime(x, "%d-%m-%Y") < current_date
				])[-delay_menu:]
				previous_menus = [
					menus[d.strftime("%d-%m-%Y")][st.session_state["skips"].get(d.strftime("%d-%m-%Y"), 0)] for d in previous_dates
				]
				
				for prev_menu in previous_menus:
					if str(row["Entrée"]).lower() in str(prev_menu["Entrée"]).lower() and \
						str(row["Plat"]).lower() in str(prev_menu["Plat"]).lower() and \
						str(row["Dessert"]).lower() in str(prev_menu["Dessert"]).lower():
						found = True
						break
				return found
				
			while dish_found() or menu_found():
				st.session_state["skips"][str_date] = st.session_state["skips"].get(str_date, 0) + 1
				row = menus[str_date][st.session_state["skips"][str_date]]
				
			week_menus.append(row)
			
			# Maintenant, on calcule le coût du menu
			# On supposera un grammage de 100g pour chaque plat
			for dish in ["Entrée", "Plat", "Légumes", "Dessert", "Laitage"]:
				if pd.isna(row[dish]):
					continue
					
				composants = [re.sub(r"(^\s+|\s+$)", "", re.sub(r"\s$", "", x.lower())) for x in str(row[dish]).split()]
				for comp in composants:
					# Calculer les informations de coût et de CO2 pour chaque entité
					for index, food_item in co2_couts.iterrows():
						try:
							if comp in food_item["Nom"] or food_item["Nom"] in comp:
								price += float(food_item["Prix"]) * 0.1  # 100g = 0.1kg
								co2 += float(food_item["CO2"]) * 0.1  # 100g = 0.1kg
								break
						except (KeyError, ValueError, TypeError):
							# Skip this item if there's an error
							continue
		except Exception as e:
			st.warning(f"Error processing menu for {str_date}: {e}")
			# Create a default menu item if there's an error
			row = {
				"Date": current_date,
				"Entrée": "Menu par défaut",
				"Plat": "Plat par défaut",
				"Légumes": "Légumes par défaut",
				"Dessert": "Dessert par défaut",
				"Laitage": "Laitage par défaut",
				"Taux de participation": 0.8,
				"Taux de gaspillage": 0.2,
				"Taux gaspillage": 0.3,  # Default initial gaspillage
				"Code_entrée": "",
				"Code_plat": "",
				"Code_légumes": "",
				"Code_dessert": "",
				"Code_laitage": ""
			}
			week_menus.append(row)
	
	return week_menus, price, co2


with col1:
    st.markdown("<h2 class='section-header'>Menu de la semaine</h2>", unsafe_allow_html=True)
    week_menus, prix_semaine, _ = get_current_menu(current_week)
    for i, row in enumerate(week_menus):        
        # Create a container for each day's menu
        with st.container():
            st.markdown(f"<div class='menu-day'>", unsafe_allow_html=True)
            
            # Day header with date
            st.markdown(f"<h3>{WEEKDAYS[row['Date'].weekday()]} ({row['Date'].strftime('%d-%m-%Y')})</h3>", unsafe_allow_html=True)
            
            # Button to change menu
            btn = st.button("Changer de menu", key=f"redo_{row['Date']}")
            if btn:
                str_date = row["Date"].strftime("%d-%m-%Y")
                st.session_state["skips"][str_date] = st.session_state["skips"].get(str_date, 0) + 1
                week_menus, prix_semaine, _ = get_current_menu(current_week)
                row = week_menus[i]
            
            # Menu items in columns
            day_cols = st.columns(3)
            
            # Entrée
            with day_cols[0]:
                st.markdown("<b>Entrée</b>", unsafe_allow_html=True)
                st.markdown(f"<div class='menu-item'>{row['Entrée']}</div>", unsafe_allow_html=True)
                if "AB" in str(row["Code_entrée"]):
                    st.success("Bio")
            
            # Plat
            with day_cols[1]:
                st.markdown("<b>Plat</b>", unsafe_allow_html=True)
                plat_text = " + ".join([x for x in [row["Plat"], row["Légumes"]] if str(x) != "nan"])
                st.markdown(f"<div class='menu-item'>{plat_text}</div>", unsafe_allow_html=True)
                if "AB" in str(row["Code_plat"]) or "AB" in str(row["Code_légumes"]):
                    st.success("Bio")
            
            # Dessert
            with day_cols[2]:
                st.markdown("<b>Dessert</b>", unsafe_allow_html=True)
                dessert_text = " + ".join([x for x in [row["Dessert"], row["Laitage"]] if str(x) != "nan"])
                st.markdown(f"<div class='menu-item'>{dessert_text}</div>", unsafe_allow_html=True)
                if "AB" in str(row["Code_dessert"]) or "AB" in str(row["Code_laitage"]):
                    st.success("Bio")
            
            st.markdown("</div>", unsafe_allow_html=True)

with col2:
	participations = []
	week_menus, prix_semaine, _ = get_current_menu(current_week)
	for row in week_menus:
		participations.append(row["Taux de participation"] * 100)
		
	col2.write("### Budget")
	cols2_2 = col2.columns(2)
	num_students = cols2_2[0].number_input("Nombre d'élèves inscrits à la cantine :", min_value=0, max_value=5000, value=150)
	show_percent = cols2_2[1].checkbox("Afficher en pourcentages", value=False)
	
	cols2_1_metrics = col2.columns(3)
	# Afficher les métriques de budget
	cout_semaine = prix_semaine * num_students
	cout_standard = 4.5 * 5 * num_students  # 4.5€ par repas standard, 5 jours
	economies = cout_standard - cout_semaine if cout_standard > cout_semaine else 0
	
	cols2_1_metrics[0].metric(
		"Coût par enfant",
		f"{prix_semaine:.2f}€",
		f"{(prix_semaine/5):.2f}€/jour"
	)
	cols2_1_metrics[1].metric(
		"Coût total semaine",
		f"{cout_semaine:.2f}€",
		f"{num_students} enfants"
	)
	cols2_1_metrics[2].metric(
		"Économies réalisées",
		f"{economies:.2f}€",
		f"{(economies/cout_standard*100):.1f}%" if cout_standard > 0 else "0%",
		delta_color="normal" if economies > 0 else "off"
	)
		
	col2.write("### Affluence")
	col2.bar_chart(
		data=pd.DataFrame(
			np.array([[round(x * 10) / 10 if show_percent else round(x / 100 * num_students)] for x in participations]),
			index=[f"{i+1} - {w}" for i, w in enumerate(WEEKDAYS)],
			columns=["Taux de participation" if show_percent else "Nombre de participants"]
		),
		y="Taux de participation" if show_percent else "Nombre de participants"
	)
	
with col3:
	week_menus, prix_semaine, co2 = get_current_menu(current_week)
	gaspillage_initial = []
	gaspillage_prevu = []
	for row in week_menus:
		gaspillage_initial.append(row["Taux gaspillage"] * 100)
		gaspillage_prevu.append(row["Taux de gaspillage"] * 100)
		
	col3.write("### Gaspillage et CO2")
	cols3_1_metrics = col3.columns(3)
	# Afficher les métriques de gaspillage
	gaspillage_moyen_initial = sum(gaspillage_initial) / len(gaspillage_initial)
	gaspillage_moyen_prevu = sum(gaspillage_prevu) / len(gaspillage_prevu)
	reduction_gaspillage = gaspillage_moyen_initial - gaspillage_moyen_prevu
	
	cols3_1_metrics[0].metric(
		"Gaspillage initial",
		f"{gaspillage_moyen_initial:.1f}%",
		delta=None
	)
	
	cols3_1_metrics[1].metric(
		"Gaspillage prévu",
		f"{gaspillage_moyen_prevu:.1f}%",
		f"-{reduction_gaspillage:.1f}%" if reduction_gaspillage > 0 else f"+{-reduction_gaspillage:.1f}%",
		delta_color="inverse"  # Green when negative (less waste)
	)
	
	cols3_1_metrics[2].metric(
		"Empreinte CO2",
		f"{co2:.1f} kg",
		f"{co2/5:.2f} kg/jour"
	)
	
	# Afficher le graphique comparatif de gaspillage
	# Restructure the data for Altair
	gaspillage_long = pd.DataFrame({
		"Jour": [f"{i+1} - {w}" for i, w in enumerate(WEEKDAYS)] * 2,
		"Type": ["Gaspillage initial"] * 5 + ["Gaspillage prévu"] * 5,
		"Pourcentage": gaspillage_initial + gaspillage_prevu
	})
	
	# Create chart with pre-melted data
	gaspillage_chart = alt.Chart(gaspillage_long).mark_bar().encode(
		x=alt.X('Jour:N', title='Jour de la semaine'),
		y=alt.Y('Pourcentage:Q', title='Gaspillage (%)'),
		color=alt.Color('Type:N', scale=alt.Scale(
			domain=['Gaspillage initial', 'Gaspillage prévu'],
			range=['#ff9999', '#66b3ff']
		)),
		column='Type:N',
		tooltip=['Jour', 'Type', 'Pourcentage']
	).properties(
		title='Comparaison du gaspillage initial et prévu'
	)
	
	col3.altair_chart(gaspillage_chart, use_container_width=True)
	
	col3.write("### Produits Bio de la semaine")
	have_bio = False
	for row in week_menus:
		cols_codes = ["Code_entrée", "Code_plat", "Code_légumes", "Code_laitage", "Code_dessert"]
		cols_dish = ["Entrée", "Plat", "Légumes", "Laitage", "Dessert"]
		for code, dish in zip(cols_codes, cols_dish):
			if "AB" in str(row[code]):
				col3.write(row[dish])
				have_bio = True
	if not have_bio:
		col3.error("Pas de bio cette semaine !")
	
	col3.write("### Paramètres")
	delay_main_dish = col3.slider("Délai d'apparition entre deux plats identiques (en jours)", min_value=1, max_value=30, value=7, step=1)
	delay_menu = col3.slider("Délai d'apparition entre deux menus identiques (en jours)", min_value=1, max_value=90, value=30, step=1)
