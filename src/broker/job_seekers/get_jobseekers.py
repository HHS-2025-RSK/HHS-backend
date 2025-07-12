from flask import request, jsonify
from src.db import db

def get_broker_job_seekers():
    """
    Retrieves a list of all job seekers managed by a specific broker.
    Uses user_id from query parameter, e.g., /broker/job-seekers?user_id=...
    """
    try:
        broker_id = request.args.get('user_id')
        if not broker_id:
            return jsonify({'error': 'The user_id query parameter is required'}), 400
        
        # Verify the user is a legitimate broker
        broker_auth_ref = db.collection('hhs_app').document('users').collection('Broker').document(broker_id)
        if not broker_auth_ref.get().exists:
            return jsonify({'error': 'Unauthorized: User is not a valid broker.'}), 403

        # Get the list of job seeker IDs from the broker's subcollection
        seekers_ref = db.collection('hhs_app_data').document('users').collection('Broker').document(broker_id).collection('Job_Seekers')
        seeker_docs = seekers_ref.stream()
        
        job_seeker_ids = [doc.id for doc in seeker_docs]
        
        if not job_seeker_ids:
            return jsonify({'message': 'No job seekers are currently linked to this broker.', 'data': []}), 200

        # Fetch the profile for each job seeker
        seekers_list = []
        for seeker_id in job_seeker_ids:
            # As per your structure, the profile is in hhs_app, not hhs_app_data
            profile_ref = db.collection('hhs_app').document('users').collection('Job Seeker').document(seeker_id)
            profile_doc = profile_ref.get()
            if profile_doc.exists:
                seekers_list.append(profile_doc.to_dict())

        return jsonify({
            'message': 'Successfully retrieved linked job seekers.',
            'count': len(seekers_list),
            'data': seekers_list
        }), 200

    except Exception as e:
        print(f"An error occurred in get_broker_job_seekers: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500