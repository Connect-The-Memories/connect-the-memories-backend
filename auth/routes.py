import logging

from flask import Blueprint, request, session
from flask_restx import Api, Namespace, Resource, abort


"""
    Import functions from services for user management and models for input specifications.
"""
from .services import (
    log_in,
    create_account,
    send_password_reset,
    delete_account

    # These functions need to be updated, modified, or deleted so they will be commented out for now.
    # get_user_data,
    # set_user_data,
)

from .models import create_account_model, logging_in_model


"""
    Declare blueprint, api, and namespace for authentication backend endpoints.
"""
auth_bp = Blueprint("auth_bp", __name__)
auth_api = Api(auth_bp, version="1.0", title="Authentication API", description="Endpoints for user authentication of React Frontend")
auth_ns = Namespace("auth", description="Authentication Endpoints")
auth_api.add_namespace(auth_ns)


"""
    Flask RESTX routes
"""
create_account_input = create_account_model(auth_ns)

@auth_ns.route('/create_account')
class CreateAccount(Resource):
    """
        Create Account route to create a new user based on the "create_account" model as input.
    """
    @auth_ns.expect(create_account_input, validate=True)
    def post(self):
        data = request.json

        email = data.get("email")
        password = data.get("password")
        """
            Temporarily will be unused, once Firestore database access is implemented, will store there.
        """
        # birthday = data.get("birthday")
        """
        Logic to convert birthday to a 6digit auth code.
        try:
            date_obj = datetime.strptime(bday_str, "%Y-%m-%d")
            formatted_bday = date_obj.strftime("%y%m%d")  
            print("Formatted birthday:", formatted_bday)
        except ValueError:
            flash("Invalid birthday format")
            return redirect(url_for("auth.signup"))
        """
        # account_type = data.get("account_type")

        try:
            create_account(email, password)
            session["firebase_token"] = log_in(email, password)
            return {"message": "User created successfully."}, 200
        except ValueError as e:
            abort(400, str(e))
        except RuntimeError as e:
            abort(500, str(e))


logging_in_input = logging_in_model(auth_ns)

@auth_ns.route('/logging_in')
class LogginIn(Resource):
    """
        Login route for the user to log in using the "logging_in" model as input.
    """
    @auth_ns.expect(logging_in_input, validate=True)
    def post(self):
        data = request.json

        email = data.get("email")
        password = data.get("password")

        try:
            session["firebase_token"] = log_in(email, password)
            return {"message": "User logged in successfully."}, 200
        except ValueError as e:
            abort(400, str(e))
        except RuntimeError as e:
            abort(500, str(e))

@auth_ns.route('/logout')
class Logout(Resource):
    """
        Logout route to end session of user.
    """
    def post(self):
        session.pop("firebase_token", None)
        return {"message": "User has been logged out successfully."}, 200


@auth_ns.route('/reset_password')
class ResetPassword(Resource):
    """
        Reset password route so that the user can reset their password given an email.
    """
    def post(self):
        data = request.json

        email = data.get("email")

        try:
            send_password_reset(email)
            return {"message": "Reset password email has been sent."}, 200
        except ValueError as e:
            abort(400, str(e))
        except RuntimeError as e:
            abort(500, str(e))


@auth_ns.route('/delete_account')
class DeleteAccount(Resource):
    """
        As long as the user is logged in, delete the account if the user wants to.
    """
    def post(self):
        try:
            firebase_token = session.get("firebase_token")
            delete_account(firebase_token)
            session.pop("firebase_token", None)
            return {"message": "Account has been deleted. You have been logged out."}, 200
        except RuntimeError     as e:
            abort(500, str(e))