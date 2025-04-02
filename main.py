from fastapi import FastAPI
from app.api import api_router
from app.db import create_tables


# Create Database tables 
create_tables()

app = FastAPI(title="AI Cover Letter Generator")

# Include API router
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Letter Generator API"}

@app.post("/recreate-tables")
def recreate_tables():
    from app.db import create_tables
    create_tables()
    return {"message": "Tables recreated successfully"}