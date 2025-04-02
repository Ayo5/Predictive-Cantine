import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import joblib

# Load data
data_meteo = pd.read_csv("data-meteo.csv")
data_meteo["Date"] = pd.to_datetime(data_meteo["Date"])
data_meteo["Year"] = data_meteo["Date"].dt.year
data_meteo["Month"] = data_meteo["Date"].dt.month
data_meteo["Day"] = data_meteo["Date"].dt.day
data_meteo["Taux gaspillage"] = pd.to_numeric(data_meteo["Taux gaspillage"], errors="coerce")
data_meteo = data_meteo.dropna()

# One-hot encode categorical columns
columns_to_encode = ["Entrée", "Dessert", "Laitage", "Légumes", "Plat", "Secteur", "Allergies", "Gouter", "Gouter_02"]
existing_columns = [col for col in columns_to_encode if col in data_meteo.columns]
data_meteo = pd.get_dummies(data_meteo, columns=existing_columns)

# Define target variable and features
y = data_meteo["Taux gaspillage"]
X = data_meteo.drop(columns=["Taux gaspillage" ,"Date" ,  "Commentaire semaine" , "Commentaire jour",
                             "Code_gouter", "Code_gouter_02" , "Code_entrée" , "Code_entrée" , "Code_plat" , "Code_légumes" , "Code_laitage"
                             , "Code_dessert"])

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, 'linear_regression_model.pkl')

# Evaluate the model
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')
print(f'Coefficients: {model.coef_}')
print(f'Intercept: {model.intercept_}')