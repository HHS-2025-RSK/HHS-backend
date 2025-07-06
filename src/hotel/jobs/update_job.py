# from flask import request, jsonify
# from firebase_admin import firestore
# from src.db import db


# def update_job(job_id):
#     try:
#         data = request.json
#         if not data:
#             return jsonify({'error': 'Request body is required'}), 400

#         # Validate user_id
#         user_id = data.get('user_id')
#         if not user_id:
#             return jsonify({'error': 'user_id is required'}), 400

#         # Verify user is a hotel_owner
#         user_ref = db.collection('users').document(user_id)
#         user = user_ref.get()
#         if not user.exists or user.to_dict().get('role') != 'hotel_owner':
#             return jsonify({'error': 'Unauthorized: Only hotel owners can update jobs'}), 403

#         # Validate mandatory fields if provided
#         if 'title' in data and not data['title']:
#             return jsonify({'error': 'Title cannot be empty'}), 400
#         if 'description' in data and not data['description']:
#             return jsonify({'error': 'Description cannot be empty'}), 400
#         if 'company' in data and not data['company']:
#             return jsonify({'error': 'Company cannot be empty'}), 400
#         if 'location' in data and not data['location']:
#             return jsonify({'error': 'Location cannot be empty'}), 400

#         # Check if job exists
#         job_ref = db.collection('HHS').document('hotels').collection(user_id).document('posted_jobs').collection('jobs').document(job_id)
#         if not job_ref.get().exists:
#             return jsonify({'error': 'Job not found'}), 404

#         # Update only provided fields
#         update_data = {}
#         for field in ['title', 'description', 'company', 'location', 'salary', 'job_type', 'benefits', 
#                       'hotel_star_rating', 'amenities', 'required_certificates', 'application_deadline', 'status']:
#             if field in data:
#                 update_data[field] = data[field]

#         job_ref.update(update_data)
#         updated_job = job_ref.get().to_dict()
#         updated_job['id'] = job_id
#         return jsonify(updated_job), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


from flask import request, jsonify
from firebase_admin import firestore
from src.db import db

def update_job(job_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        # Validate user_id
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Verify user is a hotel owner
        user_ref = db.collection('hhs_app').document('users').collection('Hotel').document(user_id)
        user = user_ref.get()
        if not user.exists:
            print(f"User with ID {user_id} does not exist")
            return jsonify({'error': 'User not found'}), 404
        user_role = user.to_dict().get('role')
        if user_role != 'Hotel':
            print(f"Unauthorized access: Expected role 'Hotel', found '{user_role}'")
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
        job_ref = db.collection('hhs_app_data').document('users').collection('Hotel').document(user_id).collection('PostedJobs').document(job_id)
        if not job_ref.get().exists:
            print(f"Job with ID {job_id} for user {user_id} not found")
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
        print(f"Job {job_id} updated successfully for user {user_id}")
        return jsonify(updated_job), 200
    except Exception as e:
        # Log the exception for debugging
        print(f"An error occurred in update_job: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500