from flask import Flask
from flask_cors import CORS

from auth import auth_bp

from config import app_config

def create_app():
    app = Flask(__name__)
    app.config.from_object(app_config)
    CORS(app, supports_credentials=True, origins=app.config["FRONTEND_URL"])

    app.register_blueprint(auth_bp, url_prefix="/api")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.config["DEBUG"])