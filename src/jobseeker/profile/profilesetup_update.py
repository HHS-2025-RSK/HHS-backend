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

def create_or_update_jobseeker_profile(user_id):
    try:
        # Validate user_id
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Verify user is a job_seeker
        user_ref = db.collection('users').document(user_id)
        user = user_ref.get()
        if not user.exists or user.to_dict().get('role') != 'job_seeker':
            return jsonify({'error': 'Unauthorized: Only job seekers can create a profile'}), 403

        # Get JSON data
        data = request.json
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400

        # Validate mandatory fields
        mandatory_fields = ['name', 'location']
        for field in mandatory_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Prepare profile data
        profile = {
            'name': data['name'],
            'location': data['location'],
            'headline': data.get('headline', ''),
            'contact_email': user.to_dict().get('email', ''),
            'phone_number': data.get('phone_number', ''),
            'linkedin_profile': data.get('linkedin_profile', ''),
            'portfolio': data.get('portfolio', ''),
            'experience_years': int(data.get('experience_years', 0)),
            'availability': data.get('availability', 'Not specified'),
            'preferred_categories': data.get('preferred_categories', []),
            'skills': data.get('skills', []),
            'certifications': data.get('certifications', []),
            'languages': data.get('languages', []),
            'resume_url': data.get('resume_url', ''),
            'profile_updated_at': firestore.SERVER_TIMESTAMP
        }

        # Store in Firestore
        profile_ref = db.collection('HHS').document('Jobseekers').collection('profilesetup').document(user_id)
        doc_snapshot = profile_ref.get()
        if not doc_snapshot.exists:
            profile['profile_created_at'] = firestore.SERVER_TIMESTAMP

        profile_ref.set(profile, merge=True)

        # Prepare response data
        response_data = {
            'user_id': user_id,
            'name': profile['name'],
            'location': profile['location'],
            'headline': profile['headline'],
            'contact_email': profile['contact_email'],
            'phone_number': profile['phone_number'],
            'linkedin_profile': profile['linkedin_profile'],
            'portfolio': profile['portfolio'],
            'experience_years': profile['experience_years'],
            'availability': profile['availability'],
            'preferred_categories': profile['preferred_categories'],
            'skills': profile['skills'],
            'certifications': profile['certifications'],
            'languages': profile['languages'],
            'resume_url': profile['resume_url']
        }

        return jsonify({
            'message': 'Profile successfully saved',
            'user_id': user_id,
            'data': response_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500