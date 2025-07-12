from flask import request, jsonify
from firebase_admin import firestore
from src.db import db

def create_or_update_broker_profile():
    """
    Creates or updates a broker's professional profile.
    Expects a JSON body with profile information.
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is a required field'}), 400

        # Verify the user is a legitimate broker
        broker_auth_ref = db.collection('hhs_app').document('users').collection('Broker').document(user_id)
        if not broker_auth_ref.get().exists:
            return jsonify({'error': 'Unauthorized: User is not a valid broker or does not exist.'}), 403

        # Prepare profile data from request
        profile_data = {
            'agency_name': data.get('agency_name'),
            'specializations': data.get('specializations', []), # e.g., ["Luxury Hotels", "Restaurant Staff"]
            'years_of_experience': data.get('years_of_experience'),
            'office_address': data.get('office_address'),
            'contact_email': data.get('contact_email'),
            'website': data.get('website'),
            'linkedin_profile': data.get('linkedin_profile'),
            'about': data.get('about'),
            'last_updated': firestore.SERVER_TIMESTAMP
        }

        # Filter out any None values so they don't overwrite existing fields with nulls
        profile_data = {k: v for k, v in profile_data.items() if v is not None}

        if not profile_data:
            return jsonify({'error': 'No profile data provided to update.'}), 400

        # Set the profile data in the specified path
        profile_ref = db.collection('hhs_app_data').document('users').collection('Broker').document(user_id).collection('profile').document('details')
        profile_ref.set(profile_data, merge=True) # merge=True allows for updates

        print(f"Profile for broker {user_id} created/updated successfully.")
        return jsonify({'message': 'Broker profile updated successfully', 'user_id': user_id}), 200

    except Exception as e:
        print(f"An error occurred in create_or_update_broker_profile: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500