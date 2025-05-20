import os
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor
from config import BASE_DIR, CSV_PREDICTIONS


class XGBoostPredictor:
    def __init__(self):
        self.text_cols = ["Entrée", "Plat", "Légumes", "Laitage", "Dessert", "Gouter"]
        self.num_cols = [
            "Température",
            "Humidité",
            "Vitesse du vent moyen 10 mn",
            "Attente moyenne",
        ]
        self.model = None
        self.pipeline = None

    def prepare_data(self, df):
        """Prépare les données pour l'entraînement ou la prédiction"""
        for col in self.text_cols:
            df[col] = df[col].fillna("")
            df[col] = df[col].astype(str)
        return df

    def create_pipeline(self):
        """Crée le pipeline de traitement et de prédiction"""
        preprocessor = ColumnTransformer(
            transformers=[
                ("text_entrée", TfidfVectorizer(), "Entrée"),
                ("text_plat", TfidfVectorizer(), "Plat"),
                ("text_légumes", TfidfVectorizer(), "Légumes"),
                ("text_laitage", TfidfVectorizer(), "Laitage"),
                ("text_dessert", TfidfVectorizer(), "Dessert"),
                ("text_gouter", TfidfVectorizer(), "Gouter"),
                ("num", StandardScaler(), self.num_cols),
            ]
        )

        model = MultiOutputRegressor(
            XGBRegressor(objective="reg:squarederror", random_state=42)
        )

        return Pipeline(steps=[("preprocessing", preprocessor), ("regressor", model)])

    def train(self, train_data_path):
        """Entraîne le modèle avec les données d'entraînement"""
        try:
            df_train = pd.read_csv(train_data_path)
            df_train = self.prepare_data(df_train)

            X = df_train.drop(["Date", "Taux participation", "Taux gaspillage"], axis=1)
            y = df_train[["Taux participation", "Taux gaspillage"]]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            self.pipeline = self.create_pipeline()
            param_grid = {
                "regressor__estimator__n_estimators": [100, 200],
                "regressor__estimator__max_depth": [3, 5, 7],
                "regressor__estimator__learning_rate": [0.05, 0.1, 0.2],
                "regressor__estimator__subsample": [0.8, 1.0],
            }

            grid_search = GridSearchCV(
                self.pipeline,
                param_grid,
                cv=3,
                scoring="neg_mean_squared_error",
                verbose=1,
                n_jobs=-1,
            )
            grid_search.fit(X_train, y_train)
            self.pipeline = grid_search.best_estimator_

            return True

        except Exception as e:
            print(f"Erreur lors de l'entraînement : {str(e)}")
            return False

    def predict_and_save(self, input_csv, output_path=None):
        """Prédit et sauvegarde les résultats dans un fichier CSV"""
        try:
            if output_path is None:
                output_path = os.path.join(BASE_DIR, "output", "predictions.csv")

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if isinstance(input_csv, pd.DataFrame):
                df_pred = input_csv.copy()
            else:
                df_pred = pd.read_csv(input_csv)

            df_pred = self.prepare_data(df_pred)

            X_pred = df_pred.drop("Date", axis=1)
            predictions = self.pipeline.predict(X_pred)

            df_pred["Taux participation prédit"] = predictions[:, 0]
            df_pred["Taux gaspillage prédit"] = predictions[:, 1]

            df_pred.to_csv(output_path, index=False)
            print(f"Prédictions sauvegardées dans {output_path}")

            return predictions

        except Exception as e:
            print(f"Erreur lors de la prédiction : {str(e)}")
            return None


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TRAIN_DATA = os.path.join(BASE_DIR, "data", "data_prediction.csv")
    INPUT_CSV = os.path.join(BASE_DIR, "uploads", "menu.csv")
    OUTPUT_PATH = os.path.join(BASE_DIR, "output", "pred.csv")

    predictor = XGBoostPredictor()
    if predictor.train(TRAIN_DATA):
        predictor.predict_and_save(INPUT_CSV, OUTPUT_PATH)
