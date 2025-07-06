# from flask import request, jsonify
# from firebase_admin import firestore
# from src.db import db

# def create_job():
#     """Creates a new job posting for a verified hotel owner."""
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({'error': 'Invalid JSON data provided'}), 400

#         # Validate user_id from the request body
#         user_id = data.get('user_id')
#         if not user_id:
#             return jsonify({'error': 'user_id is required'}), 400

#         # Verify the user is a hotel_owner
#         user_ref = db.collection('users').document(user_id)
#         user = user_ref.get()
#         if not user.exists or user.to_dict().get('role') != 'hotel_owner':
#             return jsonify({'error': 'Unauthorized: Only hotel owners can post jobs'}), 403

#         # Validate mandatory fields
#         mandatory_fields = ['title', 'description', 'company', 'location']
#         missing_fields = [field for field in mandatory_fields if not data.get(field)]
#         if missing_fields:
#             return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

#         # Prepare job data for Firestore
#         job = {
#             'title': data['title'],
#             'description': data['description'],
#             'company': data['company'],
#             'location': data['location'],
#             'salary': data.get('salary', ''),
#             'job_type': data.get('job_type', ''),
#             'benefits': data.get('benefits', []),
#             'hotel_star_rating': data.get('hotel_star_rating', 0),
#             'amenities': data.get('amenities', []),
#             'required_certificates': data.get('required_certificates', []),
#             'application_deadline': data.get('application_deadline'),
#             'status': data.get('status', 'open'),
#             'posted_at': firestore.SERVER_TIMESTAMP
#         }

#         # Store the new job in Firestore
#         write_result = db.collection('HHS', 'hotels', user_id, 'posted_jobs', 'jobs').add(job)
        
#         # Prepare the response data, including the new document ID
#         response_data = job.copy()
#         response_data['id'] = write_result[1].id
#         response_data.pop('posted_at', None) # Optionally remove server timestamp from immediate response

#         return jsonify({
#             "message": "Job created successfully",
#             "data": response_data
#         }), 201

#     except Exception as e:
#         # Log the exception for debugging
#         print(f"An error occurred in create_job: {e}")
#         return jsonify({'error': 'An internal server error occurred'}), 500



from flask import request, jsonify
from firebase_admin import firestore
from src.db import db

def create_job():
    """Creates a new job posting for a verified hotel owner."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data provided'}), 400

        # Validate user_id from the request body
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Verify the user is a hotel_owner
        user_ref = db.collection('hhs_app').document('users').collection('Hotel').document(user_id)
        user = user_ref.get()
        if not user.exists or user.to_dict().get('role') != 'Hotel':
            return jsonify({'error': 'Unauthorized: Only hotel owners can post jobs'}), 403

        # Validate mandatory fields
        mandatory_fields = ['title', 'description', 'company', 'location']
        missing_fields = [field for field in mandatory_fields if not data.get(field)]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Prepare job data for Firestore
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
            'application_deadline': data.get('application_deadline'),
            'status': data.get('status', 'open'),
            'posted_at': firestore.SERVER_TIMESTAMP
        }

        # Store the new job in Firestore with dynamic path
        job_ref = db.collection('hhs_app_data').document('users').collection('Hotel').document(user_id).collection('PostedJobs').document()
        job_ref.set(job)

        # Prepare the response data, including the new document ID
        response_data = job.copy()
        response_data['id'] = job_ref.id
        response_data.pop('posted_at', None)  # Optionally remove server timestamp from immediate response

        return jsonify({
            "message": "Job created successfully",
            "data": response_data
        }), 201

    except Exception as e:
        # Log the exception for debugging
        print(f"An error occurred in create_job: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500