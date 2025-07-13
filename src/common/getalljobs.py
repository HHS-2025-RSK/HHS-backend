from flask import request, jsonify
from firebase_admin import firestore
from src.db import db

def get_all_hotels_jobs():
    try:
        # Get user_id from query parameters
        user_id = request.args.get('user_id')
        if not user_id:
            print("No user_id provided in query parameters")
            return jsonify({'error': 'user_id is required'}), 400

        # Log the user_id for debugging
        print(f"Attempting to fetch user with ID: {user_id}")

        # === MODIFICATION 1: Find user in EITHER 'Job Seeker' or 'Broker' collection ===
        user_doc = None
        # We will check both collections to find the user
        for collection_name in ['Job Seeker', 'Broker']:
            user_ref = db.collection('hhs_app').document('users').collection(collection_name).document(user_id)
            user = user_ref.get()
            if user.exists:
                user_doc = user  # User was found, save the document
                print(f"User found in collection: {collection_name}")
                break # Stop searching
        
        # The original check, but now using 'user_doc' which we searched for
        if not user_doc:
            print(f"User with ID {user_id} does not exist in Job Seeker or Broker collections")
            return jsonify({'error': 'User not found'}), 404
        
        user_data = user_doc.to_dict()
        user_role = user_data.get('role')
        print(f"User role for {user_id}: {user_role}")
        
        # === MODIFICATION 2: Authorize EITHER 'Job Seeker' or 'Broker' role ===
        allowed_roles = ['Job Seeker', 'Broker']
        if user_role not in allowed_roles:
            print(f"Unauthorized access: Expected roles {allowed_roles}, found '{user_role}'")
            return jsonify({'error': 'Unauthorized: Only job seekers and brokers can view jobs'}), 403

        # Get query parameters for filtering
        location = request.args.get('location')
        job_type = request.args.get('job_type')
        status = request.args.get('status')  # No default filter

        # Log applied filters
        print(f"Filters - status: {status}, location: {location}, job_type: {job_type}")

        # Use collection group query to fetch all PostedJobs subcollections
        query = db.collection_group('PostedJobs')
        query_path = "hhs_app_data/users/Hotel/*/PostedJobs"
        print(f"Querying all PostedJobs subcollections at path: {query_path}")

        # Apply filters if provided
        if status:
            query = query.where('status', '==', status)
        if location:
            query = query.where('location', '==', location)
        if job_type:
            query = query.where('job_type', '==', job_type)

        # Fetch jobs
        jobs = query.stream()
        job_list = []
        jobs_found = 0

        for job in jobs:
            jobs_found += 1
            job_data = job.to_dict()
            # Extract hotel_id from the document path
            # Path format: hhs_app_data/users/Hotel/<hotel_id>/PostedJobs/<job_id>
            path_parts = job.reference.path.split('/')
            hotel_id = path_parts[-3]  # Hotel ID is third from the end
            job_data['hotel_id'] = hotel_id
            job_list.append({'id': job.id, **job_data})
        
        print(f"Found {jobs_found} jobs across all hotels")

        # --- THIS IS YOUR ORIGINAL FALLBACK LOGIC, IT IS PRESERVED ---
        if not job_list:
            print("No jobs found, trying alternative collection names")
            for alt_collection in ['hotel', 'HOTEL']:
                alt_query = db.collection('hhs_app_data').document('users').collection(alt_collection)
                alt_hotels = alt_query.stream()
                alt_hotel_ids = [h.id for h in alt_hotels]
                if alt_hotel_ids:
                    print(f"Found hotels in alternative collection /{alt_collection}: {alt_hotel_ids}")
                    for hotel_id in alt_hotel_ids:
                        query = alt_query.document(hotel_id).collection('PostedJobs')
                        query_path = f"hhs_app_data/users/{alt_collection}/{hotel_id}/PostedJobs"
                        print(f"Querying jobs at path: {query_path}")
                        if status:
                            query = query.where('status', '==', status)
                        if location:
                            query = query.where('location', '==', location)
                        if job_type:
                            query = query.where('job_type', '==', job_type)
                        jobs = query.stream()
                        for job in jobs:
                            job_data = job.to_dict()
                            job_data['hotel_id'] = hotel_id
                            job_list.append({'id': job.id, **job_data})

        if not job_list:
            print("No jobs found across all hotels or alternative collections")
            return jsonify({'error': 'No jobs found'}), 404

        print(f"Retrieved {len(job_list)} jobs across all hotels for user {user_id}: {job_list}")
        return jsonify(job_list), 200

    except Exception as e:
        # Log the exception for debugging
        print(f"An error occurred in get_all_hotels_jobs: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500