from flask import Blueprint, request, session
from flask_restx import Api, Namespace, Resource, abort

"""
    Import functions from services for user management and models for input specifications
"""
from .services import (
    sign_in,
    sign_up,
    send_password_reset,
    check_password_strength

    # These functions need to be updated, modified, or deleted so they will be commented out for now.
    # update_user_last_logged_in,
    # update_user_last_logged_out,
    # get_user_data,
    # set_user_data,
)

from .models import create_login_model, create_signup_model

"""
    Declare blueprint, api, and namespace for authentication backend endpoints.
"""
auth_bp = Blueprint("auth_bp", __name__)
auth_api = Api(auth_bp, version="1.0", title="Authentication API", description="Endpoints for user authentication of React Frontend")
auth_ns = Namespace("auth", description="Authentication Endpoints")

"""
    Flask RESTX routes
"""

signup_input = create_signup_model(auth_ns)

@auth_ns.route('signup')
class Signup(Resource):
    """
        Signup route to create a new user based on the "signup" model as input
    """
    @auth_ns.expect(signup_input, validate=True)
    def post(self):
        data = request.json

        email = data.get("email")
        password = data.get("password")
        birthday = data.get("birthday")
        account_type = data.get("account_type")

        if not check_password_strength(password):
            abort(400, "Password is not strong enough.")

        sign_up(email, password)
        user = sign_in(email, password)

            










# @auth_bp.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("pass")
#         try:
#             user = sign_in(email, password)  # from services.py
#             session["is_logged_in"] = True
#             session["email"] = user["email"]
#             session["uid"] = user["localId"]

#             # Fetch user data from RTDB
#             data = get_user_data(session["uid"])
#             if data:
#                 session["name"] = data.get("name", "User")
#                 # Update last logged in time
#                 update_user_last_logged_in(session["uid"])
#             else:
#                 session["name"] = "User"

#             # redirect to some "welcome" route in your main app
#             return redirect(url_for("welcome"))  

#         except Exception as e:
#             print("Error occurred: ", e)
#             flash("Login failed. Please try again.")
#             return redirect(url_for("auth.login"))

#     return render_template("login.html")


# @auth_bp.route("/signup", methods=["GET"])
# def signup():
#     return render_template("signup.html")


# @auth_bp.route("/register", methods=["POST", "GET"])
# def register():
#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("pass")
#         name = request.form.get("name")
#         bday_str = request.form.get("birthday")

#         # Example: Convert or format birthday if needed
#         try:
#             date_obj = datetime.strptime(bday_str, "%Y-%m-%d")
#             formatted_bday = date_obj.strftime("%y%m%d")  
#             print("Formatted birthday:", formatted_bday)
#         except ValueError:
#             flash("Invalid birthday format")
#             return redirect(url_for("auth.signup"))

#         # Check password strength
#         if not check_password_strength(password):
#             flash("Password does not meet strength requirements")
#             return redirect(url_for("auth.signup"))

#         try:
#             sign_up(email, password)
#             user = sign_in(email, password)  # log in the user right away

#             session["is_logged_in"] = True
#             session["email"] = user["email"]
#             session["uid"] = user["localId"]
#             session["name"] = name

#             # Save user data to RTDB
#             data = {
#                 "name": name,
#                 "email": email,
#                 "last_logged_in": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
#             }
#             set_user_data(session["uid"], data)

#             return redirect(url_for("welcome"))
#         except Exception as e:
#             print("Error occurred during registration: ", e)
#             flash("Registration failed. Please try again.")
#             return redirect(url_for("auth.signup"))
#     else:
#         # If GET, just redirect or render signup again
#         return redirect(url_for("auth.signup"))


# @auth_bp.route("/reset_password", methods=["GET", "POST"])
# def reset_password():
#     if request.method == "POST":
#         email = request.form.get("email")
#         try:
#             send_password_reset(email)
#             return render_template("reset_password_done.html")
#         except Exception as e:
#             print("Error occurred:", e)
#             flash("An error occurred. Please try again.")
#             return render_template("reset_password.html")
#     return render_template("reset_password.html")


# @auth_bp.route("/logout")
# def logout():
#     uid = session.get("uid")
#     if uid:
#         update_user_last_logged_out(uid)

#     session.clear()
#     return redirect(url_for("auth.login"))
