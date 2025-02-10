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
    check_password_strength,
    check_email_exists

    # These functions need to be updated, modified, or deleted so they will be commented out for now.
    # update_user_last_logged_in,
    # update_user_last_logged_out,
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

        if check_email_exists(email):
            abort(400, "Account already exists, please log in.")

        if not email or not password:
            abort(400, "Email and password are required.")

        if not check_password_strength(password):
            abort(400, "Password is not strong enough.")

        user = create_account(email, password)
        logged_in_user = log_in(email, password)

        if logged_in_user:
            session["firebase_token"] = logged_in_user["idToken"]
            return {"message": "User created successfully."}, 200
        else:
            abort(400, "Sign-in failed after user creation.")


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

        if not check_email_exists(email):
            abort(400, "Account does not exist, please sign up.")

        try:
            user = log_in(email, password)
            session["firebase_token"] = user["idToken"]
            return {"message": "User logged in successfully."}, 200
        except Exception as e:
            logging.error(f"Unexpected error during login: {e}")
            abort(400, "Invalid credentials, please try again.")


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
        #TODO: Add a check if the email exists or not.
    """
    def post(self):
        data = request.json

        email = data.get("email")

        if not check_email_exists(email):
            abort(400, "Account does not exist, you cannot reset password.")

        try:
            send_password_reset(email)
            return {"message": "Reset password email has been sent."}, 200
        except Exception as e:
            logging.error(f"Unexpected error during login: {e}")
            abort(500, "An unexpected error occurred. Please try again.")