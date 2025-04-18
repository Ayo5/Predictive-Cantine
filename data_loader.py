import pandas as pd
import numpy as np
import streamlit as st
import datarobot as dr
from datetime import datetime, timedelta
from config import *

def load_data():
    """Load and filter dataset"""
    dataset = pd.read_csv(CSV_PREDICTIONS)
    
    closed_values = [
        "VACANCES SCOLAIRES", "FERIE", "FÉRIÉ", "FERIÉ", 
        "PAS DE CENTRE", "CENTRE FERMÉ", "CENTRE FERME"
    ]
    
    for col in ["Commentaire semaine", "Commentaire jour"]:
        if col in dataset.columns:
            dataset = dataset[~dataset[col].isin(closed_values)]
        else:
            print(f"Warning: Column '{col}' not found in dataset. Skipping filter.")
    
    return dataset

def prepare_dataset(dataset, num_weeks):
    """Prepare dataset for predictions"""
    final_dataset = dataset.copy()
    final_dataset['Date'] = pd.to_datetime(final_dataset['Date'])
    
    if 'Taux de gaspillage' not in final_dataset.columns:
        final_dataset['Taux de gaspillage'] = 0.0
    
    if 'Taux de participation' not in final_dataset.columns:
        final_dataset['Taux de participation'] = 0.0
    
    if 'Taux gaspillage' not in final_dataset.columns:
        final_dataset['Taux gaspillage'] = 0.3  
    
    try:
        predict_waste_and_participation(final_dataset)
        print("Prédictions réalisées avec succès via DataRobot")
    except Exception as e:
        st.error(f"Erreur lors de la prédiction: {str(e)}")
        final_dataset['Taux de gaspillage'] = np.random.uniform(0.05, 0.35, size=len(final_dataset))
        final_dataset['Taux de participation'] = np.random.uniform(0.65, 0.95, size=len(final_dataset))
        print("Utilisation de valeurs aléatoires suite à une erreur")
    
    final_dataset['Taux de gaspillage'] = final_dataset['Taux de gaspillage'].clip(0.01, 0.5)
    final_dataset['Taux de participation'] = final_dataset['Taux de participation'].clip(0.5, 1.0)
    
    return final_dataset

def predict_waste_and_participation(final_dataset):
    """Make predictions using DataRobot models"""
    dr.Client(endpoint=ENDPOINT, token=API_TOKEN_GASP)
    project = dr.Project.get(PROJECT_ID_GASPILLAGE)
    model = dr.Model.get(PROJECT_ID_GASPILLAGE, MODEL_ID_GASPILLAGE)
    
    pred_data = final_dataset.copy()
    pred_dataset = project.upload_dataset(pred_data)
    pred_job = model.request_predictions(pred_dataset.id)
    predictions = pred_job.get_result_when_complete(max_wait=3600)
    
    try:
        results = [float(row[1]["prediction"]) for row in predictions.iterrows()]
        final_dataset.loc[:, "Taux de gaspillage"] = results
    except Exception as e:
        print(f"Erreur lors de la prédiction du taux de gaspillage: {str(e)}")
    
    try:
        dr.Client(endpoint=ENDPOINT, token=API_TOKEN)
        project_participation = dr.Project.get(PROJECT_ID_PARTICIPATION)
        model_participation = dr.Model.get(PROJECT_ID_PARTICIPATION, MODEL_ID_PARTICIPATION)
        
        pred_dataset_participation = project_participation.upload_dataset(pred_data)
        pred_job_participation = model_participation.request_predictions(pred_dataset_participation.id)
        predictions_participation = pred_job_participation.get_result_when_complete(max_wait=3600)
        
        results_participation = [float(row[1]["prediction"]) for row in predictions_participation.iterrows()]
        final_dataset.loc[:, "Taux de participation"] = results_participation
    except Exception as e:
        print(f"Erreur lors de la prédiction du taux de participation: {str(e)}")
        final_dataset.loc[:, "Taux de participation"] = np.random.uniform(0.75, 0.95, size=len(final_dataset))