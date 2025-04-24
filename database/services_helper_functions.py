"""
    This file contains helper functions that are used in either file but must be stored here to prevent circular imports. Also includes additional helper functions for uploaded media analysis.
"""
from google.cloud import vision, firestore
from vertexai.generative_models import GenerativeModel, Part
from typing import Dict, Any
from datetime import datetime, timedelta
import vertexai

from firebase.initialize import firestore_db, gcp_firestore_db, bucket, vision_client
from config import app_config

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
    

"""
    Image Analysis Helper Functions
"""
vertexai.init(project=app_config.FIREBASE_PROJECT_ID, location="us-central1")


def analyze_image(gcs_uri: str, mime_type: str, description: str = "") -> Dict[str, Any]:
    """
        Analyze an image using Vision API and Vertex AI.
    """
    try:
        vision_results = analyze_with_vision(gcs_uri)
        
        vertex_results = analyze_with_vertex(gcs_uri, mime_type, description)
        
        combined_results = process_results(vision_results, vertex_results)
        
        return {
            'status': 'completed',
            'analysis': combined_results,
            'analyzed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

def analyze_with_vision(gcs_uri: str) -> Dict[str, Any]:
    """
        Analyze image with Vision API
    """
    image = vision.Image()
    image.source.image_uri = gcs_uri
    
    features = [
        vision.Feature(type_=vision.Feature.Type.OBJECT_LOCALIZATION),
        vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION, max_results=20),
        vision.Feature(type_=vision.Feature.Type.FACE_DETECTION),
        vision.Feature(type_=vision.Feature.Type.LANDMARK_DETECTION)
    ]
    
    response = vision_client.annotate_image({
        'image': image,
        'features': features,
    })
    
    result = {
        'objects': [{
            'name': obj.name,
            'confidence': obj.score,
        } for obj in response.localized_object_annotations],
        
        'labels': [{
            'description': label.description,
            'confidence': label.score
        } for label in response.label_annotations],
        
        'landmarks': [{
            'name': landmark.description,
            'confidence': landmark.score,
        } for landmark in response.landmark_annotations],
        
        'faces': [{
            'emotions': {
                'joy': face.joy_likelihood.name,
                'sorrow': face.sorrow_likelihood.name,
                'anger': face.anger_likelihood.name,
                'surprise': face.surprise_likelihood.name
            },
            'detection_confidence': face.detection_confidence,
        } for face in response.face_annotations]
    }
    
    return result

def analyze_with_vertex(gcs_uri: str, mime_type: str, description: str = "") -> str:
    """
        Analyze image with Vertex AI Gemini
    """
    model = GenerativeModel("gemini-2.0-flash-001")
    
    prompt = f"""Analyze this image in detail and provide the following information:

    1. Key Entities: List all the main people, places, and objects visible in the image.
    
    2. Scene Classification: Identify the setting/environment (examples: house interior, kitchen, bedroom, beach, mountain, forest, urban street, office, etc.)
    
    3. Activities: Describe any activities or actions being performed by people in the image (examples: cooking, reading, playing sports, working, dancing, etc.)
    
    4. People Analysis: For each person visible:
       - Estimated age range
       - Apparent emotional state
       - What they are doing
       
    Format your response as structured information with clear headings and bullet points.
    
    User provided description: "{description}"
    """
    
    image_part = Part.from_uri(uri=gcs_uri, mime_type=mime_type)

    response = model.generate_content([image_part, prompt])
    
    return response.text

def process_results(vision_results: Dict[str, Any], vertex_text: str) -> Dict[str, Any]:
    """
        Process and combine results from both APIs
    """
    combined_results = {
        'entities': {
            'objects': vision_results['objects'],
            'labels': vision_results['labels'],
            'landmarks': vision_results['landmarks'],
            'faces': vision_results['faces'],
            'total_faces': len(vision_results['faces'])
        },
        'gemini_analysis': vertex_text,
        
        'quick_access': {
            'has_people': len(vision_results['faces']) > 0,
            'primary_objects': [obj['name'] for obj in vision_results['objects'][:5]] if vision_results['objects'] else [],
            'top_labels': [label['description'] for label in vision_results['labels'][:5]] if vision_results['labels'] else [],
            'location': vision_results['landmarks'][0]['name'] if vision_results['landmarks'] else None
        }
    }
    
    scenes = []
    activities = []
    
    scene_keywords = ['indoor', 'outdoor', 'house', 'kitchen', 'living room', 'bedroom', 
                     'bathroom', 'office', 'beach', 'mountain', 'forest', 'park', 
                     'street', 'restaurant', 'cafe', 'garden']
    
    activity_keywords = ['walking', 'running', 'sitting', 'standing', 'eating', 'drinking',
                        'cooking', 'reading', 'writing', 'playing', 'working', 'exercising',
                        'swimming', 'surfing', 'skiing', 'shopping', 'dancing', 'talking']
    
    for keyword in scene_keywords:
        if keyword in vertex_text.lower():
            scenes.append(keyword)
    
    for keyword in activity_keywords:
        if keyword in vertex_text.lower():
            activities.append(keyword)
    
    combined_results['quick_access']['probable_scenes'] = scenes
    combined_results['quick_access']['probable_activities'] = activities
    
    return combined_results