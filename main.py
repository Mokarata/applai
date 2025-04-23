from fastapi import FastAPI
from app.api import api_router

app = FastAPI(title="AI Cover Letter Generator")

# Include API router
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Letter Generator API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

