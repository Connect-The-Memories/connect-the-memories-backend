import mimetypes
import os
from datetime import datetime

from firebase.initialize import pyre_cloud_storage
from .services_firestore import store_upload_metadata


"""
    Firebase Cloud Storage Helper Function(s)
"""
def get_file_type(file_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type is None:
        raise ValueError("Invalid file type.")
    
    image_types = ["image/apng", "image/png", "image/avif", "image/gif", "image/jpeg", "image/svg+xml", "image/webp"]
    video_types = ["video/mp4", "video/quicktime", "video/mpeg", "video/webm"]
    text_types = ["text/plain", "application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

    if mime_type in image_types:
        return "image"
    elif mime_type in video_types:
        return "video"
    elif mime_type in text_types:
        return "text"
    else:
        return "other"


def upload_file(user_id: str, file_path: str) -> str:
    """
        Given a user ID and file path, uploads the file to Firebase Cloud Storage.
    """

    try:
        file_type = get_file_type(file_path)
        file_ext = os.path.splitext(file_path)[1]

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{timestamp}{file_ext}"
        destination_path = f"{user_id}/{file_name}"

        # TODO: Instead of using supp user's ID, just store straight into main user's db.
        pyre_cloud_storage.child(destination_path).put(file_path, user_id)
        file_url = pyre_cloud_storage.child(destination_path).get_url(user_id)

        # TODO: Fix obtaining metadata
        metadata = {
            "support_user_id": user_id,
            "support_user_name": "Support User",
            "main_user_id": "main_user_id",
            "file_url": file_url,
            "file_type": file_type,
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        store_upload_metadata(metadata)

        return file_url
    except Exception as e:
        raise RuntimeError(f"Error uploading file: {e}")