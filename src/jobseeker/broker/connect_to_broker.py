from flask import request, jsonify
from src.db import db
from firebase_admin import firestore

def link_seeker_to_broker():
    """
    Connects a job seeker to a broker using the broker's unique code.
    """
    try:
        data = request.get_json()
        job_seeker_id = data.get('job_seeker_id')
        broker_code = data.get('broker_code')

        if not job_seeker_id or not broker_code:
            return jsonify({'error': 'job_seeker_id and broker_code are required'}), 400

        # Verify the job seeker exists
        seeker_auth_ref = db.collection('hhs_app').document('users').collection('Job Seeker').document(job_seeker_id)
        if not seeker_auth_ref.get().exists:
            return jsonify({'error': 'Job Seeker not found.'}), 404

        # Find the broker using the unique code from the master list
        code_master_ref = db.collection('broker_codes').document(broker_code.upper())
        code_doc = code_master_ref.get()
        if not code_doc.exists:
            return jsonify({'error': 'Invalid broker code provided.'}), 404
        
        broker_id = code_doc.to_dict().get('broker_id')

        # Use a transaction to ensure both writes succeed or neither do
        @firestore.transactional
        def update_in_transaction(transaction, broker_id, job_seeker_id):
            # 1. Add broker info to the Job Seeker's record
            seeker_broker_ref = db.collection('hhs_app_data').document('users').collection('Job Seeker').document(job_seeker_id).collection('Broker').document('details')
            transaction.set(seeker_broker_ref, {
                'broker_id': broker_id,
                'is_connected': True,
                'linked_at': firestore.SERVER_TIMESTAMP
            })

            # 2. Add Job Seeker's ID to the Broker's list of seekers
            broker_seeker_ref = db.collection('hhs_app_data').document('users').collection('Broker').document(broker_id).collection('Job_Seekers').document(job_seeker_id)
            transaction.set(broker_seeker_ref, {
                'linked_at': firestore.SERVER_TIMESTAMP
            })
        
        transaction = db.transaction()
        update_in_transaction(transaction, broker_id, job_seeker_id)

        print(f"Job Seeker {job_seeker_id} successfully linked to broker {broker_id}")
        return jsonify({'message': 'Successfully connected to broker.', 'broker_id': broker_id}), 200

    except Exception as e:
        print(f"An error occurred in link_seeker_to_broker: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500