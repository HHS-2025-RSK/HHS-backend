from flask import request, jsonify
from firebase_admin import firestore
import datetime
from src.db import db


def update_application_status():
    try:
        # Get JSON data
        data = request.json
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400

        # Validate required fields
        hotel_owner_id = data.get('hotel_owner_id')
        job_id = data.get('job_id')
        user_id = data.get('user_id')
        status = data.get('status')
        if not hotel_owner_id or not job_id or not user_id or not status:
            return jsonify({'error': 'hotel_owner_id, job_id, user_id, and status are required'}), 400

        # Validate status value
        valid_statuses = ['Pending', 'Interview Scheduled', 'Accepted', 'Rejected']
        if status not in valid_statuses:
            return jsonify({'error': f'status must be one of {valid_statuses}'}), 400

        # Verify user is a hotel_owner
        user_ref = db.collection('users').document(hotel_owner_id)
        user = user_ref.get()
        if not user.exists or user.to_dict().get('role') != 'hotel_owner':
            return jsonify({'error': 'Unauthorized: Only hotel owners can update application status'}), 403

        # Verify job exists
        job_ref = db.collection('HHS').document('hotels').collection(hotel_owner_id).document('posted_jobs').collection('jobs').document(job_id)
        job = job_ref.get()
        if not job.exists:
            return jsonify({'error': 'Job not found'}), 404

        # Verify applicant exists
        applicant_ref = job_ref.collection('applicants').document(user_id)
        applicant = applicant_ref.get()
        if not applicant.exists:
            return jsonify({'error': 'Applicant not found for this job'}), 404

        # Update status in Firestore
        applicant_ref.update({
            'status': status,
            'status_updated_at': firestore.SERVER_TIMESTAMP
        })

        # Fetch updated applicant data
        updated_applicant = applicant_ref.get().to_dict()
        # Convert timestamps to strings
        for key, value in updated_applicant.items():
            if isinstance(value, datetime.datetime):
                updated_applicant[key] = value.isoformat()
            elif isinstance(value, dict):  # Handle nested profile_snapshot
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, datetime.datetime):
                        updated_applicant[key][sub_key] = sub_value.isoformat()

        # Prepare response data
        response_data = {
            'user_id': user_id,
            'job_id': job_id,
            'hotel_owner_id': hotel_owner_id,
            'status': updated_applicant['status'],
            'status_updated_at': updated_applicant.get('status_updated_at')
        }

        return jsonify({
            'message': 'Application status updated successfully',
            'hotel_owner_id': hotel_owner_id,
            'job_id': job_id,
            'user_id': user_id,
            'data': response_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500