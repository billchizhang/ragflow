from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import urllib.parse

# SQL Server connection string components
SERVER = "asireon-sql-vm.database.windows.net"
DATABASE = "Asireon-SQL"
USERNAME = "CloudSA7da9ee8f"
PASSWORD = "Pzt@9982$"  # Replace with actual password
PORT = 1433

# Create the connection URL
params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    f"PORT={PORT};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

# Create SQLAlchemy engine
SQL_SERVER_URL = f"mssql+pyodbc:///?odbc_connect={params}"
engine = create_engine(SQL_SERVER_URL, pool_pre_ping=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 