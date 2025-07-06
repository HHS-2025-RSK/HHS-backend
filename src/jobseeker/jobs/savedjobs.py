# from flask import request, jsonify
# from firebase_admin import firestore
# from src.db import db


# def save_job():
#     try:
#         # Get JSON data
#         data = request.json
#         if not data:
#             return jsonify({'error': 'Request body must be JSON'}), 400

#         # Validate user_id and job_id
#         user_id = data.get('user_id')
#         job_id = data.get('job_id')
#         hotel_owner_id = data.get('hotel_owner_id')
#         if not user_id or not job_id or not hotel_owner_id:
#             return jsonify({'error': 'user_id, job_id, and hotel_owner_id are required'}), 400

#         # Verify user is a job_seeker
#         user_ref = db.collection('users').document(user_id)
#         user = user_ref.get()
#         if not user.exists or user.to_dict().get('role') != 'job_seeker':
#             return jsonify({'error': 'Unauthorized: Only job seekers can save jobs'}), 403

#         # Verify job exists
#         job_ref = db.collection('HHS').document('hotels').collection(hotel_owner_id).document('posted_jobs').collection('jobs').document(job_id)
#         job = job_ref.get()
#         if not job.exists:
#             return jsonify({'error': 'Job not found'}), 404

#         # Prepare saved job data
#         saved_job = {
#             'job_id': job_id,
#             'hotel_owner_id': hotel_owner_id,
#             'saved_at': firestore.SERVER_TIMESTAMP
#         }

#         # Store in Firestore
#         saved_job_ref = db.collection('HHS').document('Jobseekers').collection('profilesetup').document(user_id).collection('savedjobs').document(job_id)
#         saved_job_ref.set(saved_job)

#         # Prepare response data
#         response_data = {
#             'user_id': user_id,
#             'job_id': job_id,
#             'hotel_owner_id': hotel_owner_id
#         }

#         return jsonify({
#             'message': 'Job successfully saved',
#             'user_id': user_id,
#             'data': response_data
#         }), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


from flask import request, jsonify
from firebase_admin import firestore
from src.db import db

def save_job():
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            print("No request body provided")
            return jsonify({'error': 'Request body must be JSON'}), 400

        # Validate user_id, job_id, and hotel_owner_id
        user_id = data.get('user_id')
        job_id = data.get('job_id')
        hotel_owner_id = data.get('hotel_owner_id')
        if not user_id or not job_id or not hotel_owner_id:
            print(f"Missing required fields: user_id={user_id}, job_id={job_id}, hotel_owner_id={hotel_owner_id}")
            return jsonify({'error': 'user_id, job_id, and hotel_owner_id are required'}), 400

        # Verify user is a job seeker
        user_ref = db.collection('hhs_app').document('users').collection('Job Seeker').document(user_id)
        user = user_ref.get()
        if not user.exists:
            print(f"User with ID {user_id} does not exist")
            return jsonify({'error': 'User not found'}), 404
        user_role = user.to_dict().get('role')
        if user_role != 'Job Seeker':
            print(f"Unauthorized access: Expected role 'JobSeeker', found '{user_role}'")
            return jsonify({'error': 'Unauthorized: Only job seekers can save jobs'}), 403

        # Verify job exists
        job_ref = db.collection('hhs_app_data').document('users').collection('Hotel').document(hotel_owner_id).collection('PostedJobs').document(job_id)
        job = job_ref.get()
        if not job.exists:
            print(f"Job with ID {job_id} for hotel_owner_id {hotel_owner_id} not found")
            return jsonify({'error': 'Job not found'}), 404

        # Check if job is already saved
        saved_job_ref = db.collection('hhs_app_data').document('users').collection('Job Seeker').document(user_id).collection('savedjobs').document(job_id)
        if saved_job_ref.get().exists:
            print(f"Job {job_id} already saved by user {user_id}")
            return jsonify({'error': 'Job already saved'}), 409

        # Prepare saved job data
        saved_job = {
            'job_id': job_id,
            'hotel_owner_id': hotel_owner_id,
            'saved_at': firestore.SERVER_TIMESTAMP
        }

        # Store in Firestore
        saved_job_ref.set(saved_job)
        print(f"Job {job_id} saved successfully for user {user_id}")

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
        # Log the exception for debugging
        print(f"An error occurred in save_job: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500