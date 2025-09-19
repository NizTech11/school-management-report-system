# Database Configuration for Production
import os
from sqlmodel import create_engine

# Database URL Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///students.db")

# For PostgreSQL (recommended for production)
if DATABASE_URL.startswith("postgresql://"):
    # Convert postgres:// to postgresql:// if needed (Heroku fix)
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql://", 1)

# Create engine with appropriate settings
if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL settings
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300
    )
else:
    # SQLite settings (for development)
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )

# Export the engine
__all__ = ["engine"]