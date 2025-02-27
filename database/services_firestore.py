from datetime import datetime


"""
    Import Helper Functions
"""
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

def create_user_data(user_id: str, first_name: str, last_name: str, email: str, dob_full: str, dob_6digit: str, account_type: str) -> None:
    """
        Given user data, creates a new user document in Firestore.
    """
    try:
        firestore_db.collection("users").document(user_id).set({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "date_of_birth_full": dob_full,
            "date_of_birth_6digit": dob_6digit,
            "account_type": account_type,
            "created_at": datetime.now(),
            "last_login": datetime.now()
        })
    except Exception as e:
        raise RuntimeError(f"Error creating user data: {e}")

"""
    Firestore Service Function(s)
"""
def store_messages(user_id: str, message: str) -> str:
    """
        Stores support user uploaded messages in Firestore.
        #TODO: Work on figuring out how to store the messages in the primary user's database instead of the support user's database. 
    """
    user_ref = firestore_db.collection("users").document(user_id).collection("messages")
    doc_ref = user_ref.add({**message, "timestamp": datetime.now(datetime.UTC).strftime("%Y-%m-%d")})
    return doc_ref.id

def retrieve_messages(user_id: str, last_message_id: str = None, limit: int = 5) -> tuple:
    """
        Retrieves support user uploaded messages from Firestore.
    """
    user_ref = firestore_db.collection("users").document(user_id).collection("messages")
    
    query = user_ref.order_by("timestamp", direction="DESCENDING").limit(limit)

    if last_message_id:
        last_doc_ref = user_ref.document(last_message_id).get()
        if last_doc_ref.exists:
            query = query.start_after(last_doc_ref)

    messages = query.stream()

    message_list = []
    last_message_id = None

    for message in messages:
        message_dict = message.to_dict()
        message_dict["id"] = message.id
        message_list.append(message_dict)
        last_message_id = message.id

    return message_list, last_message_id
    