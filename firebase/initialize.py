import pyrebase

from config import app_config

"""
    Firebase configuration and initialization
"""
config = {
    "apiKey": app_config.FIREBASE_API_KEY,
    "authDomain": app_config.FIREBASE_AUTH_DOMAIN,
    "databaseURL": app_config.FIREBASE_DATABASE_URL,
    "storageBucket": app_config.FIREBASE_STORAGE_BUCKET
}

firebase = pyrebase.initialize_app(config)
firebase_auth = firebase.auth()
db = firebase.database()