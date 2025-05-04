"""Test configuration and fixtures for SQL service tests.

This module provides pytest fixtures and configuration for testing the SQL service.
"""

import pytest
from api.db.sql_service.database import initialize_database, get_db_session
from api.db.sql_service.models.models import User, Tenant, UserTenant, Conversation, Dialog
from api.db.sql_service.services.tenant_service import TenantService
from api.db.sql_service.services.user_service import UserService
from api.db.sql_service.services.user_tenant_service import UserTenantService
from api.db.sql_service.services.knowledgebase_service import KnowledgebaseService

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Initialize the database before running tests.
    
    This fixture is automatically used for all tests in the session.
    It ensures the database tables are created before any tests run.
    """
    initialize_database()
    yield

@pytest.fixture(scope="function")
def test_tenant(db_session):
    """Fixture providing a test tenant."""
    tenant_data = {
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
    tenant = TenantService.save(session=db_session, **tenant_data)
    return tenant

@pytest.fixture(scope="function")
def test_user(db_session):
    """Fixture providing a test user."""
    user_data = {
        "email": "test@example.com",
        "nickname": "Test User",
        "password": "test_password",
        "is_authenticated": True,
        "is_active": True,
        "is_anonymous": False,
        "status": "1",
        "is_superuser": False
    }
    user = UserService.save(session=db_session, **user_data)
    return user

@pytest.fixture(scope="function")
def test_user_tenant(db_session, test_tenant, test_user):
    """Fixture providing a test user-tenant association."""
    user_tenant_data = {
        "user_id": test_user.id,
        "tenant_id": test_tenant.id,
        "role": "admin",
        "status": "1"
    }
    user_tenant = UserTenantService.save(session=db_session, **user_tenant_data)
    return user_tenant

@pytest.fixture(scope="function")
def test_knowledgebase(db_session, test_tenant, test_user):
    """Fixture providing a test knowledge base."""
    kb_data = {
        "name": "Test Knowledge Base",
        "tenant_id": test_tenant.id,
        "created_by": test_user.id,
        "status": "1",
        "description": "Test knowledge base for testing",
        "embd_id": "test_embedding_model",
        "permission": "me",
        "parser_id": "naive"
    }
    kb = KnowledgebaseService.save(session=db_session, **kb_data)
    return kb

@pytest.fixture(scope="function")
def db_session():
    """Fixture providing a database session.
    
    This fixture is automatically used for all tests.
    It provides a database session that can be used for database operations.
    """
    with get_db_session() as session:
        yield session
        session.rollback() 