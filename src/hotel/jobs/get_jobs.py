from flask import request, jsonify
from firebase_admin import firestore
from src.db import db


def get_jobs():
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Verify user is a hotel_owner
        user_ref = db.collection('users').document(user_id)
        user = user_ref.get()
        if not user.exists or user.to_dict().get('role') != 'hotel_owner':
            return jsonify({'error': 'Unauthorized: Only hotel owners can view jobs'}), 403

        # Get query parameters for filtering
        location = request.args.get('location')
        job_type = request.args.get('job_type')
        status = request.args.get('status', 'open')

        query = db.collection('HHS').document('hotels').collection(user_id).document('posted_jobs').collection('jobs').where('status', '==', status)

        # Apply filters if provided
        if location:
            query = query.where('location', '==', location)
        if job_type:
            query = query.where('job_type', '==', job_type)

        jobs = query.stream()
        job_list = [{'id': job.id, **job.to_dict()} for job in jobs]
        return jsonify(job_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500