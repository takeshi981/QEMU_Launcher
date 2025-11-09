import os
import json

PROFILE_DIR = "profiles"

def ensure_profile_dir():
    if not os.path.exists(PROFILE_DIR):
        os.makedirs(PROFILE_DIR)

def list_profiles():
    ensure_profile_dir()
    return [f for f in os.listdir(PROFILE_DIR) if f.endswith(".json")]

def load_profile(name):
    ensure_profile_dir()
    path = os.path.join(PROFILE_DIR, name)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

def save_profile(name, config):
    ensure_profile_dir()
    path = os.path.join(PROFILE_DIR, name)
    with open(path, "w") as f:
        json.dump(config, f, indent=4)

def delete_profile(name):
    ensure_profile_dir()
    path = os.path.join(PROFILE_DIR, name)
    if os.path.exists(path):
        os.remove(path)