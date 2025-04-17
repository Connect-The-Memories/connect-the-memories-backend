import os

from flask import Flask
from flask_cors import CORS

from auth import auth_bp
from database import database_bp

from config import app_config

def create_app():
    app = Flask(__name__)
    app.config.from_object(app_config)
    print("Security Key:", app.config["SECRET_KEY"])
    
    # Allow specific origin(s)
    origins = [app_config.FRONTEND_URL]
    # Add local dev origin if needed (check FLASK_ENV)
    if app.config.get("FLASK_ENV") == "development":
        # Assuming local frontend runs on 3000, adjust if needed
        origins.append("http://localhost:3000")

    CORS(app, supports_credentials=True, origins=origins, allow_headers=["Content-Type", "Authorization"])

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(database_bp, url_prefix="/api")

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    if os.getenv("GOOGLE_CLOUD_PROJECT"):
        # Production (Cloud Run)
        app.run(host='0.0.0.0', port=port, debug=app.config["DEBUG"])
    else:
        # Local development
        app.run(host='localhost', debug=True)
