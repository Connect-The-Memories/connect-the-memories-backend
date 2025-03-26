"""
    This file contains helper functions that are used in either file but must be stored here to prevent circular imports.
"""
from google.cloud import firestore
from datetime import timedelta

from firebase.initialize import firestore_db, gcp_firestore_db, bucket

"""
    Firestore Helper Functions
"""
def store_upload_metadata(metadata: dict) -> None:
    """
        Given metadata, stores the metadata in Firestore.
    """
    try:
        main_user_id = metadata['main_user_id']

        user_ref = gcp_firestore_db.collection("uploads").document(main_user_id)
        upload_ref = user_ref.collection("user_uploads")

        transaction = gcp_firestore_db.transaction()

        @firestore.transactional
        def transaction_function(transaction):
            snapshot = user_ref.get(transaction=transaction)
            media_counter = snapshot.get("media_counter") or 0

            metadata['media_index'] = media_counter

            transaction.set(user_ref, {"media_counter": media_counter + 1}, merge=True)

            upload_ref.add(metadata)

        transaction_function(transaction)       

    except Exception as e:
        raise RuntimeError(f"Error storing upload metadata: {e}")

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


"""
    Firebase Storage Helper Functions
"""
def generate_per_file_signed_url(media: dict, expiration=1) -> str:
    """
        Given a media file, generates a signed URL for the file. Signed URLs expire after 30 minutes.
    """
    try:
        blob = bucket.blob(media['destination_path'])
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(days=expiration),
            method="GET"
        )
        return signed_url
    except Exception as e:
        raise RuntimeError(f"Error generating signed URL: {e}")