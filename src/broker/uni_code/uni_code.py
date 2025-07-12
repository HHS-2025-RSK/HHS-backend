import string
import secrets
from flask import request, jsonify
from firebase_admin import firestore
from src.db import db

def generate_broker_code():
    """
    Generates a unique, shareable code for a broker to onboard job seekers.
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is a required field'}), 400

        # Verify the user is a legitimate broker
        broker_auth_ref = db.collection('hhs_app').document('users').collection('Broker').document(user_id)
        if not broker_auth_ref.get().exists:
            return jsonify({'error': 'Unauthorized: User is not a valid broker.'}), 403

        # Check if a code already exists for this broker
        code_ref = db.collection('hhs_app_data').document('users').collection('Broker').document(user_id).collection('uni_code').document('code')
        existing_code = code_ref.get()
        if existing_code.exists:
            return jsonify({'message': 'Broker already has a code.', 'code': existing_code.to_dict().get('code')}), 200

        # Generate a unique code
        alphabet = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(alphabet) for _ in range(6))
            # Check for uniqueness in the master list
            code_master_ref = db.collection('broker_codes').document(code)
            if not code_master_ref.get().exists:
                break
        
        # Store the code in two places for efficient lookup
        code_payload = {'code': code, 'broker_id': user_id, 'generated_at': firestore.SERVER_TIMESTAMP}
        
        # 1. In the master list for reverse lookup
        code_master_ref.set(code_payload)
        
        # 2. In the broker's own data
        code_ref.set(code_payload)

        print(f"Generated unique code {code} for broker {user_id}")
        return jsonify({'message': 'Unique code generated successfully.', 'code': code}), 200

    except Exception as e:
        print(f"An error occurred in generate_broker_code: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500