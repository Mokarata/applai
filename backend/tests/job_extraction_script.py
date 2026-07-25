import json
from pathlib import Path

import requests
from app.core.logging import get_logger

logger = get_logger(__name__)

# API endpoint
API_URL = "http://127.0.0.1:8000/api/jobs/"


# Function to read job data from file
def read_job_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# Get job data from your sample file
job_file = Path("resources/jobs/job_01.md")
job_data = read_job_data(job_file)

# Create payload: only essential fields
payload = {"job_data": job_data, "user_id": 1}

# Log payload for debugging
logger.debug("Sending payload: %s", json.dumps(payload, indent=2))

# Send request
try:
    response = requests.post(API_URL, json=payload, timeout=30)

    # Log result
    logger.info("Status code: %s", response.status_code)
    if response.status_code in (200, 201):
        logger.info("Job created successfully!")
        logger.debug("Response: %s", json.dumps(response.json(), indent=2))
    else:
        logger.error("Failed to create job: %s", response.text)
except requests.exceptions.RequestException:
    logger.exception("Error occurred while creating job")
