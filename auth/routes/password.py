# /auth/routes/password.py
from flask import request, jsonify, make_response, g, abort
from flask_restx import Resource

from .. import auth_ns
from ..services import send_password_reset

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