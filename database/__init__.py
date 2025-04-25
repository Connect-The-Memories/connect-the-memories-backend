# /database/__init__.py
from flask import Blueprint
from flask_restx import Api, Namespace

# Blueprint, api, and namespace for authentication backend endpoints
database_bp = Blueprint("database_bp", __name__)
database_api = Api(database_bp, version="1.0", title="Database API", description="Endpoints for database access of React Frontend")
database_ns = Namespace("database", description="Database Endpoints")
database_api.add_namespace(database_ns)
