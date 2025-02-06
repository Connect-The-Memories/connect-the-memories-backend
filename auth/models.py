from flask_restx import Namespace, fields

"""
    Setup Authentication user models for auth namespace to ensure correct user and frontend inputs to the backend.
"""
def create_account_model(namespace: Namespace):
    return namespace.model('SignupModel', {
        "email": fields.String(required=True, min_length=3, max_length=64),
        "password": fields.String(required=True, min_length=8, max_length=32),
        "birthday": fields.Date(required=False),
        "account_type": fields.String(required=False)
        })

def logging_in_model(namespace: Namespace):
    return namespace.model('LoginModel', {
        "email": fields.String(required=True, min_length=3, max_length=64),
        "password": fields.String(required=True, min_length=8, max_length=32),
        })