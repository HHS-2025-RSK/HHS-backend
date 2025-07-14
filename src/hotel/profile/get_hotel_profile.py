from flask import request, jsonify
from firebase_admin import firestore
import datetime
from src.db import db # Assuming 'db' is your initialized Firestore client

def get_hotel_profile():
    """
    Retrieves a hotel's profile, separating credential data from
    the detailed profile information.
    """
    try:
        # --- 1. Get and Validate user_id ---
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({'error': 'user_id is required as a query parameter'}), 400

        # --- 2. Fetch Credentials Data ---
        # This data is the primary source of truth for auth-related fields.
        credentials_ref = db.collection('hhs_app').document('users').collection('Hotel').document(user_id)
        credentials_doc = credentials_ref.get()

        if not credentials_doc.exists:
            return jsonify({'error': 'Hotel user not found'}), 404

        credentials_data = credentials_doc.to_dict()

        # --- 3. Fetch Detailed Profile Data ---
        profile_ref = db.collection('hhs_app_data').document('users').collection('Hotel').document(user_id).collection('profile').document('data')
        profile_doc = profile_ref.get()
        
        profile_data = profile_doc.to_dict() if profile_doc.exists else {}

        # --- 4. Sanitize Timestamps for JSON Response ---
        for key, value in credentials_data.items():
            if isinstance(value, datetime.datetime):
                credentials_data[key] = value.isoformat()
        
        for key, value in profile_data.items():
            if isinstance(value, datetime.datetime):
                profile_data[key] = value.isoformat()

        # --- 5. Structure the Response Data ---
        # Separate the data from the two paths into distinct objects.
        response_data = {
            'credentials_data': credentials_data,
            'profile_data': profile_data
        }

        return jsonify({
            'message': 'Hotel profile retrieved successfully',
            'user_id': user_id,
            'data': response_data
        }), 200

    except Exception as e:
        print(f"An error occurred in get_hotel_profile: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500
