import os 

API_TOKEN = "NjdmZDQwYzJkODMzODZiY2Y0MTk5NjI1Ok1tbVZrSUtyeDdINGFiNVo3amZKMEJaMzJhVXI2aGNmK0lrek9mRlJ0a0E9"
PROJECT_ID_PARTICIPATION ="67fd3bea98b547d51db6629e"
MODEL_ID_PARTICIPATION = "67fd3c9c28612c6236b2a9bb"

API_TOKEN_GASP = "NjdmZDQxYjRmMzIzNmJiMGZjMTk5NTVmOiswNzVTNFZGZzFJMTBGVWc0dTFFVWZ1aWtHMHZ4YUtNU2RSSTVZWWxaaDg9"
PROJECT_ID_GASPILLAGE ="67fd2e75a0da87f6f4503261"
MODEL_ID_GASPILLAGE = "67fd35bb84cb9ee67965e9eb"
ENDPOINT = "https://app.datarobot.com/api/v2"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_DATA = os.path.join(BASE_DIR, "data", "data-predictions.csv")
CSV_PREDICTIONS = os.path.join(BASE_DIR, "data", "data-meteo.csv")
CSV_CO2_COUTS = os.path.join(BASE_DIR, "data", "co2_couts.csv")

NUM_WEEKS = 16  
WEEKDAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

DEFAULT_DELAY_MAIN_DISH = 7  
DEFAULT_DELAY_MENU = 30  