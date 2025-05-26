import os

# API_TOKEN = ""
# PROJECT_ID_PARTICIPATION = ""
# MODEL_ID_PARTICIPATION = ""

API_TOKEN = "NjgzNGJmNjlhMmQ1ZWJhMTIwNzBhODA0OjFzUFlaLzc2cVZnMVRady9jL2JGZkUzRG5xRFlqOGJMSXVyRzJMWThJQk09"
PROJECT_ID_PARTICIPATION = "6834bcbddd6250e458d1a89b"
MODEL_ID_PARTICIPATION = "6834bd9139eaf401ad4e14d5"

API_TOKEN_GASP = "NjgzNGJmNjlhMmQ1ZWJhMTIwNzBhODA0OjFzUFlaLzc2cVZnMVRady9jL2JGZkUzRG5xRFlqOGJMSXVyRzJMWThJQk09"
PROJECT_ID_GASPILLAGE = "6834b86eae09c6bfa581cc52"
MODEL_ID_GASPILLAGE = "6834b9714877853b5f5b256b"
ENDPOINT = "https://app.datarobot.com/api/v2"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_DATA = os.path.join(BASE_DIR, "data", "train_data.csv")
CSV_PREDICTIONS = os.path.join(BASE_DIR, "uploads", "menu.csv")
PREDICTIONS = os.path.join(BASE_DIR, "output", "predictions.csv")
CSV_CO2_COUTS = os.path.join(BASE_DIR, "uploads", "couts.csv")

NUM_WEEKS = 16
WEEKDAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

DEFAULT_DELAY_MAIN_DISH = 7
DEFAULT_DELAY_MENU = 30
