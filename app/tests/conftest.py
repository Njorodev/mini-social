import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. IMPORT FIX: Rename to avoid 'module' vs 'instance' confusion
from app.main import app as fastapi_app 
from app.db.session import get_db
from app.db.base import Base
import app.db.models 

# 2. POSTGRES CONFIG
# It is best practice to use a dedicated test database
TEST_DATABASE_URL = "postgresql://postgres:anonymous@localhost:5432/test_db"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables in the Postgres test database once."""
    Base.metadata.create_all(bind=engine)
    yield
    # Optional: Base.metadata.drop_all(bind=engine) 

@pytest.fixture
def db_session():
    """Provides a fresh database session for every single test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback() # Rollback ensures Test A doesn't affect Test B
    connection.close()

@pytest.fixture(autouse=True)
def override_get_db(db_session):
    """Overrides the get_db dependency in your routes."""
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass
    # Access dependency_overrides on the FastAPI instance
    fastapi_app.dependency_overrides[get_db] = _get_test_db
    yield
    fastapi_app.dependency_overrides.clear()

@pytest.fixture
def client():
    """Returns a TestClient using the FastAPI instance."""
    with TestClient(fastapi_app) as c:
        yield c

@pytest.fixture
def test_user_token(client):
    """Utility to get a valid token for authenticated routes."""
    # Register a temporary user
    client.post("/auth/register", json={
        "username": "tester", 
        "email": "t@t.com", 
        "password": "password123"
    })
    # Login to get JWT
    response = client.post("/auth/login", data={
        "username": "tester", 
        "password": "password123"
    })
    return response.json().get("access_token")