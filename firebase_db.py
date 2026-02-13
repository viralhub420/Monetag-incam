import os
import json
import firebase_admin
from firebase_admin import credentials, db

def init_firebase():
    if not firebase_admin._apps:
        firebase_json = os.getenv("FIREBASE_CREDENTIALS")

        if not firebase_json:
            raise ValueError("FIREBASE_CREDENTIALS not found in environment variables")

        cred_dict = json.loads(firebase_json)
        cred = credentials.Certificate(cred_dict)

        firebase_admin.initialize_app(cred, {
            "databaseURL": os.getenv("DATABASE_URL")
        })

    return db.reference("/")
