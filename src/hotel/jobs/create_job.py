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

def create_job():
    try:
        data = request.json
        # Validate user_id
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Verify user is a hotel_owner
        user_ref = db.collection('users').document(user_id)
        user = user_ref.get()
        if not user.exists or user.to_dict().get('role') != 'hotel_owner':
            return jsonify({'error': 'Unauthorized: Only hotel owners can post jobs'}), 403

        # Validate mandatory fields
        mandatory_fields = ['title', 'description', 'company', 'location']
        for field in mandatory_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Prepare job data
        job = {
            'title': data['title'],
            'description': data['description'],
            'company': data['company'],
            'location': data['location'],
            'salary': data.get('salary', ''),
            'job_type': data.get('job_type', ''),
            'benefits': data.get('benefits', []),
            'hotel_star_rating': data.get('hotel_star_rating', 0),
            'amenities': data.get('amenities', []),
            'required_certificates': data.get('required_certificates', []),
            'application_deadline': data.get('application_deadline', ''),
            'status': data.get('status', 'open'),
            'posted_at': firestore.SERVER_TIMESTAMP
        }

        # Store in Firestore: HHS/hotels/<user_id>/posted_jobs
        doc_ref = db.collection('HHS').document('hotels').collection(user_id).document('posted_jobs').collection('jobs').add(job)
        response_data = {
            'id': doc_ref[1].id,
            'title': job['title'],
            'description': job['description'],
            'company': job['company'],
            'location': job['location'],
            'salary': job['salary'],
            'job_type': job['job_type'],
            'benefits': job['benefits'],
            'hotel_star_rating': job['hotel_star_rating'],
            'amenities': job['amenities'],
            'required_certificates': job['required_certificates'],
            'application_deadline': job['application_deadline'],
            'status': job['status']
        }
        return jsonify(response_data), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500