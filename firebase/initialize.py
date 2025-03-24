import pyrebase
import firebase_admin
from firebase_admin import credentials, storage
from firebase_admin import firestore as fs
from google.cloud import firestore
from google.oauth2 import service_account

from config import app_config


"""
    Firebase Admin Credentials and Initialization
"""
if not app_config.FIREBASE_ADMIN_CREDENTIALS == "":
    cred = credentials.Certificate(app_config.FIREBASE_ADMIN_CREDENTIALS)
    firebase_admin.initialize_app(cred, {
        "storageBucket": app_config.FIREBASE_CLOUD_STORAGE_BUCKET
    })
else:
    firebase_admin.initialize_app(options={
        "storageBucket": app_config.FIREBASE_CLOUD_STORAGE_BUCKET
    })

firestore_db = fs.client()
bucket = storage.bucket()


"""
    GCP Firestore Initialization for Transactions
"""
gcp_credentials = service_account.Credentials.from_service_account_file(app_config.FIREBASE_ADMIN_CREDENTIALS)
gcp_firestore_db = firestore.Client(credentials=gcp_credentials)


"""
    Pyrebase Config and Initialization
"""
config = {
    "apiKey": app_config.FIREBASE_API_KEY,
    "authDomain": app_config.FIREBASE_AUTH_DOMAIN,
    "databaseURL": "",  # Required to bypass Pyrebase error since we aren't using Firebase Realtime Database
    "storageBucket": app_config.FIREBASE_CLOUD_STORAGE_BUCKET
}

firebase = pyrebase.initialize_app(config)
pyre_auth = firebase.auth()
pyre_cloud_storage = firebase.storage()