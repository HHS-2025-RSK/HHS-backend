import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load .env file
load_dotenv() 

# This reads the environment variable you set on Render
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')

# Initialize the app only once
if not firebase_admin._apps:
    if not firebase_credentials_path:
        raise ValueError('The FIREBASE_CREDENTIALS_PATH environment variable is not set.')
    
    cred = credentials.Certificate(firebase_credentials_path)
    firebase_admin.initialize_app(cred)

# Create the db object that the rest of your app will import
db = firestore.client()