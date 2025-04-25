import os 

API_TOKEN = "NjgwYTJiOTczYjNjODM5MjcxZWQ3OGFhOm80Q0g1NWFRcWt5VXNNS1hsQkM0NWxjNHhxM0FEdmp4V2pUQm1Yci9WZmc9"
PROJECT_ID_PARTICIPATION ="680b8998f50ecb44cf49efb1"
MODEL_ID_PARTICIPATION = "680b8a71be4ff87c5f6153ce"

API_TOKEN_GASP = "NjgwYTJiOTczYjNjODM5MjcxZWQ3OGFhOm80Q0g1NWFRcWt5VXNNS1hsQkM0NWxjNHhxM0FEdmp4V2pUQm1Yci9WZmc9"
PROJECT_ID_GASPILLAGE ="680a1daaa89daf12c46838e1"
MODEL_ID_GASPILLAGE = "680a2bea9f1281df4aed786c"
ENDPOINT = "https://app.datarobot.com/api/v2"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_DATA = os.path.join(BASE_DIR, "data", "data-predictions.csv")
CSV_PREDICTIONS = os.path.join(BASE_DIR, "uploads", "menu.csv")
CSV_CO2_COUTS = os.path.join(BASE_DIR, "uploads", "couts.csv")

NUM_WEEKS = 16  
WEEKDAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

DEFAULT_DELAY_MAIN_DISH = 7  
DEFAULT_DELAY_MENU = 30  