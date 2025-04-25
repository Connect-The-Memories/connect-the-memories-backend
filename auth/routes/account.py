# /auth/routes/account.py
from flask import request, jsonify, make_response, g, abort
from flask_restx import Resource

from .. import auth_ns, create_account_input
from ..services import create_account, log_in, delete_account
from database.services_firestore import get_user_data, create_user_data, delete_user_data
from utils.decorators import token_required
from utils.formatters import format_dob

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
            return make_response(jsonify({}), 204)
        except RuntimeError as e:
            abort(500, str(e))