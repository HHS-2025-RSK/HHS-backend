# from flask import jsonify
# from firebase_admin import firestore
# import datetime
# from src.db import db


# def get_jobseeker_profile(user_id):
#     try:
#         # Validate user_id
#         if not user_id:
#             return jsonify({'error': 'user_id is required'}), 400

#         # Fetch profile from Firestore
#         profile_ref = db.collection('HHS_app').document('users').collection('Job Seeker').document(user_id)
#         profile = profile_ref.get()

#         if not profile.exists:
#             return jsonify({'error': 'Profile not found'}), 404

#         # Prepare response data
#         profile_data = profile.to_dict()
        
#         # Convert timestamps to strings
#         for key, value in profile_data.items():
#             if isinstance(value, datetime.datetime):
#                 profile_data[key] = value.isoformat()

#         return jsonify(profile_data), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500



from flask import jsonify, request  # <-- Import request
from firebase_admin import firestore
import datetime
from src.db import db

def get_jobseeker_profile():
    try:
        # ✅ Get user_id from query parameters
        user_id = request.args.get("user_id")

        # Validate user_id
        if not user_id:
            print("No user_id provided")
            return jsonify({'error': 'user_id is required as a query parameter'}), 400

        # Verify user is a job seeker
        user_ref = db.collection('hhs_app').document('users').collection('Job Seeker').document(user_id)
        user = user_ref.get()
        if not user.exists:
            print(f"User with ID {user_id} does not exist")
            return jsonify({'error': 'User not found'}), 404

        user_role = user.to_dict().get('role')
        if user_role != 'Job Seeker':
            print(f"Unauthorized access: Expected role 'Job Seeker', found '{user_role}'")
            return jsonify({'error': 'Unauthorized: Only job seekers can access their profile'}), 403

        # Fetch profile
        profile_ref = db.collection('hhs_app_data').document('users').collection('Job Seeker').document(user_id).collection('profile').document('data')
        profile = profile_ref.get()

        if not profile.exists:
            print(f"Profile not found for user {user_id}")
            return jsonify({'error': 'Profile not found'}), 404

        profile_data = profile.to_dict()

        # Convert timestamps
        for key, value in profile_data.items():
            if isinstance(value, datetime.datetime):
                profile_data[key] = value.isoformat()

        print(f"Profile retrieved successfully for user {user_id}")
        return jsonify({
            'message': 'Job seeker profile retrieved successfully',
            'user_id': user_id,
            'data': profile_data
        }), 200

    except Exception as e:
        print(f"An error occurred in get_jobseeker_profile: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500
