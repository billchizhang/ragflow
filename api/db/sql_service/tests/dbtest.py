import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import urllib.parse

from api.db.sql_service.database.sql_server import Base, SessionLocal
from api.db.sql_service.models.user import User, Tenant, UserTenant


# SQL Server connection string components for testing
TEST_SERVER = "asireon-sql-vm.database.windows.net"
TEST_DATABASE = "Asireon-SQL"  # Use a separate test database
TEST_USERNAME = "CloudSA7da9ee8f"
TEST_PASSWORD = "Pzt@9982$"  # Replace with actual password
TEST_PORT = 1433

# Create the test connection URL
test_params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={TEST_SERVER};"
    f"DATABASE={TEST_DATABASE};"
    f"UID={TEST_USERNAME};"
    f"PWD={TEST_PASSWORD};"
    f"PORT={TEST_PORT};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

# Create SQLAlchemy engine for testing
TEST_SQL_SERVER_URL = f"mssql+pyodbc:///?odbc_connect={test_params}"
test_engine = create_engine(TEST_SQL_SERVER_URL, pool_pre_ping=True)

# Create test session factory
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    # Create all tables in the test database
    Base.metadata.create_all(test_engine)
    return test_engine


@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """Create a test session factory."""
    return TestSessionLocal


@pytest.fixture(scope="function")
def db_session(test_session_factory):
    """Create a fresh database session for each test."""
    session = test_session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def clean_db(db_session):
    """Clean the database before each test."""
    # Delete all records from all tables
    db_session.query(UserTenant).delete()
    db_session.query(User).delete()
    db_session.query(Tenant).delete()
    db_session.commit()
    return db_session 