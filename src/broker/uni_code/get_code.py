from flask import request, jsonify
from src.db import db

def get_broker_code():
    """
    Retrieves the unique code for a specific broker.
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'The user_id query parameter is required'}), 400

        # Verify the user is a legitimate broker
        broker_auth_ref = db.collection('hhs_app').document('users').collection('Broker').document(user_id)
        if not broker_auth_ref.get().exists:
            return jsonify({'error': 'User is not a valid broker or does not exist.'}), 403

        # Fetch the code data
        code_ref = db.collection('hhs_app_data').document('users').collection('Broker').document(user_id).collection('uni_code').document('code')
        code_doc = code_ref.get()

        if not code_doc.exists:
            return jsonify({'error': 'A unique code has not been generated for this broker yet.'}), 404

        return jsonify({'message': 'Code retrieved successfully', 'data': code_doc.to_dict()}), 200

    except Exception as e:
        print(f"An error occurred in get_broker_code: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500