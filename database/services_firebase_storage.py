import mimetypes
import os
from datetime import datetime, timedelta

from firebase.initialize import pyre_cloud_storage, bucket
from .services_helper_functions import store_upload_metadata, get_user_media


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


def upload_file(main_user_id: str, support_user_id: str, support_user_name: str, support_user_firebase_token: str, file_path: str, original_file_name: str, description: str, date: str) -> None:
    """
        Given a user ID and file path, uploads the file to Firebase Cloud Storage.
    """

    try:
        file_type = get_file_type(file_path)
        file_ext = os.path.splitext(file_path)[1]

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{timestamp}{file_ext}"
        destination_path = f"{main_user_id}/{file_name}"

        pyre_cloud_storage.child(destination_path).put(file_path, support_user_firebase_token)

        metadata = {
            "support_user_name": support_user_name,
            "support_user_id": support_user_id,
            "main_user_id": main_user_id,
            "original_file_name": original_file_name,
            "description": description,
            "destination_path": destination_path,
            "file_type": file_type,
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "approx_date_taken": datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
        }

        store_upload_metadata(metadata)

    except Exception as e:
        raise RuntimeError(f"Error uploading file: {e}")

def generate_signed_urls(user_id: str, expiration=30) -> dict:
    """
        Given a user ID, generates signed URLs for all images in the user's uploads. Signed URLs expire after 30 minutes.
    """
    try:
        media = get_user_media(user_id)

        signed_urls = []
        for file in media:
            blob = bucket.blob(file['destination_path'])
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=expiration),
                method="GET"
            )
            signed_urls.append({
                "support_user_name": file['support_user_name'],
                "signed_url": signed_url
            })

        return signed_urls

    except Exception as e:
        raise RuntimeError(f"Error generating signed URLs: {e}")