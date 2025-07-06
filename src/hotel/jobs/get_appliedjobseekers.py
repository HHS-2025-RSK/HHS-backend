# from flask import request, jsonify
# from firebase_admin import firestore
# import datetime
# from src.db import db

# def get_applied_jobseekers():
#     try:
#         # Get hotel_owner_id and job_id from query parameters
#         hotel_owner_id = request.args.get('hotel_owner_id')
#         job_id = request.args.get('job_id')
#         if not hotel_owner_id or not job_id:
#             return jsonify({'error': 'hotel_owner_id and job_id are required in query parameters'}), 400

#         # Verify user is a hotel_owner
#         user_ref = db.collection('users').document(hotel_owner_id)
#         user = user_ref.get()
#         if not user.exists or user.to_dict().get('role') != 'hotel_owner':
#             return jsonify({'error': 'Unauthorized: Only hotel owners can view applicants'}), 403

#         # Verify job exists
#         job_ref = db.collection('HHS').document('hotels').collection(hotel_owner_id).document('posted_jobs').collection('jobs').document(job_id)
#         job = job_ref.get()
#         if not job.exists:
#             return jsonify({'error': 'Job not found'}), 404

#         # Fetch applicants from Firestore
#         applicants_ref = job_ref.collection('applicants')
#         applicants = applicants_ref.get()

#         # Prepare response data
#         applicants_data = []
#         for applicant in applicants:
#             applicant_data = applicant.to_dict()
#             # Convert timestamps to strings
#             for key, value in applicant_data.items():
#                 if isinstance(value, datetime.datetime):
#                     applicant_data[key] = value.isoformat()
#                 elif isinstance(value, dict):  # Handle nested profile_snapshot
#                     for sub_key, sub_value in value.items():
#                         if isinstance(sub_value, datetime.datetime):
#                             applicant_data[key][sub_key] = sub_value.isoformat()
#             applicants_data.append(applicant_data)

#         return jsonify({
#             'message': 'Applicants retrieved successfully',
#             'hotel_owner_id': hotel_owner_id,
#             'job_id': job_id,
#             'data': applicants_data
#         }), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


from flask import request, jsonify
from firebase_admin import firestore
import datetime
from src.db import db

def get_applied_jobseekers():
    try:
        # Get hotel_owner_id and job_id from query parameters
        hotel_owner_id = request.args.get('hotel_owner_id')
        job_id = request.args.get('job_id')
        if not hotel_owner_id or not job_id:
            print(f"Missing required query parameters: hotel_owner_id={hotel_owner_id}, job_id={job_id}")
            return jsonify({'error': 'hotel_owner_id and job_id are required in query parameters'}), 400

        # Verify user is a hotel owner
        user_ref = db.collection('hhs_app').document('users').collection('Hotel').document(hotel_owner_id)
        user = user_ref.get()
        if not user.exists:
            print(f"User with ID {hotel_owner_id} does not exist")
            return jsonify({'error': 'User not found'}), 404
        user_role = user.to_dict().get('role')
        if user_role != 'Hotel':
            print(f"Unauthorized access: Expected role 'Hotel', found '{user_role}'")
            return jsonify({'error': 'Unauthorized: Only hotel owners can view applicants'}), 403

        # Verify job exists
        job_ref = db.collection('hhs_app_data').document('users').collection('Hotel').document(hotel_owner_id).collection('PostedJobs').document(job_id)
        job = job_ref.get()
        if not job.exists:
            print(f"Job with ID {job_id} for hotel_owner_id {hotel_owner_id} not found")
            return jsonify({'error': 'Job not found'}), 404

        # Fetch applicants from Firestore
        applicants_ref = job_ref.collection('applicants')
        applicants = applicants_ref.get()

        # Prepare response data
        applicants_data = []
        for applicant in applicants:
            applicant_data = applicant.to_dict()
            # Convert timestamps to strings
            for key, value in applicant_data.items():
                if isinstance(value, datetime.datetime):
                    applicant_data[key] = value.isoformat()
                elif isinstance(value, dict):  # Handle nested profile_snapshot
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, datetime.datetime):
                            applicant_data[key][sub_key] = sub_value.isoformat()
            applicants_data.append(applicant_data)

        print(f"Retrieved {len(applicants_data)} applicants for job {job_id} by hotel_owner_id {hotel_owner_id}")
        return jsonify({
            'message': 'Applicants retrieved successfully',
            'hotel_owner_id': hotel_owner_id,
            'job_id': job_id,
            'data': applicants_data
        }), 200

    except Exception as e:
        # Log the exception for debugging
        print(f"An error occurred in get_applied_jobseekers: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500