import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import joblib

# Load the trained model
# model = joblib.load('linear_regression_model.pkl')

# Streamlit interface
st.title("POC Vision Food")
st.markdown("Il s'agit d'une preuve que notre application peux fonction")

# Champs qui permet d'envoyer un csv

upload_csv = st.file_uploader("Importer un CSV", type="csv")
if upload_csv :
    df = pd.read_csv(upload_csv)
    st.write("Apercu",df.head())

    # Champs qui permet d'explorer les données
    st.subheader("Exploration")
    if st.checkbox("Afficher stat descriptives"):
        st.write(df.describe())


# Champs qui permettra de faire une prédiction
date = st.date_input("Choisir une date")
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









# Utilisation des données saisies par le user
# nouvelle_observation = {
#     "Year": year,
#     "Month": month,
#     "Day": day,
#     "Entrée": entree,
#     "Plat": plat,
#     "Légumes": legumes,
#     "Laitage": laitage,
#     "Gouter": gouter,
#     "Allergies": allergies,
#     "Taux participation": taux_participation,
#     "Température": temperature,
#     "Humidité": humidite,
#     "Vitesse du vent moyen 10 mn": vent,
#     "Attente moyenne": attente,
#     # Add one-hot encoded values for categorical variables
# }

#nouveau_df = pd.DataFrame([nouvelle_observation])
#nouveau_df = nouveau_df.reindex(columns=model.feature_names_in_, fill_value=0)

# Prediction
#if st.button("Predict"):
#    prediction = model.predict(nouveau_df)
#    st.write(f"Predicted Waste Rate: {prediction[0]:.2f}%")