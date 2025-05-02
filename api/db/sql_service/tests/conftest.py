"""Test configuration and fixtures for SQL service tests.

This module provides pytest fixtures and configuration for testing the SQL service.
"""

import pytest
from api.db.sql_service.database import initialize_database, get_db_session
from api.db.sql_service.models.models import User, Tenant, UserTenant

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Initialize the database before running tests.
    
    This fixture is automatically used for all tests in the session.
    It ensures the database tables are created before any tests run.
    """
    initialize_database()
    yield

@pytest.fixture
def test_user_data():
    """Fixture providing test user data."""
    return {
        "email": "test@example.com",
        "nickname": "Test User",
        "password": "test_password",
        "is_authenticated": True,
        "is_active": True,
        "is_anonymous": False,
        "status": "1",
        "is_superuser": False
    }

@pytest.fixture
def test_tenant_data():
    """Fixture providing test tenant data."""
    return {
        "name": "Test Tenant",
        "public_key": "test_public_key",
        "llm_id": "test_llm_id",
        "embd_id": "test_embd_id",
        "asr_id": "test_asr_id",
        "img2txt_id": "test_img2txt_id",
        "rerank_id": "test_rerank_id",
        "tts_id": "test_tts_id",
        "parser_ids": "test_parser_ids",
        "credit": 1000,
        "status": "1"
    }

@pytest.fixture
def db_session():
    """Fixture providing a database session."""
    with get_db_session() as session:
        try:
            yield session
        finally:
            # Clean up test data
            session.query(UserTenant).delete()
            session.query(User).delete()
            session.query(Tenant).delete()
            session.commit() 