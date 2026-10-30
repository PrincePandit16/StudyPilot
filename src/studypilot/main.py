from fastapi import FastAPI
from src.studypilot.api import auth

app = FastAPI(title="StudyPilot API")

app.include_router(auth.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
