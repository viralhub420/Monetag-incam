from datetime import datetime
from firebase_db import init_firebase

db_ref = init_firebase()

def get_user_ref(user_id: str):
    return db_ref.child("users").child(user_id)

def user_exists(user_id: str):
    return get_user_ref(user_id).get() is not None

def create_user(user_id: str):
    if not user_exists(user_id):
        get_user_ref(user_id).set({
            "points": 0,
            "created_at": datetime.utcnow().isoformat(),
            "last_active": datetime.utcnow().isoformat(),
            "joined": False
        })

def update_last_active(user_id: str):
    get_user_ref(user_id).update({
        "last_active": datetime.utcnow().isoformat()
    })

def get_user_data(user_id: str):
    return get_user_ref(user_id).get()

def set_join_status(user_id: str, status: bool):
    get_user_ref(user_id).update({
        "joined": status
    })
