import os

from flask import Flask
from flask_cors import CORS

from auth import auth_bp
from database import database_bp

from config import app_config

def create_app():
    app = Flask(__name__)
    app.config.from_object(app_config)
    
    CORS(app, supports_credentials=True, origins=app_config.FRONTEND_URL, allow_headers=["Content-Type", "Authorization"])

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
