from fastapi import FastAPI
from src.studypilot.api import auth, users, documents, tutor, notes, assessments
from src.studypilot.core.worker_manager import start_worker, stop_worker
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start background worker
    await start_worker()
    yield
    # Shutdown: Stop background worker
    await stop_worker()

app = FastAPI(title="StudyPilot API", lifespan=lifespan)

# API v1 routes
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(tutor.router, prefix="/api/v1")
app.include_router(notes.router, prefix="/api/v1")
app.include_router(assessments.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
