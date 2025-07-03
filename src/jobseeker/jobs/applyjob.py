from flask import request, jsonify
from firebase_admin import firestore
from src.db import db

def apply_job():
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
            return jsonify({'error': 'Unauthorized: Only job seekers can apply to jobs'}), 403

        # Verify job exists
        job_ref = db.collection('HHS').document('hotels').collection(hotel_owner_id).document('posted_jobs').collection('jobs').document(job_id)
        job = job_ref.get()
        if not job.exists:
            return jsonify({'error': 'Job not found'}), 404

        # Verify user has a profile
        profile_ref = db.collection('HHS').document('Jobseekers').collection('profilesetup').document(user_id)
        profile = profile_ref.get()
        if not profile.exists:
            return jsonify({'error': 'User must have a profile to apply for a job'}), 400

        # Prepare application data
        application = {
            'user_id': user_id,
            'applied_at': firestore.SERVER_TIMESTAMP,
            'profile_snapshot': profile.to_dict()  # Store profile data at time of application
        }

        # Store in Firestore
        applicant_ref = db.collection('HHS').document('hotels').collection(hotel_owner_id).document('posted_jobs').collection('jobs').document(job_id).collection('applicants').document(user_id)
        
        # Check if user already applied
        if applicant_ref.get().exists:
            return jsonify({'error': 'User has already applied to this job'}), 409

        applicant_ref.set(application)

        # Prepare response data
        response_data = {
            'user_id': user_id,
            'job_id': job_id,
            'hotel_owner_id': hotel_owner_id
        }

        return jsonify({
            'message': 'Job application successfully submitted',
            'user_id': user_id,
            'data': response_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500