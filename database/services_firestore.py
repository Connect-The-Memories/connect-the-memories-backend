from datetime import datetime, timedelta, timezone
import random

"""
    Import Helper Functions
"""
from firebase.initialize import firestore_db
from .services_helper_functions import generate_per_file_signed_url

from utils.formatters import iso_to_datetime

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

def get_random_indexed_media(user_id: str, visited_indices: list[int]) -> dict:
    """
        Given a user ID, retrieves a random image from the user's images that has not been visited before.
    """
    user_doc = firestore_db.collection("uploads").document(user_id).get()

    media_count = user_doc.get("media_counter") or 0
    if media_count == 0:
        raise ValueError("No media found for user.")
    
    available_indices = set(range(media_count)) - set(visited_indices)

    if not available_indices:
        raise ValueError("All media has been visited.")
    
    random_index = random.choice(list(available_indices))

    query = firestore_db.collection("uploads").document(user_id).collection("user_uploads").where("media_index", "==", random_index).limit(1)

    docs = list(query.stream())

    if not docs:
        raise ValueError("Media not found.")
    
    media = docs[0].to_dict()
    destination_path = media["destination_path"]
    signed_url = generate_per_file_signed_url(destination_path)

    required_media_data = {
        "signed_url": signed_url,
        "destination_path": destination_path,
        "approx_date_taken": media["approx_date_taken"],
        "description": media["description"],
        "media_index": media["media_index"]
    }

    return required_media_data

def store_exercise_data(exercise_name: str, timestamp: datetime, accuracy: float, avg_reaction_time: float, user_id: str) -> None:
    """
        Given exercise data, store the data in firestore for each exercise for the user.
    """
    try:
        exercise_ref = firestore_db.collection("exercises").document(exercise_name).collection("user_attempts").document(user_id).collection("attempts").document()

        exercise_data = {
            'user_id': user_id,
            'exercise_name': exercise_name,
            'timestamp': timestamp,
            'accuracy': accuracy,
            'avg_reaction_time': avg_reaction_time
        }

        exercise_ref.set(exercise_data)
    except Exception as e:
        raise RuntimeError(f"Error storing exercise data: {e}")
    
def get_exercise_data(user_id: str) -> list[dict]:
    all_attempts = []
    try:
        attempts_group_ref = firestore_db.collection_group("attempts")
        query = attempts_group_ref.where("user_id", "==", user_id).order_by("timestamp", direction="DESCENDING")

        for attempt in query.stream():
            attempt_data = attempt.to_dict()

            timestamp = attempt_data.get("timestamp")
            if hasattr(timestamp, 'to_datetime'):
                attempt_data["timestamp"] = timestamp.to_datetime().replace(tz=timezone.utc)
            elif isinstance(timestamp, datetime):
                attempt_data["timestamp"] = timestamp

            all_attempts.append(attempt_data)
        
        return all_attempts
    except Exception as e:
        raise RuntimeError(f"Error retrieving exercise data: {e}")
    
def store_journal_entries(entry: str, timestamp: datetime, destination_path: str, user_id: str) -> None:
    """
        Given journal entry data, store the data in firestore for each exercise for the user.
    """
    try:
        journal_ref = firestore_db.collection("journals").document(user_id).collection("entries").document()

        journal_data = {
            'entry': entry,
            'timestamp': timestamp,
            'destination_path': destination_path
        }

        journal_ref.set(journal_data)
    except Exception as e:
        raise RuntimeError(f"Error storing journal entry: {e}")

def get_journal_entries(user_id: str, date: datetime) -> list[dict]:
    """
        Given a user ID, retrieves the journal entries from Firestore.
    """
    try:

        if date is None:
            raise ValueError("Date is required.")
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        journal_ref = firestore_db.collection("journals").document(user_id).collection("entries")
        query = (
            journal_ref.where("timestamp", ">=", start_of_day)
            .where("timestamp", "<", end_of_day)
            .order_by("timestamp", direction="DESCENDING")
        )

        entry_list = []

        for entry in query.stream():
            entry_dict = entry.to_dict()
            timestamp = entry_dict.get("timestamp")
            if hasattr(timestamp, 'to_datetime'):
                entry_dict["timestamp"] = timestamp.to_datetime()
            elif isinstance(timestamp, datetime):
                entry_dict["timestamp"] = timestamp

            entry_dict["signed_url"] = generate_per_file_signed_url(entry_dict["destination_path"])
            
            entry_list.append(entry_dict)

        return entry_list
    except Exception as e:
        raise RuntimeError(f"Error retrieving journal entries: {e}")
    