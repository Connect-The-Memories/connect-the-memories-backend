from datetime import datetime

from flask import Blueprint, g, jsonify, make_response, request, session
from flask_restx import Api, Namespace, Resource, abort


"""
    Import functions from services for user management and models for input specifications.
"""
from .models import create_account_model, logging_in_model

from .services import (
    send_password_reset,
    log_in,
    create_account,
    delete_account
)

from database.services_firestore import create_user_data, delete_user_data, get_user_data

from firebase.initialize import firestore_db

from utils.decorators import token_required
from utils.formatters import format_dob


"""
    Declare blueprint, api, and namespace for authentication backend endpoints.
"""
auth_bp = Blueprint("auth_bp", __name__)
auth_api = Api(auth_bp, version="1.0", title="Authentication API", description="Endpoints for user authentication of React Frontend")
auth_ns = Namespace("auth", description="Authentication Endpoints")
auth_api.add_namespace(auth_ns)


"""
    Flask RestX routes (based on Flask-RESTX documentation and official example.)
"""
create_account_input = create_account_model(auth_ns)
logging_in_input = logging_in_model(auth_ns)

@auth_ns.route("/account")
class Account(Resource):
    """
        TODO: Implement routes that are listed as not implemented.
        (PUT) Route to update user account information. (Currently not implemented, will implement in future if needed.)
    """
    @auth_ns.doc("get_account")
    @token_required
    def get(self):
        """
            (GET /account) Route to retrieve user account information, primarily user's first name and list of linked users.
        """
        try:
            user_id = g.uid
            user_data = get_user_data(user_id)

            if not user_data:
                abort(400, "User data does not exist in the database.")
            
            first_name = user_data.get("first_name")

            return make_response(jsonify({
                "first_name": first_name
            }), 200)
        except ValueError as e:
            abort(400, str(e))
        except RuntimeError as e:
            abort(500, str(e))

    
    @auth_ns.expect(create_account_input)
    @auth_ns.doc("create_account")
    def post(self):
        """
            (POST /account) Route to create a new user, using the "create_account" model as input.
        """
        data = request.json

        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        password = data.get("password")
        dob = data.get("dob")
        account_type = data.get("account_type")
  
        dob_full, dob_6digit = format_dob(dob)
        
        try:
            create_account(email, password)
            user = log_in(email, password)
            idToken = user.get("idToken")
            create_user_data(user.get("localId"), first_name, last_name, email, dob_full, dob_6digit, account_type)

            return make_response(jsonify({
                "message": "User created and logged in successfully.",
                "account_type": account_type,
                "idToken": idToken
                }), 201)
        except ValueError as e:
            abort(400, str(e))
        except RuntimeError as e:
            abort(500, str(e))

    @auth_ns.doc("delete_account")
    @token_required
    def delete(self):
        """
            (DELETE /account) Route to delete user account.
        """
        try:
            firebase_token = g.firebase_token
            user_id = g.uid

            delete_account(firebase_token)
            delete_user_data(user_id)
            session.clear()
            return make_response(jsonify({}), 204)
        except RuntimeError as e:
            abort(500, str(e))


@auth_ns.route("/account/login")
class AccountLogin(Resource):
     """
        (POST /login) Route to log in a user, using the "logging_in" model as input.
     """
     @auth_ns.expect(logging_in_input, validate=True)
     @auth_ns.doc("logging_in")
     def post(self):
        data = request.json

        email = data.get("email")
        password = data.get("password")
        # dob_input = data.get("dob")
        # _, dob_6digit = format_dob(dob_input)

        try:
            user = log_in(email, password)
            idToken = user.get("idToken")
  
            user_data = firestore_db.collection("users").document(user.get("localId"))
            user_data_snapshot = user_data.get()
            if not user_data_snapshot.exists:
                abort(400, "User data does not exist in the database.")

            user = user_data_snapshot.to_dict()
            # stored_dob_6digit = user.get("date_of_birth_6digit")
            stored_account_type = user.get("account_type")

            # if dob_6digit != stored_dob_6digit:
            #     abort(400, "Verification using date of birth failed.")

            user_data.update({
                "last_login": datetime.now()
            })
            return make_response(jsonify({
                "message": "User logged in successfully.",
                "account_type": stored_account_type,
                "idToken": idToken
                }), 200)
        except ValueError as e:
            abort(400, str(e))
        except RuntimeError as e:
            abort(500, str(e))


@auth_ns.route("/account/logout")
class AccountLogout(Resource):
    """
        (POST /account/logout) Route to log out a user.
    """
    @auth_ns.doc("logout")
    @token_required
    def post(self):
        session.clear()
        return make_response(jsonify({"message": "User has been logged out successfully."}), 200)


@auth_ns.route("/account/reset_password")
class AccountResetPassword(Resource):
    """
        (POST /account/reset_password) Route to reset a user's password.
    """
    @auth_ns.doc("reset_password")
    def post(self):
        data = request.json

        email = data.get("email")

        try:
            send_password_reset(email)
            return make_response(jsonify({"message": "Password reset email has been sent."}), 200)
        except ValueError as e:
            abort(400, str(e))
        except RuntimeError as e:
            abort(500, str(e))