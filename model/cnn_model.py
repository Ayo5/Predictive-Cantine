import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv1D, Flatten, MaxPooling1D, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import joblib
import os

# Set random seed for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

def load_and_preprocess_data():
    """Load and preprocess the data from CSV files"""
    print("Loading data...")
    
    # Load the main dataset
    data_meteo = pd.read_csv("data-meteo.csv")
    
    # Load CO2 and cost data
    co2_costs = pd.read_csv("co2_couts.csv")
    
    # Convert date to datetime
    data_meteo["Date"] = pd.to_datetime(data_meteo["Date"])
    
    # Extract date features
    data_meteo["Year"] = data_meteo["Date"].dt.year
    data_meteo["Month"] = data_meteo["Date"].dt.month
    data_meteo["Day"] = data_meteo["Date"].dt.day
    data_meteo["DayOfWeek"] = data_meteo["Date"].dt.dayofweek
    
    # Convert target variables to numeric
    data_meteo["Taux gaspillage"] = pd.to_numeric(data_meteo["Taux gaspillage"], errors="coerce")
    data_meteo["Taux participation"] = pd.to_numeric(data_meteo["Taux participation"], errors="coerce")
    
    # Drop rows with missing target values
    data_meteo = data_meteo.dropna(subset=["Taux gaspillage", "Taux participation"])
    
    # Handle special cases like "FERIE", "CENTRE FERME", etc.
    special_cases = ["FERIE", "CENTRE FERME", "CENTRE FERMÉ", "VACANCES SCOLAIRES", "FERMÉ"]
    
    # Create a new column to indicate special days
    data_meteo["SpecialDay"] = data_meteo["Plat"].apply(
        lambda x: 1 if isinstance(x, str) and any(case in x.upper() for case in special_cases) else 0
    )
    
    # Filter out rows with special cases for training
    data_filtered = data_meteo[data_meteo["SpecialDay"] == 0].copy()
    
    # Create a mapping of food items to CO2 values
    co2_mapping = dict(zip(co2_costs["Nom"].str.lower(), co2_costs["Kg CO2 pour 1 kilo ou 1L"]))
    
    # Function to extract CO2 value for a food item
    def get_co2_value(food_item):
        if not isinstance(food_item, str):
            return 0
        
        food_item = food_item.lower()
        for key, value in co2_mapping.items():
            if key in food_item:
                return value
        return 0
    
    # Calculate CO2 impact for each meal component
    for col in ["Entrée", "Plat", "Légumes", "Laitage", "Dessert", "Gouter"]:
        if col in data_filtered.columns:
            data_filtered[f"{col}_CO2"] = data_filtered[col].apply(get_co2_value)
    
    # Calculate total CO2 impact
    co2_cols = [col for col in data_filtered.columns if col.endswith("_CO2")]
    if co2_cols:
        data_filtered["Total_CO2"] = data_filtered[co2_cols].sum(axis=1)
    
    print(f"Data loaded and preprocessed. Shape: {data_filtered.shape}")
    return data_filtered

def prepare_features_and_targets(data):
    """Prepare features and target variables for the model"""
    print("Preparing features and targets...")
    
    # Define categorical and numerical features
    categorical_features = [
        "Secteur", "Month", "DayOfWeek", 
        "Entrée", "Plat", "Légumes", "Laitage", "Dessert", "Gouter"
    ]
    
    # Keep only categorical features that exist in the data
    categorical_features = [col for col in categorical_features if col in data.columns]
    
    numerical_features = [
        "Year", "Day", "Température", "Humidité", 
        "Vitesse du vent moyen 10 mn", "Attente moyenne", "Allergies"
    ]
    
    # Add CO2 features if they exist
    co2_features = [col for col in data.columns if col.endswith("_CO2")]
    if co2_features:
        numerical_features.extend(co2_features)
    
    # Keep only numerical features that exist in the data
    numerical_features = [col for col in numerical_features if col in data.columns]
    
    # Define the preprocessing for categorical features
    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse=False))
    ])
    
    # Define the preprocessing for numerical features
    numerical_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])
    
    # Combine preprocessing steps
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    # Prepare X and y
    X = data[numerical_features + categorical_features]
    y_waste = data["Taux gaspillage"]
    y_attendance = data["Taux participation"]
    
    # Split the data
    X_train, X_test, y_waste_train, y_waste_test, y_attendance_train, y_attendance_test = train_test_split(
        X, y_waste, y_attendance, test_size=0.2, random_state=42
    )
    
    # Fit and transform the data
    X_train_preprocessed = preprocessor.fit_transform(X_train)
    X_test_preprocessed = preprocessor.transform(X_test)
    
    # Save the preprocessor for later use
    joblib.dump(preprocessor, 'cnn_preprocessor.pkl')
    
    # Reshape data for CNN (samples, timesteps, features)
    X_train_cnn = X_train_preprocessed.reshape(X_train_preprocessed.shape[0], 1, X_train_preprocessed.shape[1])
    X_test_cnn = X_test_preprocessed.reshape(X_test_preprocessed.shape[0], 1, X_test_preprocessed.shape[1])
    
    print(f"Features prepared. Training shape: {X_train_cnn.shape}")
    return (X_train_cnn, X_test_cnn, y_waste_train, y_waste_test, 
            y_attendance_train, y_attendance_test, preprocessor)

