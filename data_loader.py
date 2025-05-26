import streamlit as st
import pandas as pd
import numpy as np
import datarobot as dr
import os
from config import (
    ENDPOINT,
    API_TOKEN,
    API_TOKEN_GASP,
    PROJECT_ID_GASPILLAGE,
    MODEL_ID_GASPILLAGE,
    PROJECT_ID_PARTICIPATION,
    MODEL_ID_PARTICIPATION,
    CSV_PREDICTIONS,
    TRAIN_DATA,
)

from model.model_xgboost import XGBoostPredictor


def load_data():
    """Load and filter dataset"""
    dataset = pd.read_csv(CSV_PREDICTIONS)

    closed_values = [
        "VACANCES SCOLAIRES",
        "FERIE",
        "FÉRIÉ",
        "FERIÉ",
        "PAS DE CENTRE",
        "CENTRE FERMÉ",
        "CENTRE FERME",
        "ferme",
    ]

    for col in ["Commentaire semaine", "Commentaire jour"]:
        if col in dataset.columns:
            dataset = dataset[~dataset[col].isin(closed_values)]
        else:
            print(f"Warning: Column '{col}' not found in dataset. Skipping filter.")

    return dataset


def predict_waste_and_participation(final_dataset, model_choice="local"):
    """Make predictions using selected model"""
    if model_choice == "datarobot":
        try:
            dr.Client(endpoint=ENDPOINT, token=API_TOKEN_GASP)
            project = dr.Project.get(PROJECT_ID_GASPILLAGE)
            model = dr.Model.get(PROJECT_ID_GASPILLAGE, MODEL_ID_GASPILLAGE)

            pred_data = final_dataset.copy()
            pred_dataset = project.upload_dataset(pred_data)
            pred_job = model.request_predictions(pred_dataset.id)
            predictions = pred_job.get_result_when_complete(max_wait=3600)

            results = [float(row[1]["prediction"]) for row in predictions.iterrows()]
            final_dataset.loc[:, "Taux gaspillage prédit datarobot"] = results

            dr.Client(endpoint=ENDPOINT, token=API_TOKEN)
            project_participation = dr.Project.get(PROJECT_ID_PARTICIPATION)
            model_participation = dr.Model.get(
                PROJECT_ID_PARTICIPATION, MODEL_ID_PARTICIPATION
            )

            pred_dataset_participation = project_participation.upload_dataset(pred_data)
            pred_job_participation = model_participation.request_predictions(
                pred_dataset_participation.id
            )
            predictions_participation = pred_job_participation.get_result_when_complete(
                max_wait=3600
            )

            results_participation = [
                float(row[1]["prediction"])
                for row in predictions_participation.iterrows()
            ]
            final_dataset.loc[:, "Taux participation datarobot"] = results_participation

        except Exception as e:
            st.error(f"Erreur lors de la prédiction avec DataRobot: {str(e)}")
            model_choice = "local"

    if model_choice == "local":
        try:
            predictor = XGBoostPredictor()
            predictor.train(TRAIN_DATA)
            predictor.predict_and_save(final_dataset)

            st.success(f"Prédictions sauvegardées dans output")
        except Exception as e:
            st.error(f"Erreur lors de la prédiction avec le modèle local: {str(e)}")

    return final_dataset


def prepare_dataset(dataset, num_week):
    """Prepare dataset for predictions"""
    final_dataset = dataset.copy()
    final_dataset["Date"] = pd.to_datetime(final_dataset["Date"])

    st.markdown(
        """
        <style>
        div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
            background-color: #1b5e20;
            
        }
        div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover > div:first-child {
            background-color: #2e7d32;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    model_choice = st.radio(
        "Choisir le modèle de prédiction",
        ["DataRobot", "Local (XGBoost)"],
        key="model_choice",
    )

    result = predict_waste_and_participation(
        final_dataset, model_choice.lower().replace(" (xgboost)", "")
    )
    if result is None:
        st.error(
            "Impossible de générer des prédictions. Veuillez vérifier les données d'entrée."
        )
        return None

    st.success(f"Prédictions réalisées avec succès via {model_choice}")
    return result
