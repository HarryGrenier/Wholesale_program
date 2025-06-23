import os
import json
from models.database_creation import create_tables
from ui.settings import DEFAULT_SETTINGS, SETTINGS_FILE

DATA_DIR = os.path.join(os.path.dirname(__file__), "Data")
DB_PATH = os.path.join(DATA_DIR, "invoice.db")

def ensure_data_directory():
    if not os.path.exists(DATA_DIR):
        print("Creating 'Data/' directory...")
        os.makedirs(DATA_DIR)

def ensure_settings_json():
    if not os.path.exists(SETTINGS_FILE):
        print("Creating default settings.json...")
        with open(SETTINGS_FILE, "w") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)

def ensure_database():
    if not os.path.exists(DB_PATH):
        print("Creating invoice.db and schema...")
        create_tables()

def run_setup():
    ensure_data_directory()
    ensure_settings_json()
    ensure_database()
