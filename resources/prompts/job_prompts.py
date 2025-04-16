"""
Prompts for job-related AI operations.
"""

# System prompt defines the AI's role and capabilities
JOB_EXTRACTION_SYSTEM = """
You are a specialized job data extraction assistant. Your task is to accurately extract key information 
from job descriptions. You excel at identifying job titles, company names, and locations from 
unstructured text. You always return data in clean, structured JSON format.
"""

# User prompt contains the specific task and formatting instructions
JOB_EXTRACTION_USER = """
Extract the following information from the job offer:
- Job title (the specific role being advertised)
- Company name (the organization offering the job)
- Location (city, state, or country where the job is located)

Job offer: {job_data}

Return ONLY a valid JSON object with this exact format:
{{
    "title": "The exact job title",
    "company": "The company name",
    "location": "The job location"
}}

Do not include any explanations or markdown formatting in your response.
"""

# Example for few-shot learning (optional)
JOB_EXTRACTION_EXAMPLE = {
    "job_description": "Software Engineer at Google in Mountain View, CA. We are looking for talented engineers...",
    "expected_output": {
        "title": "Software Engineer",
        "company": "Google",
        "location": "Mountain View, CA"
    }
}