from flask import request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os

# Initialize Firebase (only once)
if not firebase_admin._apps:
    load_dotenv()
    firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    if not firebase_credentials_path or not os.path.exists(firebase_credentials_path):
        raise ValueError('Firebase credentials path is invalid or not found')
    cred = credentials.Certificate(firebase_credentials_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def save_job():
    try:
        # Get JSON data
        data = request.json
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400

        # Validate user_id and job_id
        user_id = data.get('user_id')
        job_id = data.get('job_id')
        hotel_owner_id = data.get('hotel_owner_id')
        if not user_id or not job_id or not hotel_owner_id:
            return jsonify({'error': 'user_id, job_id, and hotel_owner_id are required'}), 400

        # Verify user is a job_seeker
        user_ref = db.collection('users').document(user_id)
        user = user_ref.get()
        if not user.exists or user.to_dict().get('role') != 'job_seeker':
            return jsonify({'error': 'Unauthorized: Only job seekers can save jobs'}), 403

        # Verify job exists
        job_ref = db.collection('HHS').document('hotels').collection(hotel_owner_id).document('posted_jobs').collection('jobs').document(job_id)
        job = job_ref.get()
        if not job.exists:
            return jsonify({'error': 'Job not found'}), 404

        # Prepare saved job data
        saved_job = {
            'job_id': job_id,
            'hotel_owner_id': hotel_owner_id,
            'saved_at': firestore.SERVER_TIMESTAMP
        }

        # Store in Firestore
        saved_job_ref = db.collection('HHS').document('Jobseekers').collection('profilesetup').document(user_id).collection('savedjobs').document(job_id)
        saved_job_ref.set(saved_job)

        # Prepare response data
        response_data = {
            'user_id': user_id,
            'job_id': job_id,
            'hotel_owner_id': hotel_owner_id
        }

        return jsonify({
            'message': 'Job successfully saved',
            'user_id': user_id,
            'data': response_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500