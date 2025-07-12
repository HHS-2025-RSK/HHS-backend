from flask import Flask
from flask_cors import CORS
import os

# --- 1. Import your routes using relative paths ---
# The leading dot (.) is the fix.
from .hotel.jobs.create_job import create_job
from .hotel.jobs.get_jobs import get_jobs
from .hotel.jobs.update_job import update_job
from .hotel.jobs.get_appliedjobseekers import get_applied_jobseekers
from .hotel.jobs.update_application_status import update_application_status

from .jobseeker.profile.profilesetup_update import create_or_update_jobseeker_profile
from .jobseeker.profile.getprofile import get_jobseeker_profile
from .jobseeker.jobs.applyjob import apply_job
from .jobseeker.jobs.savedjobs import save_job
from .jobseeker.jobs.get_saved_jobs import get_saved_jobs
from .jobseeker.jobs.getappliedjobs import get_applied_jobs
from .jobseeker.broker.connect_to_broker import link_seeker_to_broker

from .broker.profile.profilesetup_update import create_or_update_broker_profile
from .broker.profile.get_profile import get_broker_profile
from .broker.job_seekers.get_jobseekers import get_broker_job_seekers
from .broker.uni_code.uni_code import generate_broker_code
from .broker.uni_code.get_code import get_broker_code

from .common.getalljobs import get_all_hotels_jobs



# --- 2. Create the Flask App ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv('FRONTEND_URL', '*')}})


# --- 3. Register your routes ---
# This part does not need to change.
# Hotel APIs
app.route('/createjob', methods=['POST'])(create_job)
app.route('/getjobs', methods=['GET'])(get_jobs)
app.route('/editjob/<job_id>', methods=['PUT'])(update_job)
app.route('/hotel/job-applicants', methods=['GET'])(get_applied_jobseekers)
app.route('/hotel/job-applicants/application-status', methods=['POST'])(update_application_status)

# Jobseeker APIs
app.route('/jobseeker/createprofile', methods=['POST'])(create_or_update_jobseeker_profile)
app.route('/jobseeker/getprofile', methods=['GET'])(get_jobseeker_profile)
app.route('/jobseeker/apply-job', methods=['POST'])(apply_job)
app.route('/jobseeker/save-job', methods=['POST'])(save_job)
app.route('/jobseeker/saved-jobs', methods=['GET'])(get_saved_jobs)
app.route('/jobseeker/applied-jobs', methods=['GET'])(get_applied_jobs)
app.route('/jobseeker/connect-to-broker', methods=['POST'])(link_seeker_to_broker)


#Broker APIs
app.route('/broker/broker-profile', methods=['POST'])(create_or_update_broker_profile)
app.route('/broker/get-broker-profile', methods=['GET'])(get_broker_profile)
app.route('/broker/job-seekers', methods=['GET'])(get_broker_job_seekers)
app.route('/broker/create-code', methods=['POST'])(generate_broker_code)
app.route('/broker/get-code', methods=['GET'])(get_broker_code)
#Common APIs
app.route('/get_all_hotels_jobs', methods=['GET'])(get_all_hotels_jobs)


# --- 4. Run the App ---
if __name__ == '__main__':
    # When running with "python -m src.app", this block is not executed.
    # It's only for when you might run "python src/app.py" directly, which causes import errors.
    app.run(host='0.0.0.0', port=8080, debug=True)