from flask import Flask
from flask_cors import CORS

from auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "SUPER_SECRET_KEY"
    CORS(app)

    app.register_blueprint(auth_bp, url_prefix="/api")

    return app

if __name__ == '__main__':
    app = create_app()
    # app.run(debug=True)