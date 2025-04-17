import pandas as pd
import numpy as np
import streamlit as st
import datarobot as dr
from datetime import datetime, timedelta
from config import *

def load_data():
    """Load and filter dataset"""
    dataset = pd.read_csv("./data/data-meteo.csv")
    
    # Filter out closed days
    closed_values = [
        "VACANCES SCOLAIRES", "FERIE", "FÉRIÉ", "FERIÉ", 
        "PAS DE CENTRE", "CENTRE FERMÉ", "CENTRE FERME"
    ]
    
    for col in ["Commentaire semaine", "Commentaire jour"]:
        dataset = dataset[~dataset[col].isin(closed_values)]
    
    return dataset

def prepare_dataset(dataset, num_weeks):
    """Prepare dataset for predictions"""
    final_dataset = None
    
    # Create dataset for each day
    for i in range(num_weeks * 5):
        partial_dataset = dataset.copy()
        # Add a day, skipping weekends
        current_date = datetime(2023, 1, 2) + timedelta(days=i + (2 * np.floor(i / 5)))
        partial_dataset.loc[:, "Date"] = current_date
        
        if final_dataset is None:
            final_dataset = partial_dataset.sample(n=500)
        else:
            final_dataset = pd.concat((final_dataset, partial_dataset.sample(n=500)))
    
    # Initialize prediction columns
    final_dataset.loc[:, "Taux de gaspillage"] = 0
    final_dataset.loc[:, "Taux de participation"] = 0
    final_dataset.loc[:, "Taux gaspillage"] = 0.3  # Initial waste rate
    
    # Make predictions
    try:
        predict_waste_and_participation(final_dataset)
    except Exception as e:
        st.error(f"Error during prediction: {str(e)}")
        # Fallback to random values
        final_dataset.loc[:, "Taux de gaspillage"] = np.random.uniform(0.05, 0.35, size=len(final_dataset))
        final_dataset.loc[:, "Taux de participation"] = np.random.uniform(0.65, 0.95, size=len(final_dataset))
    
    return final_dataset

def predict_waste_and_participation(final_dataset):
    """Make predictions using DataRobot models"""
    # Predict waste
    dr.Client(endpoint=ENDPOINT, token=API_TOKEN_GASP)
    project = dr.Project.get(PROJECT_ID_GASPILLAGE)
    model = dr.Model.get(PROJECT_ID_GASPILLAGE, MODEL_ID_GASPILLAGE)
    
    pred_data = final_dataset.copy()
    pred_dataset = project.upload_dataset(pred_data)
    pred_job = model.request_predictions(pred_dataset.id)
    predictions = pred_job.get_result_when_complete(max_wait=3600)
    
    results = [row[1]["prediction"] for row in predictions.iterrows()]
    final_dataset.loc[:, "Taux de gaspillage"] = results
    
    # Predict participation
    dr.Client(endpoint=ENDPOINT, token=API_TOKEN)
    project = dr.Project.get(PROJECT_ID_PARTICIPATION)
    model = dr.Model.get(PROJECT_ID_PARTICIPATION, MODEL_ID_PARTICIPATION)
    
    pred_data = final_dataset.copy()
    if "Taux de gaspillage" in pred_data.columns:
        pred_data = pred_data.drop("Taux de gaspillage", axis=1)
    
    pred_dataset = project.upload_dataset(pred_data)
    pred_job = model.request_predictions(pred_dataset.id)
    predictions = pred_job.get_result_when_complete(max_wait=3600)
    
    results = [row[1]["prediction"] for row in predictions.iterrows()]
    final_dataset.loc[:, "Taux de participation"] = results