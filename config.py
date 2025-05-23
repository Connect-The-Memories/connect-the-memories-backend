import os
from google.cloud import secretmanager
from dotenv import load_dotenv

is_local = not os.getenv("GOOGLE_CLOUD_PROJECT")

# Load local .env file if running locally
if not os.getenv("GOOGLE_CLOUD_PROJECT"):  # This variable is auto-set on Cloud Run
    print("Running locally: Loading .env file")
    load_dotenv()

def get_secret(secret_name, default_value=""):
    """Fetch secrets from Google Secret Manager only if running in Cloud Run."""
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    
    if is_local:  # If running locally, return .env value
        return os.getenv(secret_name, default_value)

    try:
        client = secretmanager.SecretManagerServiceClient()
        secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        
        response = client.access_secret_version(request={"name": secret_path})
        return response.payload.data.decode("UTF-8").strip()
    except Exception as e:
        print(f"Warning: Could not load secret {secret_name}, using default. Error: {e}")
        return os.getenv(secret_name, default_value)  # Fallback to local .env variable

# Load Secrets (Only When in Cloud Run)
if is_local:
    print("Loading secrets locally from .env")
else:
    print("Running in Cloud Run: Fetching secrets from Secret Manager")
    os.environ["SECRET_KEY"] = get_secret("SECRET_KEY", "default_secret")
    os.environ["DEBUG"] = get_secret("DEBUG", "False")
    os.environ["FIREBASE_API_KEY"] = get_secret("FIREBASE_API_KEY", "")
    os.environ["FIREBASE_AUTH_DOMAIN"] = get_secret("FIREBASE_AUTH_DOMAIN", "")
    os.environ["FIREBASE_CLOUD_STORAGE_BUCKET"] = get_secret("FIREBASE_CLOUD_STORAGE_BUCKET", "")
    os.environ["FIREBASE_PROJECT_ID"] = get_secret("FIREBASE_PROJECT_ID", "")
    os.environ["FRONTEND_URL"] = get_secret("FRONTEND_URL", "http://localhost:3000")
    os.environ["FLASK_ENV"] = get_secret("FLASK_ENV", "development")
# Flask Config
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
    DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "t"]
    FIREBASE_ADMIN_CREDENTIALS = os.getenv("FIREBASE_ADMIN_CREDENTIALS", "")
    FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
    FIREBASE_AUTH_DOMAIN = os.getenv("FIREBASE_AUTH_DOMAIN", "")
    FIREBASE_CLOUD_STORAGE_BUCKET = os.getenv("FIREBASE_CLOUD_STORAGE_BUCKET", "")
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    # Default session cookie settings (can be overridden)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False # Default to False, override in Prod
    SESSION_COOKIE_SAMESITE = 'Lax' # Default to Lax

class DevelopmentConfig(Config):
    DEBUG = True
    # Session Cookie Settings
    SESSION_COOKIE_SECURE = False 
    SESSION_COOKIE_SAMESITE = 'Lax' 

class ProductionConfig(Config):
    DEBUG = False
    # Session Cookie Settings
    SESSION_COOKIE_SECURE = True  # Send cookie only over HTTPS
    SESSION_COOKIE_HTTPONLY = True # Prevent client-side JS access
    SESSION_COOKIE_SAMESITE = 'None'  # CSRF protection

config_name = os.getenv("FLASK_ENV", "development").lower()
app_config = ProductionConfig() if config_name == "production" else DevelopmentConfig()
