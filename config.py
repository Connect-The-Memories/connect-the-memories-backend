import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask nvironment Variables
    SECRET_KEY = os.getenv("SECRET_KEY", "defaul_secret_key")
    DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "t"]

    # FireBase Environment Variables
    FIREBASE_ADMIN_CREDENTIALS = os.getenv("FIREBASE_ADMIN_CREDENTIALS", "")
    FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
    FIREBASE_AUTH_DOMAIN = os.getenv("FIREBASE_AUTH_DOMAIN", "")
    # FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL", "")
    # FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", "")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config_name = os.getenv("FLASK_ENV", "development").lower()
if config_name == "production":
    app_config = ProductionConfig()
else:
    app_config = DevelopmentConfig()