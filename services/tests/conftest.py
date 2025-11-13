import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.main import app
from app.database import Base
from app.dependencies import get_db

# --- Test Database Setup ---
# Use the test database file
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_v1.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Fixture to manage database tables ---
@pytest.fixture(scope="function")
def db_session():
    """
    Create a new database session for a test, with clean tables.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables
        Base.metadata.drop_all(bind=engine)

# --- Fixture to override the get_db dependency ---
@pytest.fixture(scope="function")
def client(db_session):
    """
    Get a TestClient instance that uses the test database.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    # Set TESTING mode to disable rate limiting
    os.environ["TESTING"] = "true"
    
    yield TestClient(app)

    # Clean up
    del app.dependency_overrides[get_db]
    os.environ["TESTING"] = "false"
