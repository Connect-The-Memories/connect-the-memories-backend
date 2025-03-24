from datetime import datetime, timedelta, timezone
import random


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

def store_upload_metadata(metadata: dict) -> None:
    """
        Given metadata, stores the metadata in Firestore.
    """
    try:
        main_user_id = metadata['main_user_id']

        user_ref = firestore_db.collection("uploads").document(main_user_id)
        upload_ref = user_ref.collection("user_uploads")

        def transaction_function(transaction):
            snapshot = user_ref.get(transaction=transaction)
            media_counter = snapshot.get("media_counter") or 0

            metadata['media_index'] = media_counter

            transaction.set(user_ref, {"media_counter": media_counter + 1}, merge=True)

            upload_ref.add(metadata)

        firestore_db.run_transaction(transaction_function)         

    except Exception as e:
        raise RuntimeError(f"Error storing upload metadata: {e}")

"""
    Firestore Service Function(s)
"""
def store_messages(support_full_name: str, main_user_id: str, messages: list[str]) -> list[str]:
    """
        Given user id and array of messages, batch store the messages in Firestore using batch writes.
    """
    user_ref = firestore_db.collection("users").document(main_user_id).collection("messages")

    batch = firestore_db.batch()

    doc_id = []

    for msg in messages:
        doc_ref = user_ref.document()
        batch.set(doc_ref, {
            "support_full_name": support_full_name,
            "message": msg,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d")
            })
        doc_id.append(doc_ref.id)
    
    batch.commit()

    return doc_id

def retrieve_messages(user_id: str) -> tuple:
    """
        Retrieves support user uploaded messages from Firestore.
    """
    user_ref = firestore_db.collection("users").document(user_id).collection("messages")
    
    query = user_ref.order_by("timestamp", direction="DESCENDING")

    messages = query.stream()

    message_list = []

    for message in messages:
        message_dict = message.to_dict()
        message_list.append({
            "support_full_name": message_dict["support_full_name"],
            "message": message_dict["message"],
            "timestamp": message_dict["timestamp"]
        })

    return message_list

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
        """
        Additional logic for if the main user requires easy query for support users.
        support_user_data = get_user_data(support_user_id)
        support_user_full_name = f"{support_user_data['first_name']} {support_user_data['last_name']}"
        """

        firestore_db.collection("user_links").document(link_id).set({
            "main_user": main_user_id,
            "support_user": support_user_id,
            "linked_at": datetime.now(tz=timezone.utc)
        })

        supp_user_ref = firestore_db.collection("users").document(support_user_id)
        supp_user_ref.set({
            "linked_users": {
                main_user_full_name: main_user_id
            }
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
    return user_data.get("linked_users", {})

def get_verified_uid_from_user_name(support_user_uid: str, user_name: str) -> str:
    """
        Given a the full name of a user from the frontend, retrieve the internal UID from firestore.
    """
    if support_user_uid is None:
        raise ValueError("Unauthorized. Please log in and try again.")
    
    if user_name is None:
        raise ValueError("User name is required.")
    
    linked_accounts = get_linked_users(support_user_uid)

    if user_name not in linked_accounts:
        raise ValueError("User not linked to support user.")
    
    return linked_accounts[user_name]

def verify_user_link(support_user_uid: str, main_user_id: str) -> bool:
    """
        Given a support user ID and a main user ID, verifies if the user is linked.
    """
    link_id = f"{main_user_id}_{support_user_uid}"
    link_exists = firestore_db.collection("user_links").document(link_id).get().exists

    return link_exists

# TODO: Implement pagination for user images if needed.
def get_user_media(user_id: str):
    """
        Given a user ID, retrieves the user's images from Firestore.
    """
    collection_ref = firestore_db.collection("uploads").document(user_id).collection("user_uploads")

    query = collection_ref.order_by("uploaded_at", direction="DESCENDING")

    results = query.stream()

    media = []
    for doc in results:
        data = doc.to_dict()
        media.append({
            "destination_path": data["destination_path"],
            "support_user_name": data["support_user_name"],
        })

    return media