"""SQLAlchemy database configuration and session management.

This module re-exports SQLAlchemy database utilities from sql_service.
"""

# Re-export database utilities
from api.db.sql_service.database import (
    Base, engine, get_db, get_db_session, session_context,
    initialize_database, SessionLocal, ScopedSession
) 