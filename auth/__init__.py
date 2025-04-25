# /auth/__init__.py
from flask import Blueprint
from flask_restx import Api, Namespace

# Import models for input specifications
from .models import create_account_model, logging_in_model

# Blueprint, api, and namespace for authentication backend endpoints
auth_bp = Blueprint("auth_bp", __name__)
auth_api = Api(auth_bp, version="1.0", title="Authentication API", description="Endpoints for user authentication of React Frontend")
auth_ns = Namespace("auth", description="Authentication Endpoints")
auth_api.add_namespace(auth_ns)

# Define input models tied to the namespace
create_account_input = create_account_model(auth_ns)
logging_in_input = logging_in_model(auth_ns)

# Import route files after defining the namespace
from .routes import account, session, password