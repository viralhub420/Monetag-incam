import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import os
import json
from config import DATABASE_URL

# ==============================
# Firebase Initialize (Render Safe)
# ==============================
if not firebase_admin._apps:
    cred_json = os.getenv("FIREBASE_CREDENTIALS")

    if cred_json:
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            "databaseURL": DATABASE_URL
        })
    else:
        raise ValueError("FIREBASE_CREDENTIALS not found in environment")


# ==============================
# Create New User
# ==============================
def create_user(user_id):
    ref = db.reference(f"users/{user_id}")
    if not ref.get():
        ref.set({
            "points": 0,
            "created_at": str(datetime.now()),
            "last_active": str(datetime.now()),
            "joined": False
        })


# ==============================
# Update Last Active
# ==============================
def update_last_active(user_id):
    ref = db.reference(f"users/{user_id}")
    ref.update({
        "last_active": str(datetime.now())
    })


# ==============================
# Set Join Status
# ==============================
def set_join_status(user_id, status: bool):
    ref = db.reference(f"users/{user_id}")
    ref.update({
        "joined": status
    })


# ==============================
# Get User Data
# ==============================
def get_user_data(user_id):
    ref = db.reference(f"users/{user_id}")
    return ref.get() or {}
