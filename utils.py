import pytz
from datetime import datetime
import json
import os

def get_current_uk_hour():
    uk_tz = pytz.timezone("Europe/London")
    return datetime.now(uk_tz).hour

def load_previous():
    path = "data/processed.json"
    if not os.path.exists(path):
        return set()
    with open(path, "r") as f:
        return set(json.load(f))

def save_processed(company_numbers):
    with open("data/processed.json", "w") as f:
        json.dump(list(company_numbers), f)
