"""
Prompt module for cover letter generation.
"""
# System prompt defines the AI's role and capabilities
COVER_LETTER_SYSTEM = """
    You are an expert career assistant specializing in writing cover letters.
    You excel in highlighting relevant skills and experiences that match job requirements.
    You cover letters are professional, concise, and compelling.
"""

# User prompt contains the specific task and formating instructions
COVER_LETTER_USER = """
    Write a professional cover letter for the following job offer and user profile:

    Job offer: 
    {job_details}
    
    User profile:
    {user_profile}

    Tone: Professional and concise

    Output format:
    {output_format}

    Example:
    {example}

    Guidelines:
    - Focus on matching user's experience and skills to the job requirements
    - Use concise language and avoid repetition (300-400 words)
    - Highlight key achievements and experiences
    - Tailor the cover letter to the specific job and company
    - Proofread for grammar and spelling errors
    - Show enthusiasm and passion for the job and company
    - Include a call to action in the colsing paragraph
"""



