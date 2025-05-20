# FoodVision 🍽️

FoodVision est une application innovante de gestion et d'optimisation des menus de restauration collective, utilisant l'intelligence artificielle pour prédire les taux de participation et de gaspillage alimentaire.

## Fonctionnalités Principales 🚀

- **Prédiction des Taux**
  - Taux de participation des convives
  - Taux de gaspillage alimentaire

- **Gestion des Données**
  - Import de menus via fichiers CSV
  - Import des données CO2 et coûts
  - Saisie manuelle des données

- **Double Moteur de Prédiction**
  - API DataRobot pour des prédictions précises
  - Modèle XGBoost local en solution de repli

- **Analyse Environnementale**
  - Suivi des émissions CO2 par aliment
  - Calcul des coûts par repas
  - Statistiques détaillées

## Structure des Données 📊

### Format du CSV Menu
Colonnes requises :
- Date
- Entrée
- Plat
- Légumes
- Dessert
- Laitage
- Gouter (optionnel)
- Température
- Humidité
- Vitesse du vent moyen 10 mn
- Attente moyenne

### Format du CSV CO2 et Coûts
Colonnes requises :
- Nom
- Kg CO2 pour 1 kilo ou 1L
- Prix Unitaire Kg

## Technologies Utilisées 💻

- Python
- Streamlit (Interface utilisateur)
- Pandas (Manipulation des données)
- Scikit-learn (Prétraitement)
- XGBoost (Modèle de prédiction local)
- DataRobot API (Prédictions avancées)

## Installation et Utilisation 🛠️

1. Cloner le repository
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Lancer l'application :
   ```bash
   streamlit run app.py
   ```

## Modèles de Prédiction 🤖

### DataRobot
- Modèle principal pour les prédictions
- Nécessite une connexion API valide
- Configuration dans config.py

### XGBoost Local
- Solution de repli automatique
- Entraîné sur les données historiques
- Optimisé par validation croisée

## Structure du Projet 📁

```
FoodVision/
├── components/
│   └── upload_csv.py     # Gestion des imports CSV
├── model/
│   └── model_xgboost.py  # Modèle de prédiction local
├── data/
│   └── data_prediction.csv # Données d'entraînement
├── uploads/              # Dossier des fichiers importés
├── config.py            # Configuration globale
├── data_loader.py       # Chargement et préparation des données
└── app.py              # Point d'entrée de l'application
```

## Sécurité et Confidentialité 🔒

- Les tokens API sont stockés dans config.py
- Les données sont traitées localement
- Aucune donnée n'est partagée sans autorisation

## Performance et Limites ⚠️

- Prédictions optimisées pour des menus sur 16 semaines
- Taux de participation prédits entre 50% et 100%
- Taux de gaspillage prédits entre 1% et 50%
- Basculement automatique vers le modèle local en cas d'erreur API