import requests
import json
import os
from pathlib import Path

# API endpoint
API_URL = "http://127.0.0.1:8000/api/jobs/"

# Function to read job description from file
def read_job_description(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Get job description from your sample file
job_file = Path("resources/jobs/raw/job_01.md")
job_description = read_job_description(job_file)

# Create payload: only essential fields
payload = {
    "description": job_description,
    "user_id": 2
}

# Print payload for debugging
print("Sending payload:")
print(json.dumps(payload, indent=2))

# Send request
try:
    response = requests.post(API_URL, json=payload)

    # Print result
    print(f"\nStatus code: {response.status_code}")
    if response.status_code in (200, 201):
        print("Job created successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed to create job: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Error: {str(e)}")
