from firebase.initialize import firestore_db

"""
    Firestore Helper Function(s)
"""
def delete_user_data(user_token: str) -> None:
    """
        Given a firebase token, deletes the user's data from Firestore.
    """
    try:
        firestore_db.collection("users").document(user_token).delete()
    except Exception as e:
        raise RuntimeError(f"Error deleting user data: {e}")