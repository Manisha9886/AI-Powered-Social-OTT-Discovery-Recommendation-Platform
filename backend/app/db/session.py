from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

import os
db_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or settings.DATABASE_URL

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Attempt database connection, fall back to local SQLite if primary DB is unavailable
try:
    if db_url and db_url.startswith("sqlite"):
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    elif db_url and ("postgresql" in db_url or "postgres" in db_url):
        engine = create_engine(db_url, pool_pre_ping=True)
        with engine.connect() as conn:
            pass
    else:
        raise ValueError(f"Unsupported database URL scheme")
except Exception as e:
    print(f"Primary database connection note ({e}). Using ott_discovery.db SQLite database.")
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
