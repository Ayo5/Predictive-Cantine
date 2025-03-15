import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import joblib

# Load the trained model
# model = joblib.load('linear_regression_model.pkl')

# Streamlit interface
st.title("POC Vision Food")

# Input fields for new data
year = st.number_input("Year", min_value=2000, max_value=2100, value=2023)
month = st.number_input("Month", min_value=1, max_value=12, value=1)
day = st.number_input("Day", min_value=1, max_value=31, value=1)
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

# Widget
st.checkbox('Yes')
st.button('Click Me')
st.radio('Pick your gender', ['Male', 'Female'])
st.selectbox('Pick a fruit', ['Apple', 'Banana', 'Orange'])
st.multiselect('Choose a planet', ['Jupiter', 'Mars', 'Neptune'])
st.select_slider('Pick a mark', ['Bad', 'Good', 'Excellent'])
st.slider('Pick a number', 0, 50)









# Create a DataFrame for the new observation
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
    # Add one-hot encoded values for categorical variables
}

#nouveau_df = pd.DataFrame([nouvelle_observation])
#nouveau_df = nouveau_df.reindex(columns=model.feature_names_in_, fill_value=0)

# Prediction
#if st.button("Predict"):
#    prediction = model.predict(nouveau_df)
#    st.write(f"Predicted Waste Rate: {prediction[0]:.2f}%")