"""
SQLAlchemy ORM configuration.
Sets up the base and session for SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from .constants import INSTANCE_DIR

# Create base class for SQLAlchemy models
Base = declarative_base()

# Default path for the database
DB_PATH = os.path.join(INSTANCE_DIR, "black_scholes.db")

# Create engine (this doesn't actually connect to the database yet)
engine = create_engine(
    f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}
)

# Create sessionmaker factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    """
    Get a database session.

    Returns
    -------
    SQLAlchemy Session
        A session for database operations
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db(db_path: str = DB_PATH) -> None:
    """
    Initialize the SQLite database with the necessary tables.

    Parameters
    ----------
    db_path : str
        Path to the SQLite database file.
    """
    # Create engine with the specified path
    local_engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )

    # Create all tables
    Base.metadata.create_all(bind=local_engine)
