import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Définir les plats possibles
entrees = ["Carottes râpées", "Salade verte", "Betteraves", "Taboulé", "Pamplemousse", "Concombres"]
plats = ["Poulet rôti", "Steak haché", "Rôti de porc", "Lasagnes", "Poisson pané", "Rôti de bœuf"]
legumes = ["Riz", "Frites", "Haricots verts", "Petits pois", "Carottes", "Légumes"]
laitages = ["Yaourt nature", "Fromage blanc", "Petit suisse", "Saint Paulin", "Camembert", "Emmental"]
desserts = ["Fruit frais", "Compote", "Gâteau", "Crème dessert", "Tarte aux pommes", "Mousse au chocolat"]
gouters = ["Pain / Fromage / Lait", "Pain / Chocolat / Lait", "Pain / Confiture / Jus"]


start_date = datetime(2024, 9, 1)  
end_date = datetime(2025, 6, 30)  
dates = []
current_date = start_date

while current_date <= end_date:
    # Exclure les weekends (5 = samedi, 6 = dimanche)
    if current_date.weekday() < 5:
        dates.append(current_date.strftime("%Y-%m-%d"))
    current_date += timedelta(days=1)


data = []
for date in dates:
    
    row = {
        "Date": date,
        "Entrée": np.random.choice(entrees),
        "Plat": np.random.choice(plats),
        "Légumes": np.random.choice(legumes),
        "Laitage": np.random.choice(laitages),
        "Dessert": np.random.choice(desserts, p=[0.3, 0.3, 0.2, 0.1, 0.05, 0.05]),  # Certains desserts sont plus fréquents
        "Gouter": np.random.choice(gouters),
        "Taux participation": round(np.random.uniform(0.85, 1.0), 2),
        "Température": round(np.random.uniform(5.0, 25.0), 1),
        "Humidité": round(np.random.randint(40, 80)),
        "Vitesse du vent moyen 10 mn": round(np.random.uniform(2.0, 6.0), 1),
        "Taux gaspillage": round(np.random.uniform(0.01, 0.5), 2),
        "Attente moyenne": round(np.random.uniform(5.0, 40.0), 2)
    }
    
    if np.random.random() < 0.1:
        if np.random.random() < 0.5:
            row["Dessert"] = ""
        else:
            row["Laitage"] = ""
    
    data.append(row)

df = pd.DataFrame(data)
df.to_csv("/Users/dayabe/Documents/Projet/Kesk'IA/dashboard_3_drive/data/data_prediction_simulated_weekly.csv", index=False)

print(f"Fichier généré avec {len(data)} jours de données simulées")