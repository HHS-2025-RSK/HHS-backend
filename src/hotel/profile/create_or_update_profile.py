from flask import request, jsonify
from firebase_admin import firestore
import datetime
from src.db import db # Assuming 'db' is your initialized Firestore client

def create_or_update_hotel_profile():
    """
    Creates a new hotel profile or updates an existing one.
    This endpoint is idempotent.
    """
    try:
        # --- 1. Get and Validate Request Data ---
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400

        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is a required field'}), 400

        # --- 2. Verify User is a Hotel ---
        user_ref = db.collection('hhs_app').document('users').collection('Hotel').document(user_id)
        user_doc = user_ref.get()
        if not user_doc.exists:
            return jsonify({'error': f'User with ID {user_id} not found or is not a Hotel'}), 404
        
        # --- 3. Validate Required Profile Fields ---
        required_fields = [
            'hotel_name', 'star_rating', 'hotel_type', 'website_url', 
            'address_line_1', 'city', 'state', 'postal_code', 'country',
            'business_registration_number', 'description', 'amenities', 
            'hr_contact_name', 'hr_contact_email'
        ]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # --- 4. Prepare Profile Data ---
        profile_data = {
            # Required Fields
            'hotel_name': data['hotel_name'],
            'star_rating': data['star_rating'],
            'hotel_type': data['hotel_type'],
            'website_url': data['website_url'],
            'address_line_1': data['address_line_1'],
            'city': data['city'],
            'state': data['state'],
            'postal_code': data['postal_code'],
            'country': data['country'],
            'business_registration_number': data['business_registration_number'],
            'description': data['description'],
            'amenities': data['amenities'], # Expects a list of strings
            'hr_contact_name': data['hr_contact_name'],
            'hr_contact_email': data['hr_contact_email'],
            
            # Optional Fields
            'google_maps_link': data.get('google_maps_link'),
            'license_number': data.get('license_number'),
            'year_established': data.get('year_established'),
            'number_of_rooms': data.get('number_of_rooms'),
            'hr_contact_phone': data.get('hr_contact_phone'),
            'logo_url': data.get('logo_url'),
            'gallery_image_urls': data.get('gallery_image_urls', []),

            # Metadata
            'updated_at': firestore.SERVER_TIMESTAMP,
            'profile_status': 'Pending Verification' # Initial status
        }

        # --- 5. Store or Update Profile in Firestore ---
        profile_ref = db.collection('hhs_app_data').document('users').collection('Hotel').document(user_id).collection('profile').document('data')
        
        # Using set with merge=True allows for both creation and update seamlessly
        profile_ref.set(profile_data, merge=True)
        
        # Add 'created_at' only if the document is new
        profile_ref.update({'created_at': firestore.SERVER_TIMESTAMP})

        message = 'Hotel profile updated successfully'
        
        return jsonify({
            'message': message,
            'user_id': user_id,
        }), 200

    except Exception as e:
        print(f"An error occurred in create_or_update_hotel_profile: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500

