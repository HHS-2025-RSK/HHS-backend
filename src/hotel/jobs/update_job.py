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

def update_job(job_id):
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        # Validate user_id
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Verify user is a hotel_owner
        user_ref = db.collection('users').document(user_id)
        user = user_ref.get()
        if not user.exists or user.to_dict().get('role') != 'hotel_owner':
            return jsonify({'error': 'Unauthorized: Only hotel owners can update jobs'}), 403

        # Validate mandatory fields if provided
        if 'title' in data and not data['title']:
            return jsonify({'error': 'Title cannot be empty'}), 400
        if 'description' in data and not data['description']:
            return jsonify({'error': 'Description cannot be empty'}), 400
        if 'company' in data and not data['company']:
            return jsonify({'error': 'Company cannot be empty'}), 400
        if 'location' in data and not data['location']:
            return jsonify({'error': 'Location cannot be empty'}), 400

        # Check if job exists
        job_ref = db.collection('HHS').document('hotels').collection(user_id).document('posted_jobs').collection('jobs').document(job_id)
        if not job_ref.get().exists:
            return jsonify({'error': 'Job not found'}), 404

        # Update only provided fields
        update_data = {}
        for field in ['title', 'description', 'company', 'location', 'salary', 'job_type', 'benefits', 
                      'hotel_star_rating', 'amenities', 'required_certificates', 'application_deadline', 'status']:
            if field in data:
                update_data[field] = data[field]

        job_ref.update(update_data)
        updated_job = job_ref.get().to_dict()
        updated_job['id'] = job_id
        return jsonify(updated_job), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500