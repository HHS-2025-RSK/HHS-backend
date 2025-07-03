from flask import jsonify
from firebase_admin import firestore
import datetime
from src.db import db


def get_jobseeker_profile(user_id):
    try:
        # Validate user_id
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Fetch profile from Firestore
        profile_ref = db.collection('HHS').document('Jobseekers').collection('profilesetup').document(user_id)
        profile = profile_ref.get()

        if not profile.exists:
            return jsonify({'error': 'Profile not found'}), 404

        # Prepare response data
        profile_data = profile.to_dict()
        
        # Convert timestamps to strings
        for key, value in profile_data.items():
            if isinstance(value, datetime.datetime):
                profile_data[key] = value.isoformat()

        return jsonify(profile_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500