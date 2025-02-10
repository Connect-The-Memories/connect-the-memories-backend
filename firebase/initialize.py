import pyrebase
import firebase_admin

from firebase_admin import auth, credentials, firestore
from config import app_config


"""
    Firebase Admin Credentials and Initialization
"""
cred = credentials.Certificate(app_config.FIREBASE_ADMIN_CREDENTIALS)
firebase_admin.initialize_app(cred)

firestore_db = firestore.client()
# TODO: Initialize storage

"""
    Pyrebase Config and Initialization
"""
config = {
    "apiKey": app_config.FIREBASE_API_KEY,
    "authDomain": app_config.FIREBASE_AUTH_DOMAIN,
    "databaseURL": "", "storageBucket": "" # Required to bypass Pyrebase error since we aren't using Pyrebase for database access.
}

firebase = pyrebase.initialize_app(config)
pyre_auth = firebase.auth()