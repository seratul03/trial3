"""
Database configuration and session management
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base
import os

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./college_chatbot.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    # Lightweight schema migration for small changes (e.g., adding new columns)
    # This helps when the code adds a column but the SQLite file was created earlier.
    try:
        if "sqlite" in DATABASE_URL:
            with engine.connect() as conn:
                # Check if announcements table has the `removed` column; add if missing
                result = conn.execute(text("PRAGMA table_info(announcements)"))
                cols = [row[1] for row in result]
                if "removed" not in cols:
                    conn.execute(text("ALTER TABLE announcements ADD COLUMN removed BOOLEAN DEFAULT 0"))
    except Exception:
        # If migration fails, ignore — the app will still attempt to operate and show errors
        pass

    print("Database initialized successfully!")
