from flask import Blueprint, request, session
from flask_restx import Api, Namespace, Resource, abort


"""
    Declare blueprint, api, and namespace for database access backend endpoints.
"""
database_bp = Blueprint("database_bp", __name__)
database_api = Api(database_bp, version="1.0", title="Database API", description="Endpoints for database access of React Frontend")
database_ns = Namespace("database", description="Database Endpoints")
database_api.add_namespace(database_ns)


"""
    Flask RestX routes
    TODO: Create the routes based:
    - after the user exits out of an exercise, regardless of completion, save exercise data to the database.
    - 
"""