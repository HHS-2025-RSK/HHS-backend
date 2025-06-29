from flask import jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
import datetime

# Initialize Firebase (only once)
if not firebase_admin._apps:
    load_dotenv()
    firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    if not firebase_credentials_path or not os.path.exists(firebase_credentials_path):
        raise ValueError('Firebase credentials path is invalid or not found')
    cred = credentials.Certificate(firebase_credentials_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

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