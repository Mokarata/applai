import json

import requests

# API endpoint
API_URL = "http://localhost:8000/api/cover-letters/"

# Test data
user_id = 1
job_id = 1

# Create payload with minimal data to trigger AI cover letter generation
payload = {"template_name": "AI Generated Cover Letter"}

# Query parameters
params = {"user_id": user_id, "job_id": job_id}
