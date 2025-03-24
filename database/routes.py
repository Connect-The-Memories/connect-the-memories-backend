import os
import tempfile
from flask import Blueprint, jsonify, make_response, request, session
from flask_restx import Api, Namespace, Resource, abort
from werkzeug.utils import secure_filename
from datetime import datetime

"""
    Import functions from services for database access.
"""

from .services_firestore import (
    get_user_data,
    generate_otp,
    retrieve_messages,
    store_messages,
    validate_otp,
    get_linked_users,
    get_verified_uid_from_user_name,
    verify_user_link
    )

from .services_firebase_storage import upload_file

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

        messages = data.get("messages")
        main_user_name = data.get("main_user_name")

        if main_user_name is None:
            abort(401, {"error": "Main user name is required."})

        firebase_token = session.get("firebase_token")

        if firebase_token is None:
            abort(401, {"error": "Unauthorized. Please log in and try again."})
        
        is_verified, decoded_user_token = verify_user_token(firebase_token)
        
        if not is_verified:
            abort(401, {"error": "Unauthorized. Please log in and try again."})

        supp_user_uid = decoded_user_token.get("uid")
        supp_user_data = get_user_data(supp_user_uid)

        supp_full_name = supp_user_data.get("first_name") + " " + supp_user_data.get("last_name")

        main_user_id = get_verified_uid_from_user_name(supp_user_uid, main_user_name)

        linked = verify_user_link(supp_user_uid, main_user_id)

        if not linked:
            abort(401, {"error": "User is not linked."})

        try:
            doc_id = store_messages(supp_full_name, main_user_id, messages)
            return make_response(jsonify({"message_ids": doc_id}), 201)
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


@database_ns.route("/firestore/otp")
class OTP(Resource):
    @database_ns.doc("generate_otp")
    def post(self):
        """
            (POST /otp) Route to generate OTP for user.
        """
        firebase_token = session.get("firebase_token")

        if firebase_token is None:
            return make_response(jsonify({"error": "Unauthorized. Please log in and try again."}), 401)

        is_verified, decoded_user_token = verify_user_token(firebase_token)

        if not is_verified:
            return make_response(jsonify({"error": "Unauthorized. Please log in and try again."}), 401)
        
        user_id = decoded_user_token.get("uid")

        try:
            otp = generate_otp(user_id)
            return make_response(jsonify({"otp": otp}), 201)
        except Exception as e:
            return make_response(jsonify({"error": f"Failed to generate OTP: {str(e)}"}), 500)

    
    @database_ns.doc("validate_otp")
    def put(self):
        """
            (PUT /otp) Route to validate OTP for user.
        """
        data = request.json

        entered_otp = data.get("otp")
        firebase_token = session.get("firebase_token")

        if firebase_token is None:
            return make_response(jsonify({"error": "Unauthorized. Please log in and try again."}), 401)

        is_verified, decoded_user_token = verify_user_token(firebase_token)

        if not is_verified:
            return make_response(jsonify({"error": "Unauthorized. Please log in and try again."}), 401)
        
        support_user_id = decoded_user_token.get("uid")

        try:
            is_valid, msg = validate_otp(support_user_id, entered_otp)

            if not is_valid:
                return make_response(jsonify({"error": msg}), 400)
            
            return make_response(jsonify({"message": msg}), 200)
        except Exception as e:
            return make_response(jsonify({"error": f"Failed to validate OTP: {str(e)}"}), 500)


@database_ns.route("/firestore/linked_accounts")
class LinkedAccounts(Resource):
    @database_ns.doc("get_linked_accounts")
    def get(self):
        """
            (GET /linked_accounts) Route to get linked accounts for user.
        """
        firebase_token = session.get("firebase_token")

        if firebase_token is None:
            return make_response(jsonify({"error": "Unauthorized. Please log in and try again."}), 401)

        is_verified, decoded_user_token = verify_user_token(firebase_token)

        if not is_verified:
            return make_response(jsonify({"error": "Unauthorized. Please log in and try again."}), 401)
        
        user_id = decoded_user_token.get("uid")

        try:
            linked_users = get_linked_users(user_id)
            linked_user_names = list(linked_users.keys())
            return make_response(jsonify({"linked_user_names": linked_user_names}), 200)
        except Exception as e:
            return make_response(jsonify({"error": f"Failed to get linked accounts: {str(e)}"}), 500)
        

@database_ns.route("/firebase_storage/media")
class Media(Resource):
    @database_ns.doc("upload_media")
    def post(self):
        """
            (POST /media) Route to upload media to Firebase Cloud Storage.
        """

        firebase_token = session.get("firebase_token")

        if firebase_token is None:
            return make_response(jsonify({"error": "Unauthorized. Please log in and try again."}), 401)
        
        is_verified, decoded_user_token = verify_user_token(firebase_token)

        if not is_verified:
            return make_response(jsonify({"error": "Unauthorized. Please log in and try again."}), 401)

        main_user_name = request.form.get("main_user_name")
        files = request.files.getlist("files")
        descriptions = request.form.getlist("descriptions")

        supp_user_uid = decoded_user_token.get("uid")
        supp_user_data = get_user_data(supp_user_uid)
        supp_user_full_name = supp_user_data.get("first_name") + " " + supp_user_data.get("last_name")
        main_user_uid = get_verified_uid_from_user_name(supp_user_uid, main_user_name)

        linked = verify_user_link(supp_user_uid, main_user_uid)

        if not linked:
            return make_response(jsonify({"error": "User is not linked."}), 401)

        for i, file_storage in enumerate(files):
            file_name = secure_filename(file_storage.filename)

            with tempfile.TemporaryDirectory() as tmpdir:
                temp_path = os.path.join(tmpdir, file_name)
                file_storage.save(temp_path)


                try:
                    desc = descriptions[i] if i < len(descriptions) else ""
                    upload_file(main_user_uid, supp_user_uid, supp_user_full_name, firebase_token, temp_path, file_name, desc)

                except Exception as e:
                    return {"error": str(e)}, 500

        return {"message": "Files uploaded successfully"}, 200

    @database_ns.doc("retrieve_media")
    def get(self):
        """
            (GET /media) Route to retrieve media from Firebase Cloud Storage.
        """
        pass