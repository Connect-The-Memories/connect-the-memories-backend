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

def get_user_data(user_id: str) -> dict:
    """
        Given a user ID, retrieves the user's data from Firestore.
    """
    user_data = firestore_db.collection("users").document(user_id).get()
    if not user_data.exists:
        raise ValueError("User data does not exist in the database.")
    
    return user_data.to_dict()

"""
    Firestore Service Function(s)
"""
def store_messages(support_user_id: str, message: str) -> str:
    """
        Stores support user uploaded messages in Firestore.
        #TODO: Work on figuring out how to store the messages in the main user's database instead of the support user's database. 
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
        "main_user_id": user_id, 
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

        main_user_id = data["main_user_id"]

        if datetime.now(tz=timezone.utc) > expires_at:
            return False, "OTP has expired."

        link_id = f"{main_user_id}_{support_user_id}"

        link_exists = firestore_db.collection("user_links").document(link_id).get().exists

        if link_exists:
            return False, "Users are already linked."

        main_user_data = get_user_data(main_user_id)
        main_user_full_name = f"{main_user_data['first_name']} {main_user_data['last_name']}"
        support_user_data = get_user_data(support_user_id)
        support_user_full_name = f"{support_user_data['first_name']} {support_user_data['last_name']}"

        firestore_db.collection("user_links").document(link_id).set({
            "main_user": main_user_id,
            "main_user_full_name": main_user_full_name,
            "support_user": support_user_id,
            "support_user_full_name": support_user_full_name,
            "linked_at": datetime.now(tz=timezone.utc)
        }, merge=True)

        firestore_db.collection("one_time_codes").document(main_user_id).delete()

        return True, "User linked successfully."

    return False, "OTP is invalid."

def get_linked_users(user_id: str):
    """
        Given a user ID, retrieves the linked users from Firestore. The linked users are stored in a dictionary where the key is the user's full name and the value is the user's ID.
    """

    user = firestore_db.collection("users").document(user_id).get()
    if not user.exists:
        raise ValueError("User data does not exist in the database.")
    
    user_data = user.to_dict()
    user_type = user_data["account_type"]

    linked_users = {}

    if user_type == "main":
        user_links = firestore_db.collection("user_links").where("main_user", "==", user_id).stream()

        for link in user_links:
            link_data = link.to_dict()
            linked_users[link_data["support_user_full_name"]] = link_data["support_user"]

    elif user_type == "support":
        user_links = firestore_db.collection("user_links").where("support_user", "==", user_id).stream()

        for link in user_links:
            link_data = link.to_dict()
            linked_users[link_data["main_user_full_name"]] = link_data["main_user"]
        
    else:
        raise ValueError("User account type is invalid.")

    return linked_users