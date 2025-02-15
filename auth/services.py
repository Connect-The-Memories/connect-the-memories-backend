from datetime import datetime
import logging
import re

from firebase_admin import auth
from firebase.initialize import pyre_auth

"""
    Import Firebase Admin Helper Functions
"""
from firebase.helper_functions import check_email_exists, verify_user_token


"""
    Helper Functions
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

def format_dob(dob: str) -> str:
    """
        Convert date of birth to both YYYY-MM-DD for showing the user in the future and MMDDYY for simple 2FA.
    """
    try:
        date_obj = datetime.strptime(dob, "%Y-%m-%d")
        return date_obj, date_obj.strftime("%m%d%y")
    except ValueError:
        logging.error("Error in converting DoB to correct format.")
        raise ValueError("Invalid DoB format.")


"""
    Authentication Functions
"""
def log_in(email: str, password: str) -> str:
    """
        Attempts to sign in from email and pass. 
        If successful returns user dict of data, if not raises exception.
    """
    if not check_email_exists(email):
        raise ValueError("Account does not exist, please sign up.")

    try:
        return pyre_auth.sign_in_with_email_and_password(email, password) 
    except Exception as e:
        logging.error(f"Error during login: {e}")
        raise RuntimeError("Invalid credentials, please try again.")

def create_account(email: str, password: str) -> None:
    """
        Attempts to create a new user from email and password. Also automatically sends verification email upon creation.
        If successful returns user data, if user exists or other errors, exception is raised.
    """
    if check_email_exists(email):
        raise ValueError("Account already exists, please log in.")
    
    if not check_password_strength(password):
        raise ValueError("Password is not strong enough.")

    try:
        user = pyre_auth.create_user_with_email_and_password(email, password)

        id_token = user.get("idToken")
        if not id_token:
            raise RuntimeError("Failed to retrieve user token.")

        send_verification_email(id_token)
    except Exception as e:
        logging.error(f"Error during account creation: {e}")
        raise RuntimeError("Account creation failed. Please try again.")

def send_verification_email(idToken: str) -> None:
    """
        Sends email to verify user's email after account creation.
    """
    try:
        pyre_auth.send_email_verification(idToken)
    except Exception as e:
        logging.error(f"Error verifying email: {e}")
        raise RuntimeError("Unable to send verification email. Please try again.")
    

def send_password_reset(email: str) -> None:
    """
        Send a password reset email.
        Raises an exception on failure.
    """
    if not check_email_exists(email):
        raise ValueError("Account does not exist, you cannot reset password.")

    try:
        pyre_auth.send_password_reset_email(email)
    except Exception as e:
        logging.error(f"Error during login: {e}")
        raise RuntimeError("Unable to send reset email. Please try again.")

def delete_account(firebase_token: str) -> None:
    """
        Attempts to delete an account based on the firebase token, user has to be logged in already for this.
    """
    try:
        pyre_auth.delete_user_account(firebase_token)
    except Exception as e:
        logging.error(f"Error deleting account: {e}")
        raise RuntimeError("Account deletion failed. Please try again.")
