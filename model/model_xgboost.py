import os
import pandas as pd 
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PREDICTIONS = "/Users/dayabe/Documents/Projet/Kesk'IA/uploads/menu.csv"
TRAIN_DATA = "/Users/dayabe/Documents/Projet/Kesk'IA/data/data_prediction.csv"

df_train = pd.read_csv(TRAIN_DATA)

text_cols = ["Entrée", "Plat", "Légumes", "Laitage", "Dessert", "Gouter"]
for col in text_cols:
    df_train[col] = df_train[col].fillna('')
    df_train[col] = df_train[col].astype(str)

print (df_train.columns)
X = df_train.drop(['Date', 'Taux participation', 'Taux gaspillage'], axis=1)
y = df_train[['Taux participation', 'Taux gaspillage']]

text_cols = ["Entrée", "Plat", "Légumes", "Laitage", "Dessert", "Gouter"]
num_cols = ["Température", "Humidité", "Vitesse du vent moyen 10 mn", "Attente moyenne"]

preprocessor = ColumnTransformer(transformers=[
    ("text_entrée", TfidfVectorizer(), "Entrée"),
    ("text_plat", TfidfVectorizer(), "Plat"),
    ("text_légumes", TfidfVectorizer(), "Légumes"),
    ("text_laitage", TfidfVectorizer(), "Laitage"),
    ("text_dessert", TfidfVectorizer(), "Dessert"),
    ("text_gouter", TfidfVectorizer(), "Gouter"),
    ("num", StandardScaler(), num_cols)
])

model = MultiOutputRegressor(XGBRegressor(objective='reg:squarederror', random_state=42))
pipeline = Pipeline(steps=[
    ("preprocessing", preprocessor),
    ("regressor", model)
])

param_grid = {
    "regressor__estimator__n_estimators": [100, 200],
    "regressor__estimator__max_depth": [3, 5, 7],
    "regressor__estimator__learning_rate": [0.05, 0.1, 0.2],
    "regressor__estimator__subsample": [0.8, 1.0]
}

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring='neg_mean_squared_error', verbose=1, n_jobs=-1)
grid_search.fit(X_train, y_train)

df_pred = pd.read_csv(CSV_PREDICTIONS)
for col in text_cols:
    df_pred[col] = df_pred[col].fillna('')
    df_pred[col] = df_pred[col].astype(str)

X_pred = df_pred.drop("Date", axis=1)

prediction = grid_search.predict(X_pred)
df_pred["Taux particiaption"] = prediction[:, 0]
df_pred["Taux gaspillage"] = prediction[:, 1]
df_pred.to_csv("./output/pred.csv", index=False)