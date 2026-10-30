import pytest
from httpx import AsyncClient, ASGITransport
from src.studypilot.main import app
from src.studypilot.core.database import SessionLocal, engine, Base
from src.studypilot.models.user import User
from sqlalchemy import delete

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Ensure tables are created before any tests run
    Base.metadata.create_all(bind=engine)
    yield
    # Optional: Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    connection = SessionLocal()
    try:
        yield connection
    finally:
        connection.close()

@pytest.mark.asyncio
async def test_register_user(db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        db.execute(delete(User))
        db.commit()

        payload = {
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User"
        }
        response = await ac.post("/auth/register", json=payload)
        assert response.status_code == 201
        assert response.json()["email"] == "test@example.com"
        assert "id" in response.json()

@pytest.mark.asyncio
async def test_duplicate_registration(db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        db.execute(delete(User))
        db.commit()

        payload = {
            "email": "dup@example.com",
            "password": "password123",
            "full_name": "Duplicate"
        }
        await ac.post("/auth/register", json=payload)
        response = await ac.post("/auth/register", json=payload)
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_login_success(db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        db.execute(delete(User))
        db.commit()

        # Register first
        payload = {
            "email": "login@example.com",
            "password": "password123",
            "full_name": "Login User"
        }
        await ac.post("/auth/register", json=payload)

        # Login using OAuth2 form data
        login_payload = {
            "username": "login@example.com",
            "password": "password123"
        }
        response = await ac.post("/auth/login", data=login_payload)
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_failure(db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        db.execute(delete(User))
        db.commit()

        login_payload = {
            "username": "wrong@example.com",
            "password": "wrongpassword"
        }
        response = await ac.post("/auth/login", data=login_payload)
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect email or password"
