from flask import request, jsonify
from firebase_admin import firestore
import datetime
from src.db import db # Assuming 'db' is your initialized Firestore client

def get_hotel_profile():
    """
    Retrieves a combined hotel profile by fetching and merging data from
    the user authentication collection and the detailed profile collection.
    """
    try:
        # --- 1. Get and Validate user_id ---
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({'error': 'user_id is required as a query parameter'}), 400

        # --- 2. Fetch Base User Data ---
        # This data is the primary source of truth for auth-related fields.
        base_user_ref = db.collection('hhs_app').document('users').collection('Hotel').document(user_id)
        base_user_doc = base_user_ref.get()

        if not base_user_doc.exists:
            return jsonify({'error': 'Hotel user not found'}), 404

        base_user_data = base_user_doc.to_dict()

        # --- 3. Fetch Detailed Profile Data ---
        profile_ref = db.collection('hhs_app_data').document('users').collection('Hotel').document(user_id).collection('profile').document('data')
        profile_doc = profile_ref.get()
        
        profile_data = profile_doc.to_dict() if profile_doc.exists else {}

        # --- 4. Combine the Data ---
        # Start with the detailed profile, then overwrite with base data
        # to ensure core fields (email, phone, etc.) are from the auth source.
        combined_data = {**profile_data, **base_user_data}

        # --- 5. Sanitize Timestamps for JSON Response ---
        for key, value in combined_data.items():
            if isinstance(value, datetime.datetime):
                combined_data[key] = value.isoformat()

        return jsonify({
            'message': 'Hotel profile retrieved successfully',
            'user_id': user_id,
            'data': combined_data
        }), 200

    except Exception as e:
        print(f"An error occurred in get_hotel_profile: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500

