import mimetypes
import os

from firebase.initialize import pyre_cloud_storage


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
        file_name = os.path.basename(file_path)
        destination_path = f"{user_id}/{file_type}/{file_name}"
        pyre_cloud_storage.child(destination_path).put(file_path, user_id)
        return file_name
    except Exception as e:
        raise RuntimeError(f"Error uploading file: {e}")