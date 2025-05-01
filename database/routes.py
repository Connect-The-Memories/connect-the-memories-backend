import os
import tempfile
from flask import Blueprint, g, jsonify, make_response, request, session
from flask_restx import Api, Namespace, Resource, abort
from werkzeug.utils import secure_filename

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
    verify_user_link,
    get_random_indexed_media,
    store_exercise_data,
    get_exercise_data,
    store_journal_entries,
    get_journal_entries
    )

from .services_firebase_storage import upload_file, generate_signed_urls

from utils.decorators import token_required
from utils.formatters import iso_to_datetime, format_data_for_json
from utils.normalizors import process_exercise_data


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
"""
@database_ns.route("/firestore/messages")
class Messages(Resource):
    @database_ns.doc("store_messages")
    @token_required
    def put(self):
        """
            (PUT /messages) Route to store messages in Firestore.
        """
        data = request.json

        messages = data.get("messages")
        main_user_name = data.get("main_user_name")

        if main_user_name is None:
            abort(401, {"error": "Main user name is required."})

        supp_user_uid = g.uid
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
    @token_required
    def get(self):
        """
            (GET /messages) Route to retrieve messages from Firestore.
        """
        try:
            messages = retrieve_messages(g.uid)
            return make_response(jsonify({
                "messages": messages,
            }), 200)
        except Exception as e:
            abort(500, {"error": f"Failed to retrieve messages: {e}"})


@database_ns.route("/firestore/otp")
class OTP(Resource):
    @database_ns.doc("generate_otp")
    @token_required
    def post(self):
        """
            (POST /otp) Route to generate OTP for user.
        """
        try:
            otp = generate_otp(g.uid)
            return make_response(jsonify({"otp": otp}), 201)
        except Exception as e:
            return make_response(jsonify({"error": f"Failed to generate OTP: {str(e)}"}), 500)

    
    @database_ns.doc("validate_otp")
    @token_required
    def put(self):
        """
            (PUT /otp) Route to validate OTP for user.
        """
        data = request.json

        entered_otp = data.get("otp")

        try:
            is_valid, msg = validate_otp(g.uid, entered_otp)

            if not is_valid:
                return make_response(jsonify({"error": msg}), 400)
            
            return make_response(jsonify({"message": msg}), 200)
        except Exception as e:
            return make_response(jsonify({"error": f"Failed to validate OTP: {str(e)}"}), 500)


@database_ns.route("/firestore/linked_accounts")
class LinkedAccounts(Resource):
    @database_ns.doc("get_linked_accounts")
    @token_required
    def get(self):
        """
            (GET /linked_accounts) Route to get linked accounts for user.
        """
        try:
            linked_users = get_linked_users(g.uid)
            linked_user_names = list(linked_users.keys())
            return make_response(jsonify({"linked_user_names": linked_user_names}), 200)
        except Exception as e:
            return make_response(jsonify({"error": f"Failed to get linked accounts: {str(e)}"}), 500)
        

@database_ns.route("/firebase_storage/media")
class Media(Resource):
    @database_ns.doc("upload_media")
    @token_required
    def post(self):
        """
            (POST /media) Route to upload media to Firebase Cloud Storage.
        """
        main_user_name = request.form.get("main_user_name")
        files = request.files.getlist("files")
        descriptions = request.form.getlist("descriptions")
        file_dates = request.form.getlist("dates")

        supp_user_uid = g.uid
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
                    date = file_dates[i] if i < len(file_dates) else ""
                    upload_file(main_user_uid, supp_user_uid, supp_user_full_name, g.firebase_token, temp_path, file_name, desc, date)

                except Exception as e:
                    return {"error": str(e)}, 500

        return {"message": "Files uploaded successfully"}, 200

    @database_ns.doc("retrieve_media")
    @token_required
    def get(self):
        """
            (GET /media) Route to retrieve media from Firebase Cloud Storage.
        """
        try:
            media = generate_signed_urls(g.uid)
            return make_response(jsonify({"media": media}), 200)
        except Exception as e:
            return make_response(jsonify({"error": f"Failed to retrieve images: {str(e)}"}), 500)        


@database_ns.route("/firestore/media/random_indexed")
class RandomIndexedMedia(Resource):
    @database_ns.doc("get_random_indexed_media")
    @token_required
    def get(self):
        """
            (GET /media/random_indexed) Route to retrieve random indexed media from Firestore.
            Removed session usage for simplicity as nothing else uses sessions and there were issues with it on GPC.
        """
        # session_key = f"visited_{g.uid}"
        # visited_indices = session.get(session_key, [])
        visited_indices = []
        count = int(request.args.get("count", 1))

        try:
            media_list = []
            for _ in range(count):
                try:
                    media = get_random_indexed_media(g.uid, visited_indices)
                    media_list.append(media)
                    visited_indices.append(media["media_index"])
                except ValueError:
                    break

            if not media_list:
                return make_response(jsonify({"error": "No unvisited media found."}), 404)

            return make_response(jsonify({"media": media_list}), 200)
        except Exception as e:
            return make_response(jsonify({"error": f"Failed to retrieve images: {str(e)}"}), 500)


@database_ns.route("/firestore/exercises")
class Exercises(Resource):
    @database_ns.doc("store_exercise_data")
    @token_required
    def post(self):
        """
            (POST /exercises) Route to store exercise data in Firestore.
        """
        data = request.json

        exercise_name = data.get("exercise")
        timestamp = data.get("timestamp")
        formatted_timestamp = iso_to_datetime(timestamp)
        accuracy = float(data.get("accuracy"))
        avg_reaction_time = float(data.get("avg_reaction_time"))

        if not exercise_name or not timestamp or not accuracy or not avg_reaction_time:
            return make_response(jsonify({"error": "All fields are required."}), 400)
        
        try:
            store_exercise_data(exercise_name, formatted_timestamp, accuracy, avg_reaction_time, g.uid)
            return make_response(jsonify({"message": "Exercise data stored successfully."}), 201)
        except Exception as e:
            return make_response(jsonify({"error": f"Failed to store exercise data: {str(e)}"}), 500)
    
    @database_ns.doc("get_exercise_data")
    @token_required
    def get(self):
        """
            (GET /exercises) Route to retrieve exercise data from Firestore.
        """
        try:
            all_exercise_data = get_exercise_data(g.uid)
            normalized_data = process_exercise_data(all_exercise_data)
            json_safe_data = format_data_for_json(normalized_data)
            return make_response(jsonify({"exercise_data": json_safe_data}), 200)
        except Exception as e:
            return make_response(jsonify({"error": f"Failed to retrieve exercise data: {str(e)}"}), 500)
    

@database_ns.route("/firestore/journal_entries")
class JournalEntries(Resource):
    @database_ns.doc("store_journal_entry")
    @token_required
    def post(self):
        """
            (POST /journal_entries) Route to store journal entries in Firestore.
        """
        data = request.json
        entry = data.get("entry")
        timestamp = data.get("timestamp")
        destination_path = data.get("destination_path")

        if not entry or not timestamp or not destination_path:
            return make_response(jsonify({"error": "All fields are required."}), 400)

        formatted_timestamp = iso_to_datetime(timestamp)

        try:
            store_journal_entries(entry, formatted_timestamp, destination_path, g.uid)
            return make_response(jsonify({"message": "Journal entry stored successfully."}), 201)
        except Exception as e:
            return make_response(jsonify({"error": f"Failed to store journal entry: {str(e)}"}), 500)
        
    @database_ns.doc("get_journal_entries")
    @token_required
    def get(self):
        """
        GET /firestore/journal_entries?date=YYYY-MM-DDTHH:MM:SS.sssZ
        Returns all journal entries for that calendar day.
        """
        # 1) pull date from query-param
        date_str = request.args.get("date")
        if not date_str:
            abort(400, "Missing required `date` query parameter")

        # 2) parse ISO → datetime
        try:
            date = iso_to_datetime(date_str)
        except Exception:
            abort(400, "Invalid date format; expected ISO string")

        # 3) fetch entries
        try:
            entries = get_journal_entries(g.uid, date)
        except Exception as e:
            abort(500, f"Failed to retrieve journal entries: {e}")

        # 4) convert each timestamp to ISO for JSON
        for e in entries:
            if hasattr(e["timestamp"], "isoformat"):
                e["timestamp"] = e["timestamp"].isoformat()

        # 5) return under entries 
        return make_response(jsonify({"entries": entries}), 200)