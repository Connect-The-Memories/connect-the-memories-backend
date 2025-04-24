import re

"""
    Utility functions for validating inputs.
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

def check_valid_email(email: str) -> bool:
    """
        Check if the email is valid.
    """
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None