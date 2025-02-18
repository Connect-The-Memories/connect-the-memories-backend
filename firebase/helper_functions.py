import logging

from firebase_admin import auth


"""
    Firebase Admin Helper Functions
"""
def check_email_exists(email: str) -> bool:
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

def verify_user_token(firebase_token: str) -> bool:
    """
        Given a firebase token, verifies if the token is valid.
    """
    try:
        decoded_token = auth.verify_id_token(firebase_token)
        return True, decoded_token
    except Exception as e:
        logging.error(f"Error verifying user token: {e}")
        return False