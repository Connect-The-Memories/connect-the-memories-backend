from datetime import datetime, timedelta, timezone
import random

from google.cloud import firestore


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
            "created_at": datetime.now(timezone.utc),
            "last_login": datetime.now(timezone.utc)
        })
    except Exception as e:
        raise RuntimeError(f"Error creating user data: {e}")

"""
    Firestore Service Function(s)
"""
def store_messages(support_user_id: str, message: str) -> str:
    """
        Stores support user uploaded messages in Firestore.
        #TODO: Work on figuring out how to store the messages in the primary user's database instead of the support user's database. 
    """
    
    
    user_ref = firestore_db.collection("users").document(user_id).collection("messages")
    doc_ref = user_ref.add({**message, "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d")})
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

def generate_otp(user_id: str) -> str:
    """
        Generates a 6-digit OTP for the user and stores it in Firestore.
    """
    otp = str(random.randint(100000, 999999))

    expiration_date = datetime.now(tz=timezone.utc) + timedelta(minutes=5)

    otp_ref = firestore_db.collection("one_time_codes").document(user_id)
    otp_ref.set({
        "otp": otp, 
        "primary_user_id": user_id, 
        "expires_at": expiration_date
    })
    return otp

def validate_otp(support_user_id: str, entered_otp: str) -> tuple[bool, str]:
    """
        Validates an OTP and links the support user if the OTP is correct and not expired.
    """
    otp_ref = firestore_db.collection("one_time_codes").where("otp", "==", str(entered_otp)).stream()

    docs = list(otp_ref)
    if not docs:
        return False, "OTP is invalid."

    for doc in docs:
        data = doc.to_dict()
        expires_at = data["expires_at"]
        if hasattr(expires_at, 'to_datetime'):
            expires_at = expires_at.to_datetime()

        primary_user_id = data["primary_user_id"]

        if datetime.now(tz=timezone.utc) > expires_at:
            return False, "OTP has expired."

        link_id = f"{primary_user_id}_{support_user_id}"

        link_exists = firestore_db.collection("user_links").document(link_id).get().exists

        support_user_doc = firestore_db.collection("users").document(primary_user_id).collection("support_users").document(support_user_id).get()
        subcollection_exists = support_user_doc.exists

        if link_exists or subcollection_exists:
            return False, "Users are already linked."

        firestore_db.collection("user_links").document(link_id).set({
            "primary_user": primary_user_id,
            "support_user": support_user_id,
            "linked_at": datetime.now(tz=timezone.utc)
        }, merge=True)
    
        firestore_db.collection("users").document(primary_user_id).collection("support_users").document(support_user_id).set({
            "linked_at": datetime.now(timezone.utc),
            "status": "active"
        }, merge=True)

        firestore_db.collection("one_time_codes").document(primary_user_id).delete()

        return True, "User linked successfully."

    return False, "OTP is invalid."