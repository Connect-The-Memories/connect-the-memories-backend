# /auth/routes/session.py
from datetime import datetime
from flask import request, jsonify, make_response, g, abort
from flask_restx import Resource

from .. import auth_ns, logging_in_input
from ..services import log_in
from firebase.initialize import firestore_db
from utils.decorators import token_required

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
        return make_response(jsonify({"message": "User has been logged out successfully."}), 200)