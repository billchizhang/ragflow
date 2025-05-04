"""SQLAlchemy database configuration and session management.

This module provides SQLAlchemy engine setup, session factory, and Base class
for model definitions.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from functools import wraps

# Use SQL Server configuration
TEST_SERVER = "asireon-sql-vm.database.windows.net"
TEST_DATABASE = "Asireon-SQL"
TEST_USERNAME = "CloudSA7da9ee8f"
TEST_PASSWORD = "Pzt@9982$"
TEST_PORT = 1433

# Create SQLAlchemy URL for SQL Server
database_url = f"mssql+pyodbc://{TEST_USERNAME}:Pzt%409982%24@{TEST_SERVER}:{TEST_PORT}/{TEST_DATABASE}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=yes&Connection+Timeout=60"
engine = create_engine(database_url, pool_pre_ping=True, connect_args={"timeout": 60})

# Create session factory
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ScopedSession = scoped_session(session_factory)

# Base class for all models
Base = declarative_base()

@contextmanager
def get_db_session():
    """Context manager for database sessions.
    
    Provides a session and handles commit/rollback automatically.
    
    Yields:
        session: SQLAlchemy session
    
    Example:
        with get_db_session() as session:
            user = session.query(User).first()
    """
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def session_context(func):
    """Decorator for providing session to functions.
    
    If the function already has a session parameter, it will use that.
    Otherwise, it will create a new session and pass it to the function.
    
    Args:
        func: Function to decorate
    
    Returns:
        Decorated function
    
    Example:
        @session_context
        def get_user(session, user_id):
            return session.query(User).filter_by(id=user_id).first()
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'session' in kwargs and kwargs['session'] is not None:
            # Use the provided session
            return func(*args, **kwargs)
        else:
            # Create a new session
            with get_db_session() as session:
                kwargs['session'] = session
                return func(*args, **kwargs)
    return wrapper


def initialize_database():
    """Initialize database by creating all tables.
    
    This function creates all tables defined in SQLAlchemy models.
    """
    # Import all models to ensure they are registered with the Base
    from api.db.sql_service.models.models import (
        User, Tenant, UserTenant, Knowledgebase, Document, File,
        File2Document, Dialog, Conversation, InvitationCode
    )
    
    # Create a session to manage transactions
    session = session_factory()
    try:
        # Drop all tables first
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Commit the changes
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_db():
    """Get a database session.
    
    This function is intended for dependency injection in FastAPI.
    
    Yields:
        session: SQLAlchemy session
    
    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = session_factory()
    try:
        yield db
    finally:
        db.close() 