import re

from firebase.initialize import firebase_auth

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
    return firebase_auth.sign_in_with_email_and_password(email, password)

def create_account(email: str, password: str):
    """
        Attempts to create a new user from email and password. 
        If successful returns user data, if user exists or other errors, exception is raised.
    """
    return firebase_auth.create_user_with_email_and_password(email, password)

def send_password_reset(email: str):
    """
        Send a password reset email.
        Raises an exception on failure.
    """
    return firebase_auth.send_password_reset_email(email)


"""
    Code written from example online, will modify when needed.
    #TODO: Modify/Delete code once needed
"""
# def update_user_last_logged_in(uid: str):
#     """
#     Update 'last_logged_in' field in the RTDB for the given user UID.
#     """
#     now_str = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
#     db.child("users").child(uid).update({"last_logged_in": now_str})

# def update_user_last_logged_out(uid: str):
#     """
#     Update 'last_logged_out' field in the RTDB for the given user UID.
#     """
#     now_str = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
#     db.child("users").child(uid).update({"last_logged_out": now_str})

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
