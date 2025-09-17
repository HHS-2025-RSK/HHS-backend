from flask import request, jsonify
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename
from src.db import db
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables and configure Cloudinary
load_dotenv()
cloudinary.config(secure=True)

def upload_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400

        resume_file = request.files['resume']
        if resume_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        user_id = request.form.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Secure the filename and upload to Cloudinary
        filename = secure_filename(resume_file.filename)
        upload_result = cloudinary.uploader.upload(
            resume_file,
            folder="resumes",
            resource_type="raw",
            public_id=f"{user_id}/{filename}",
            overwrite=True
        )
        resume_url = upload_result.get('secure_url')

        # Optionally store the URL in Firestore (e.g., for reference)
        resume_ref = db.collection('hhs_app_data').document('users').collection('Job Seeker').document(user_id).collection('resume').document('data')
        resume_ref.set({'resume_url': resume_url, 'updated_at': firestore.SERVER_TIMESTAMP})

        logger.debug(f"Resume uploaded for user {user_id}: {resume_url}")

        return jsonify({'url': resume_url}), 200

    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        return jsonify({'error': 'Failed to upload resume'}), 500