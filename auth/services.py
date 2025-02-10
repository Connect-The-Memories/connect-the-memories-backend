import re
import logging

from firebase_admin import auth
from firebase.initialize import pyre_auth

"""
    Helper function for checking password strength
"""
def check_password_strength(password: str) -> bool:
    """
        Check if the password meets certain complexity requirements:
        - At least one lowercase
        - At least one uppercase
        - At least one digit
        - At least one special character
        - Minimum length of 8
    """
    pattern = r'^(?=.*\d)(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z]).{8,}$'
    return re.match(pattern, password) is not None


"""
    Authentication functions to be used in routes
"""
def log_in(email: str, password: str):
    """
        Attempts to sign in from email and pass. 
        If successful returns user dict of data, if not raises exception.
    """
    return pyre_auth.sign_in_with_email_and_password(email, password)

def create_account(email: str, password: str):
    """
        Attempts to create a new user from email and password. 
        If successful returns user data, if user exists or other errors, exception is raised.
    """
    return pyre_auth.create_user_with_email_and_password(email, password)

def send_password_reset(email: str):
    """
        Send a password reset email.
        Raises an exception on failure.
    """
    return pyre_auth.send_password_reset_email(email)


"""
    Firebase Admin Functions to check account existence
"""
def check_email_exists(email: str):
    """
        Given email, checks whether or not it exists in the Firebase system.
    """
    try:
        user = auth.get_user_by_email(email)
        return True
    except auth.UserNotFoundError:
        return False
    except Exception as e:
        logging.error(f"Unexpected error during login: {e}")
        return False

"""
    Code written from example online, will modify when needed.
    #TODO: Modify/Delete code once needed
"""
# def get_user_data(uid: str):
#     """
#     Fetch user data from RTDB. Returns dict or None if user not found.
#     """
#     user_data = db.child("users").child(uid).get().val()
#     return user_data

# def set_user_data(uid: str, data: dict):
#     """
#     Write user data to RTDB under 'users/<uid>'.
#     """
#     db.child("users").child(uid).set(data)
