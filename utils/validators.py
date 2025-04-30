import json
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

"""
    Utility functions for validating outputs (e.g., generated AI content).
"""
def validate_ai_content(content: str) -> json:
    """
        Validate AI-generated content.
        - Check if the content is not empty.
        - Converts the content to json.
    """
    match = re.search(r':\s*"(.*)"', content, re.DOTALL)
    
    if not content or not match:
        raise ValueError("Invalid AI content format.")
    else:
        content_string = match.group(1)

        json_string = content_string.strip()
        if json_string.startswith("```json"):
            json_string = json_string[len("```json") :]
        if json_string.endswith("```"):
            json_string = json_string[: -len("```")]
        json_string = json_string.strip()

        try:
            json_object = json.loads(json_string)
            if not isinstance(json_object, dict):
                raise ValueError("Invalid JSON format.")
            return json_object
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON: {e}")