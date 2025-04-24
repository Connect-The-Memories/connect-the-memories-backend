import pyrebase
import firebase_admin
from firebase_admin import credentials, storage
from firebase_admin import firestore as fs
from google.cloud import firestore, vision
from google.oauth2 import service_account

from config import app_config


"""
    Firebase Admin Credentials and Initialization
"""
try:
    cred = credentials.Certificate(app_config.FIREBASE_ADMIN_CREDENTIALS)
    firebase_admin.initialize_app(cred, {
        "storageBucket": app_config.FIREBASE_CLOUD_STORAGE_BUCKET
    })

    firestore_db = fs.client()
    bucket = storage.bucket()
except Exception as e:
    raise RuntimeError(f"Error initializing Firebase Admin SDK: {e}")


"""
    GCP Firestore Initialization for Transactions
"""
try:
    gcp_credentials = service_account.Credentials.from_service_account_file(app_config.FIREBASE_ADMIN_CREDENTIALS)
    gcp_firestore_db = firestore.Client(credentials=gcp_credentials)
    vision_client = vision.ImageAnnotatorClient(credentials=gcp_credentials)
except Exception as e:
    raise RuntimeError(f"Error initializing GCP Firestore: {e}")



"""
    Pyrebase Config and Initialization
"""
try:
    config = {
        "apiKey": app_config.FIREBASE_API_KEY,
        "authDomain": app_config.FIREBASE_AUTH_DOMAIN,
        "databaseURL": "",  # Required to bypass Pyrebase error since we aren't using Firebase Realtime Database
        "storageBucket": app_config.FIREBASE_CLOUD_STORAGE_BUCKET
    }

    firebase = pyrebase.initialize_app(config)
    pyre_auth = firebase.auth()
    pyre_cloud_storage = firebase.storage()
except Exception as e:
    raise RuntimeError(f"Error initializing Pyrebase: {e}")