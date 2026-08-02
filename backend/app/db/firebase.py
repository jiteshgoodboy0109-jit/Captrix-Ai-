import os
import firebase_admin
from firebase_admin import credentials, firestore

# Determine path to firebase key file
KEY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "firebase-key.json")

db = None
firebase_app = None

def init_firebase():
    global db, firebase_app
    if firebase_app is not None:
        return db

    if os.path.exists(KEY_PATH):
        try:
            cred = credentials.Certificate(KEY_PATH)
            firebase_app = firebase_admin.initialize_app(cred, {
                'projectId': 'captrix-ai'
            })
            db = firestore.client()
            print(f"[FIREBASE] Initialized Cloud Firestore successfully (Project ID: captrix-ai)")
            return db
        except Exception as e:
            print(f"[FIREBASE WARNING] Failed to initialize Firebase Admin SDK: {e}")
            return None
    else:
        print(f"[FIREBASE WARNING] Key file not found at {KEY_PATH}")
        return None

# Attempt initialization on module load
init_firebase()
