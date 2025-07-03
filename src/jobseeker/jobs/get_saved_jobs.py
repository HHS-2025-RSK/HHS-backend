from flask import request, jsonify
from firebase_admin import firestore
import datetime
from src.db import db

def get_saved_jobs():
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required in query parameters'}), 400

        # Verify user is a job_seeker
        user_ref = db.collection('users').document(user_id)
        user = user_ref.get()
        if not user.exists or user.to_dict().get('role') != 'job_seeker':
            return jsonify({'error': 'Unauthorized: Only job seekers can view saved jobs'}), 403

        # Fetch saved jobs from Firestore
        saved_jobs_ref = db.collection('HHS').document('Jobseekers').collection('profilesetup').document(user_id).collection('savedjobs')
        saved_jobs = saved_jobs_ref.get()

        # Prepare response data
        saved_jobs_data = []
        for saved_job in saved_jobs:
            job_data = saved_job.to_dict()
            # Convert timestamps to strings
            for key, value in job_data.items():
                if isinstance(value, datetime.datetime):
                    job_data[key] = value.isoformat()
            # Fetch job details from job collection
            job_ref = db.collection('HHS').document('hotels').collection(job_data['hotel_owner_id']).document('posted_jobs').collection('jobs').document(job_data['job_id'])
            job = job_ref.get()
            if job.exists:
                job_details = job.to_dict()
                # Convert job timestamps
                for key, value in job_details.items():
                    if isinstance(value, datetime.datetime):
                        job_details[key] = value.isoformat()
                job_data['job_details'] = job_details
            else:
                job_data['job_details'] = None  # Job may have been deleted
            saved_jobs_data.append(job_data)

        return jsonify({
            'message': 'Saved jobs retrieved successfully',
            'user_id': user_id,
            'data': saved_jobs_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500