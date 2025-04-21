from functools import wraps
from flask import request, g, abort

from firebase.helper_functions import verify_user_token

def get_token_from_header():
    """
        Helper to extract Bearer token from Authorization header.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        abort(401, "Authorization header missing or invalid format (Bearer <token>).")
    try:
        token = auth_header.split("Bearer ")[1]
        if not token:
             abort(401, "Bearer token missing after 'Bearer ' prefix.")
        return token
    except IndexError:
        abort(401, "Bearer token missing after 'Bearer ' prefix.")
    except Exception as e:
        abort(401, f"Error processing Authorization header: {str(e)}")


def token_required(f):
    """
        Decorator to obtain a user's id from the token in the Authorization header.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        try:
            token = get_token_from_header()
            decoded_token = verify_user_token(token)
            if decoded_token is False or decoded_token is None or decoded_token == {}:
                abort(401, "Token is invalid, expired, or could not be decoded.")

            g.uid = decoded_token # User's local id which is specific and unchangeable
            g.firebase_token = token # Temporary token given by firebase which changes upon each login/refresh
        except Exception as e:
            error_message = str(e)
            status_code = 401 # Default to 401
            if hasattr(e, 'code') and isinstance(e.code, int):
                 status_code = e.code
            if status_code == 401:
                 abort(401, f"Token validation failed: {error_message}")
            else:
                 print(f"Unexpected error during token validation: {error_message}")
                 abort(500, "An internal error occurred during authentication.")


        return f(*args, **kwargs)
    return decorated