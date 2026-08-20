from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

db_url = settings.DATABASE_URL

# Attempt PostgreSQL connection with 3-second timeout, fall back to local SQLite database if PostgreSQL is unavailable
try:
    if db_url.startswith("sqlite"):
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(db_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
        # Test connection quickly
        with engine.connect() as conn:
            pass
except Exception as e:
    print(f"PostgreSQL connection unavailable ({e}). Falling back to local SQLite database (ott_discovery.db).")
    sqlite_url = "sqlite:///./ott_discovery.db"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
