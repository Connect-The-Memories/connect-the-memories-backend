# /auth/models.py
from flask_restx import Namespace, fields

# Setup Authentication user models for auth namespace to ensure correct user and frontend inputs to the backend
def create_account_model(namespace: Namespace):
    return namespace.model('SignupModel', {
        "first_name": fields.String(required=True, min_length=1, max_length=32),
        "last_name": fields.String(required=True, min_length=1, max_length=32),
        "email": fields.String(required=True, min_length=3, max_length=64),
        "password": fields.String(required=True, min_length=8, max_length=32),
        "dob": fields.Date(required=True),
        "account_type": fields.String(required=True)
        })

def logging_in_model(namespace: Namespace):
    return namespace.model('LoginModel', {
        "email": fields.String(required=True, min_length=3, max_length=64),
        "password": fields.String(required=True, min_length=8, max_length=32),
        "dob": fields.Date(required=False) # Optional for now, but will be required for 2FA once that is implemented.
        })