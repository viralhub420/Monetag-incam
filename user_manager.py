import json
import os
from datetime import datetime

DATA_FILE = "users.json"


# ==========================
# Load Database
# ==========================
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)

    with open(DATA_FILE, "r") as f:
        return json.load(f)


# ==========================
# Save Database
# ==========================
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ==========================
# Create New User
# ==========================
def create_user(user_id):
    data = load_data()

    if user_id not in data:
        data[user_id] = {
            "points": 0,
            "created_at": str(datetime.now()),
            "last_active": str(datetime.now()),
            "joined": False
        }

        save_data(data)


# ==========================
# Update Last Active
# ==========================
def update_last_active(user_id):
    data = load_data()

    if user_id in data:
        data[user_id]["last_active"] = str(datetime.now())
        save_data(data)


# ==========================
# Set Join Status
# ==========================
def set_join_status(user_id, status: bool):
    data = load_data()

    if user_id in data:
        data[user_id]["joined"] = status
        save_data(data)


# ==========================
# Get User Data
# ==========================
def get_user_data(user_id):
    data = load_data()
    return data.get(user_id, {})
