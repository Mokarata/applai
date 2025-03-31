from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Cover Letter Generator", description="Generate cover letters using AI", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Cover Letter Generator!"}

