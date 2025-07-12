from flask import jsonify, request # Import request object
from src.db import db

def get_applied_jobs():
    """
    Retrieves applied jobs using a user_id from query parameters.
    e.g., /applied-jobs?user_id=some_user_id
    """
    try:
        # Get user_id from query parameter instead of URL path
        user_id = request.args.get('user_id') 

        if not user_id:
            return jsonify({'error': 'The user_id query parameter is required'}), 400

        # --- The rest of the logic remains exactly the same ---

        applied_jobs_ref = db.collection('hhs_app_data').document('users').collection('Job Seeker').document(user_id).collection('applied_jobs')
        
        applied_job_docs = applied_jobs_ref.order_by('applied_at', direction='DESCENDING').stream()

        applied_jobs_list = []
        for doc in applied_job_docs:
            app_data = doc.to_dict()
            job_id = app_data.get('job_id')
            hotel_owner_id = app_data.get('hotel_owner_id')

            if not job_id or not hotel_owner_id:
                continue

            job_ref = db.collection('hhs_app_data').document('users').collection('Hotel').document(hotel_owner_id).collection('PostedJobs').document(job_id)
            job_doc = job_ref.get()

            if not job_doc.exists:
                continue 

            job_details = job_doc.to_dict()
            job_details['job_id'] = job_id
            job_details['hotel_owner_id'] = hotel_owner_id

            applicant_ref = job_ref.collection('applicants').document(user_id)
            applicant_doc = applicant_ref.get()
            
            if applicant_doc.exists:
                status_details = applicant_doc.to_dict()
                job_details['application_status'] = status_details.get('status', 'N/A')
                job_details['status_updated_at'] = status_details.get('status_updated_at')
                job_details['applied_at'] = status_details.get('applied_at')
            else:
                job_details['application_status'] = 'Processing'

            applied_jobs_list.append(job_details)

        print(f"Successfully retrieved {len(applied_jobs_list)} applied jobs for user {user_id}")
        
        return jsonify({
            'message': 'Successfully retrieved applied jobs.',
            'count': len(applied_jobs_list),
            'data': applied_jobs_list
        }), 200

    except Exception as e:
        print(f"An error occurred in get_applied_jobs: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500