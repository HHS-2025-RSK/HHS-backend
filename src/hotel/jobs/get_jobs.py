# from flask import request, jsonify
# from firebase_admin import firestore
# from src.db import db


# def get_jobs():
#     try:
#         # Get user_id from query parameters
#         user_id = request.args.get('user_id')
#         if not user_id:
#             return jsonify({'error': 'user_id is required'}), 400

#         # Verify user is a hotel_owner
#         user_ref = db.collection('users').document(user_id)
#         user = user_ref.get()
#         if not user.exists or user.to_dict().get('role') != 'hotel_owner':
#             return jsonify({'error': 'Unauthorized: Only hotel owners can view jobs'}), 403

#         # Get query parameters for filtering
#         location = request.args.get('location')
#         job_type = request.args.get('job_type')
#         status = request.args.get('status', 'open')

#         query = db.collection('HHS').document('hotels').collection(user_id).document('posted_jobs').collection('jobs').where('status', '==', status)

#         # Apply filters if provided
#         if location:
#             query = query.where('location', '==', location)
#         if job_type:
#             query = query.where('job_type', '==', job_type)

#         jobs = query.stream()
#         job_list = [{'id': job.id, **job.to_dict()} for job in jobs]
#         return jsonify(job_list), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


from flask import request, jsonify
from firebase_admin import firestore
from src.db import db

def get_jobs():
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Log the user_id for debugging
        print(f"Attempting to fetch user with ID: {user_id}")

        # Verify user is a hotel owner
        user_ref = db.collection('hhs_app').document('users').collection('Hotel').document(user_id)
        user = user_ref.get()
        
        if not user.exists:
            print(f"User with ID {user_id} does not exist")
            return jsonify({'error': 'User not found'}), 404
        
        user_data = user.to_dict()
        user_role = user_data.get('role')
        print(f"User role for {user_id}: {user_role}")
        
        if user_role != 'Hotel':
            print(f"Unauthorized access: Expected role 'Hotel', found '{user_role}'")
            return jsonify({'error': 'Unauthorized: Only hotel owners can view jobs'}), 403

        # Get query parameters for filtering
        location = request.args.get('location')
        job_type = request.args.get('job_type')
        status = request.args.get('status', 'open')

        # Query jobs from the updated Firestore path
        query = db.collection('hhs_app_data').document('users').collection('Hotel').document(user_id).collection('PostedJobs').where('status', '==', status)

        # Apply filters if provided
        if location:
            query = query.where('location', '==', location)
        if job_type:
            query = query.where('job_type', '==', job_type)

        jobs = query.stream()
        job_list = [{'id': job.id, **job.to_dict()} for job in jobs]
        print(f"Retrieved {len(job_list)} jobs for user {user_id}")
        return jsonify(job_list), 200

    except Exception as e:
        # Log the exception for debugging
        print(f"An error occurred in get_jobs: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500