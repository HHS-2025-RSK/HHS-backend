from flask import Flask
from flask_cors import CORS
import os

# Hotel APIs
from hotel.jobs.create_job import create_job
from hotel.jobs.get_jobs import get_jobs
from hotel.jobs.update_job import update_job
from hotel.jobs.get_appliedjobseekers import get_applied_jobseekers
from hotel.jobs.update_application_status import update_application_status

# Jobseeker APIs
from jobseeker.profile.profilesetup_update import create_or_update_jobseeker_profile
from jobseeker.profile.getprofile import get_jobseeker_profile
from jobseeker.jobs.applyjob import apply_job
from jobseeker.jobs.savedjobs import save_job
from jobseeker.jobs.get_saved_jobs import get_saved_jobs



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv('FRONTEND_URL', '*')}})

# Register API routes
app.route('/createjob', methods=['POST'])(create_job)
app.route('/getjobs', methods=['GET'])(get_jobs)
app.route('/editjob/<job_id>', methods=['PUT'])(update_job)
app.route('/hotel/job-applicants', methods=['GET'])(get_applied_jobseekers)
app.route('/hotel/job-applicants/application-status', methods=['POST'])(update_application_status)



#jobseeker APIs
app.route('/jobseeker/createprofile/<user_id>', methods=['POST'])(create_or_update_jobseeker_profile)
app.route('/jobseeker/getprofile/<user_id>', methods=['GET'])(get_jobseeker_profile)
app.route('/jobseeker/apply-job', methods=['POST'])(apply_job)
app.route('/jobseeker/save-job', methods=['POST'])(save_job)
app.route('/jobseeker/saved-jobs', methods=['GET'])(get_saved_jobs)



#Broker APIs




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)