"""
Prompt module for cover letter generation.
"""
# System prompt defines the AI's role and capabilities
COVER_LETTER_SYSTEM = """
    You are an expert career assistant specializing in writing cover letters.
    You excel in highlighting relevant skills and experiences that match job requirements.
    You cover letters are professional, concise, and compelling.
"""

# User prompt contains the specific task and formatting instructions
COVER_LETTER_USER = """
    Write a professional cover letter for the following job offer and user profile:

    Job offer: 
    {job_details}
    
    User profile:
    {user_profile}

    Tone: Professional and concise

    Output format:
    {output_format}

    Example cover letters for reference:

    EXAMPLE 1 - Junior Backend Developer:
    Dear Hiring Manager,

    I am writing to express my interest in the Backend Developer position I found on [Platform]. As a recent graduate with a B.Sc. in Computer Science from State University, I have developed a strong foundation in Python and web development frameworks, particularly Django and Flask.

    During my academic career, I completed a capstone project where I built a RESTful API for a campus events platform, integrating PostgreSQL and Docker for deployment. I am eager to bring my passion for clean code and scalable backend systems to [Company Name].

    I am excited about the opportunity to contribute to your team and further develop my skills in cloud-based backend solutions. My resume is attached for your review. I look forward to the possibility of discussing my fit for this role.

    Sincerely,
    Alex Kim

    EXAMPLE 2 - Senior Full-Stack Engineer:
    Dear Hiring Team,

    I am excited to apply for the Full-Stack Engineer role at [Company Name], as advertised on [Platform]. With over 7 years of experience building robust web applications, I have developed deep expertise in both frontend (React, Redux) and backend (Node.js, Express) technologies.

    At my current position with TechWave, I led a team to deliver a multi-tenant SaaS platform, optimizing performance and enhancing security. My contributions to open-source projects, including improvements to a popular React component library, reflect my commitment to community and code quality.

    I am particularly drawn to [Company Name]'s mission to innovate in the fintech space and would love to bring my experience in scalable architectures to your engineering team. Please find my resume attached. I am available at your convenience for an interview.

    Best regards,
    Priya Desai

    Guidelines:
    - Focus on matching user's experience and skills to the job requirements
    - Use concise language and avoid repetition (300-400 words)
    - Highlight key achievements and experiences
    - Tailor the cover letter to the specific job and company
    - Proofread for grammar and spelling errors
    - Show enthusiasm and passion for the job and company
    - Include a call to action in the closing paragraph
"""