def build_cnn_model(input_shape):
    """Build a CNN model for regression"""
    model = Sequential([
        Conv1D(filters=64, kernel_size=1, activation='relu', input_shape=input_shape),
        MaxPooling1D(pool_size=1),
        Conv1D(filters=32, kernel_size=1, activation='relu'),
        Flatten(),
        Dense(64, activation='relu'),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(2)  # Two outputs: waste rate and attendance rate
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='mse',
        metrics=['mae']
    )
    
    return model

def train_and_evaluate_model(X_train, X_test, y_waste_train, y_waste_test, 
                             y_attendance_train, y_attendance_test):
    """Train and evaluate the CNN model"""
    print("Training the model...")
    
    # Combine targets for multi-output model
    y_train = np.column_stack((y_waste_train, y_attendance_train))
    y_test = np.column_stack((y_waste_test, y_attendance_test))
    
    # Build the model
    model = build_cnn_model((X_train.shape[1], X_train.shape[2]))
    
    # Train the model
    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        verbose=1
    )
    
    # Evaluate the model
    loss, mae = model.evaluate(X_test, y_test)
    print(f"Test Loss: {loss:.4f}")
    print(f"Test MAE: {mae:.4f}")
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics for each output
    waste_mae = np.mean(np.abs(y_pred[:, 0] - y_test[:, 0]))
    attendance_mae = np.mean(np.abs(y_pred[:, 1] - y_test[:, 1]))
    
    print(f"Waste Rate MAE: {waste_mae:.4f}")
    print(f"Attendance Rate MAE: {attendance_mae:.4f}")
    
    # Plot training history
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper right')
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['mae'])
    plt.plot(history.history['val_mae'])
    plt.title('Model MAE')
    plt.ylabel('MAE')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper right')
    
    plt.tight_layout()
    plt.savefig('cnn_training_history.png')
    
    # Save the model
    model.save('cnn_food_waste_attendance_model.h5')
    
    return model, y_pred, y_test

def predict_new_meal(model, preprocessor, meal_data):
    """Make predictions for a new meal"""
    # Preprocess the input data
    X_new = preprocessor.transform(pd.DataFrame([meal_data]))
    
    # Reshape for CNN
    X_new_cnn = X_new.reshape(X_new.shape[0], 1, X_new.shape[1])
    
    # Make prediction
    prediction = model.predict(X_new_cnn)[0]
    
    return {
        'waste_rate': prediction[0],
        'attendance_rate': prediction[1]
    }

def main():
    """Main function to run the entire pipeline"""
    # Load and preprocess data
    data = load_and_preprocess_data()
    
    # Prepare features and targets
    X_train, X_test, y_waste_train, y_waste_test, y_attendance_train, y_attendance_test, preprocessor = prepare_features_and_targets(data)
    
    # Train and evaluate model
    model, y_pred, y_test = train_and_evaluate_model(
        X_train, X_test, y_waste_train, y_waste_test, y_attendance_train, y_attendance_test
    )
    
    # Example prediction
    example_meal = {
        'Secteur': 1,
        'Year': 2023,
        'Month': 5,
        'Day': 15,
        'DayOfWeek': 0,  # Monday
        'Entrée': 'Pamplemousse',
        'Plat': 'Rôti de porc au jus',
        'Légumes': 'Lentilles',
        'Laitage': 'Crème au chocolat',
        'Dessert': '',
        'Gouter': 'Pain/ confiture d\'abricots/ lait',
        'Température': 15.0,
        'Humidité': 70.0,
        'Vitesse du vent moyen 10 mn': 3.0,
        'Attente moyenne': 10.0,
        'Allergies': 0.02,
        'Entrée_CO2': 0.4,  # Pamplemousse (agrumes)
        'Plat_CO2': 12.0,   # Porc
        'Légumes_CO2': 1.8,  # Lentilles (légumineuses)
        'Laitage_CO2': 3.2,  # Crème (lait)
        'Gouter_CO2': 3.2,   # Lait
        'Total_CO2': 20.6
    }
    
    prediction = predict_new_meal(model, preprocessor, example_meal)
    print("\nExample Prediction:")
    print(f"Predicted Waste Rate: {prediction['waste_rate']:.2%}")
    print(f"Predicted Attendance Rate: {prediction['attendance_rate']:.2%}")

if __name__ == "__main__":
    main()