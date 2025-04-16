import requests
import json

# API endpoint
API_URL = "http://localhost:8000/api/cover-letters/"

# Test data
user_id = 1
job_id = 1

# Create payload with minimal data to trigger AI cover letter generation
payload = {
    "template_name": "AI Generated Cover Letter"
}

# Query parameters
params = {
    "user_id": user_id,
    "job_id": job_id
}

# Send request
try:
    response = requests.post(API_URL, json=payload, params=params)
    
    # Print result
    print(f"Status code: {response.status_code}")
    if response.status_code in (200, 201):
        print("Cover letter generated successfully!")
        result = response.json()
        print("\n--- COVER LETTER ---\n")
        print(result['cover_letter_text'])
    else:
        print(f"Failed to generate cover letter: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Error: {str(e)}")