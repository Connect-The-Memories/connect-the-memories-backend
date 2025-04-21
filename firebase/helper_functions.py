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
        _ = auth.get_user_by_email(email)
        return True
    except auth.UserNotFoundError:
        return False
    except Exception as e:
        logging.error(f"Unexpected error during login: {e}")
        return False

# Currently unused, might be used in the future.
def get_user_id_from_email(email: str) -> str:
    """
        Given an email, retrieves the user's ID.
    """
    try:
        user = auth.get_user_by_email(email)
        return user.uid
    except Exception as e:
        logging.error(f"Error retrieving user ID: {e}")
        return ""

def verify_user_token(firebase_token: str):
    """
        Given a firebase token, verifies if the token is valid.
    """
    try:
        decoded_user = auth.verify_id_token(firebase_token)
        decoded_token = decoded_user.get("uid")
        return decoded_token
    except Exception as e:
        logging.error(f"Error verifying user token: {e}")
        return False