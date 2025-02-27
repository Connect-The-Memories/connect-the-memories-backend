from flask import Blueprint, jsonify, make_response, request, session
from flask_restx import Api, Namespace, Resource, abort

"""
    Import functions from services for database access.
"""

from .services_firestore import retrieve_messages, store_messages

from firebase.helper_functions import verify_user_token


"""
    Declare blueprint, api, and namespace for database access backend endpoints.
"""
database_bp = Blueprint("database_bp", __name__)
database_api = Api(database_bp, version="1.0", title="Database API", description="Endpoints for database access of React Frontend")
database_ns = Namespace("database", description="Database Endpoints")
database_api.add_namespace(database_ns)


"""
    Flask RestX routes
    TODO: Create the routes based:
    - after the user exits out of an exercise, regardless of completion, save exercise data to the database.
    - message uploads and retrieval
    - img/vid/txt uploads and retrieval
"""
@database_ns.route("/firestore/messages")
class Messages(Resource):
    @database_ns.doc("store_messages")
    def put(self):
        """
            (PUT /messages) Route to store messages in Firestore.
        """
        data = request.json

        message = data.get("message")

        firebase_token = session.get("firebase_token")

        if firebase_token is None:
            abort(401, {"error": "Unauthorized. Please log in and try again."})

        is_verified, decoded_user_token = verify_user_token(firebase_token)

        if not is_verified:
            abort(401, {"error": "Unauthorized. Please log in and try again."})

        try:
            doc_id = store_messages(decoded_user_token.get("uid"), message)
            return make_response(jsonify({"message_id": doc_id}), 201)
        except Exception as e:
            abort(500, {"error": f"Failed to store message: {e}"})
    
    @database_ns.doc("retrieve_messages")
    def get(self):
        """
            (GET /messages) Route to retrieve messages from Firestore.
        """
        firebase_token = session.get("firebase_token")

        if firebase_token is None:
            abort(401, {"error": "Unauthorized. Please log in and try again."})
        
        is_verified, decoded_user_token = verify_user_token(firebase_token)

        if not is_verified:
            abort(401, {"error": "Unauthorized. Please log in and try again."})

        last_message_id = request.args.get("last_message_id")
        limit = request.args.get("limit", default=5, type=int)

        try:
            messages, new_last_message_id = retrieve_messages(
                decoded_user_token.get("uid"),
                last_message_id=last_message_id,
                limit=limit
            )
            return make_response(jsonify({
                "messages": messages,
                "last_message_id": new_last_message_id
            }), 200)
        except Exception as e:
            abort(500, {"error": f"Failed to retrieve messages: {e}"})