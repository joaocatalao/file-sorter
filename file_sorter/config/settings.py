import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")

DEFAULTS = {
    "close_tab_after_save": True,
    "minimize_to_tray": False
}

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_settings():
    ensure_data_dir()
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r") as f:
                return json.load(f)
        except Exception:
            print("⚠️ Failed to load settings.json, falling back to defaults.")
            return DEFAULTS.copy()
    else:
        # Save defaults on first launch
        save_settings(DEFAULTS)
        return DEFAULTS.copy()

def save_settings(settings: dict):
    ensure_data_dir()
    try:
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print("⚠️ Failed to save settings.json:", e)
