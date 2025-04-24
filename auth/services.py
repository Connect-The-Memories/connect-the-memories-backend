import logging

"""
    Import Helper Functions and Modules
"""
from firebase.initialize import pyre_auth
from firebase.helper_functions import check_email_exists
from utils.validators import check_password_strength, check_valid_email


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
    if password is None or email is None:
        raise ValueError("Missing email or password, please provide and try again.")

    if not check_valid_email(email):
        raise ValueError("Invalid email format. Please try again.")

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")

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
