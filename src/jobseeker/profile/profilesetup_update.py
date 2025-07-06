# from flask import request, jsonify
# from firebase_admin import firestore
# from src.db import db


# def create_or_update_jobseeker_profile(user_id):
#     try:
#         # Validate user_id
#         if not user_id:
#             return jsonify({'error': 'user_id is required'}), 400

#         # Verify user is a job_seeker
#         user_ref = db.collection('users').document(user_id)
#         user = user_ref.get()
#         if not user.exists or user.to_dict().get('role') != 'job_seeker':
#             return jsonify({'error': 'Unauthorized: Only job seekers can create a profile'}), 403

#         # Get JSON data
#         data = request.json
#         if not data:
#             return jsonify({'error': 'Request body must be JSON'}), 400

#         # Validate mandatory fields
#         mandatory_fields = ['name', 'location']
#         for field in mandatory_fields:
#             if not data.get(field):
#                 return jsonify({'error': f'{field} is required'}), 400

#         # Prepare profile data
#         profile = {
#             'name': data['name'],
#             'location': data['location'],
#             'headline': data.get('headline', ''),
#             'contact_email': user.to_dict().get('email', ''),
#             'phone_number': data.get('phone_number', ''),
#             'linkedin_profile': data.get('linkedin_profile', ''),
#             'portfolio': data.get('portfolio', ''),
#             'experience_years': int(data.get('experience_years', 0)),
#             'availability': data.get('availability', 'Not specified'),
#             'preferred_categories': data.get('preferred_categories', []),
#             'skills': data.get('skills', []),
#             'certifications': data.get('certifications', []),
#             'languages': data.get('languages', []),
#             'resume_url': data.get('resume_url', ''),
#             'profile_updated_at': firestore.SERVER_TIMESTAMP
#         }

#         # Store in Firestore
#         profile_ref = db.collection('HHS').document('Jobseekers').collection('profilesetup').document(user_id)
#         doc_snapshot = profile_ref.get()
#         if not doc_snapshot.exists:
#             profile['profile_created_at'] = firestore.SERVER_TIMESTAMP

#         profile_ref.set(profile, merge=True)

#         # Prepare response data
#         response_data = {
#             'user_id': user_id,
#             'name': profile['name'],
#             'location': profile['location'],
#             'headline': profile['headline'],
#             'contact_email': profile['contact_email'],
#             'phone_number': profile['phone_number'],
#             'linkedin_profile': profile['linkedin_profile'],
#             'portfolio': profile['portfolio'],
#             'experience_years': profile['experience_years'],
#             'availability': profile['availability'],
#             'preferred_categories': profile['preferred_categories'],
#             'skills': profile['skills'],
#             'certifications': profile['certifications'],
#             'languages': profile['languages'],
#             'resume_url': profile['resume_url']
#         }

#         return jsonify({
#             'message': 'Profile successfully saved',
#             'user_id': user_id,
#             'data': response_data
#         }), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


from flask import request, jsonify
from firebase_admin import firestore
import datetime
from src.db import db

def create_or_update_jobseeker_profile():
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            print("No request body provided")
            return jsonify({'error': 'Request body must be JSON'}), 400

        # Validate required fields
        required_fields = [
            'First name', 'Last name', 'headline', 'location', 'contact_email',
            'phone_number', 'linkedin_profile', 'portfolio', 'experience_years',
            'availability', 'preferred_categories', 'Qualifications', 'College Name',
            'Year of Passout', 'Grade', 'skills', 'certifications', 'languages', 'resume_url'
        ]
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            print(f"Missing required fields: {missing_fields}")
            return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400

        # Validate user_id
        user_id = data.get('user_id')
        if not user_id:
            print("No user_id provided")
            return jsonify({'error': 'user_id is required'}), 400

        # Verify user is a job seeker
        user_ref = db.collection('hhs_app').document('users').collection('Job Seeker').document(user_id)
        user = user_ref.get()
        if not user.exists:
            print(f"User with ID {user_id} does not exist")
            return jsonify({'error': 'User not found'}), 404
        user_role = user.to_dict().get('role')
        if user_role != 'Job Seeker':
            print(f"Unauthorized access: Expected role 'Job Seeker', found '{user_role}'")
            return jsonify({'error': 'Unauthorized: Only job seekers can create or update a profile'}), 403

        # Copy user data
        user_data = user.to_dict()
        profile_data = {
            'email': user_data.get('email'),
            'fullName': user_data.get('fullName'),
            'isEmailVerified': user_data.get('isEmailVerified'),
            'phone': user_data.get('phone'),
            'role': user_data.get('role'),
            'uid': user_data.get('uid'),
            'first_name': data.get('First name'),
            'last_name': data.get('Last name'),
            'headline': data.get('headline'),
            'location': data.get('location'),
            'contact_email': data.get('contact_email'),
            'phone_number': data.get('phone_number'),
            'linkedin_profile': data.get('linkedin_profile'),
            'portfolio': data.get('portfolio'),
            'experience_years': data.get('experience_years'),
            'availability': data.get('availability'),
            'preferred_categories': data.get('preferred_categories'),
            'qualifications': data.get('Qualifications'),
            'college_name': data.get('College Name'),
            'year_of_passout': data.get('Year of Passout'),
            'grade': data.get('Grade'),
            'skills': data.get('skills'),
            'certifications': data.get('certifications'),
            'languages': data.get('languages'),
            'resume_url': data.get('resume_url'),
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }

        # Validate copied fields
        required_copied_fields = ['email', 'fullName', 'isEmailVerified', 'phone', 'role', 'uid']
        missing_copied_fields = [field for field in required_copied_fields if profile_data[field] is None]
        if missing_copied_fields:
            print(f"Missing copied fields from user data: {missing_copied_fields}")
            return jsonify({'error': f'Missing required user data: {missing_copied_fields}'}), 400

        # Store or update profile in Firestore
        profile_ref = db.collection('hhs_app_data').document('users').collection('Job Seeker').document(user_id).collection('profile').document('data')
        if profile_ref.get().exists:
            print(f"Updating existing profile for user {user_id}")
            profile_ref.update(profile_data)
            message = 'Job seeker profile updated successfully'
        else:
            print(f"Creating new profile for user {user_id}")
            profile_ref.set(profile_data)
            message = 'Job seeker profile created successfully'

        # Fetch updated profile data for response
        updated_profile = profile_ref.get().to_dict()
        # Convert timestamps to strings
        for key, value in updated_profile.items():
            if isinstance(value, datetime.datetime):
                updated_profile[key] = value.isoformat()

        # Prepare response data
        response_data = {
            'user_id': user_id,
            'profile': updated_profile
        }

        return jsonify({
            'message': message,
            'user_id': user_id,
            'data': response_data
        }), 200

    except Exception as e:
        # Log the exception for debugging
        print(f"An error occurred in create_or_update_jobseeker_profile: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500