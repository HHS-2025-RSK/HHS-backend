from flask import request, jsonify
from src.db import db

def get_broker_profile():
    """
    Retrieves the profile for a specific broker using their user_id.
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'The user_id query parameter is required'}), 400

        # Verify the user is a legitimate broker
        broker_auth_ref = db.collection('hhs_app').document('users').collection('Broker').document(user_id)
        if not broker_auth_ref.get().exists:
            return jsonify({'error': 'User is not a valid broker or does not exist.'}), 403

        # Fetch the profile data
        profile_ref = db.collection('hhs_app_data').document('users').collection('Broker').document(user_id).collection('profile').document('details')
        profile_doc = profile_ref.get()

        if not profile_doc.exists:
            return jsonify({'error': 'Broker profile has not been created yet.'}), 404

        return jsonify({'message': 'Profile retrieved successfully', 'data': profile_doc.to_dict()}), 200

    except Exception as e:
        print(f"An error occurred in get_broker_profile: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500
    