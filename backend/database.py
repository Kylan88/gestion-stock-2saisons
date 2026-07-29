"""
Moteur SQLAlchemy + SessionLocal.
Usage :
    from database import SessionLocal
    db = SessionLocal()
    try:
        ...
    finally:
        db.close()
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import DATABASE_URL, DB_ECHO, get_db_config

cfg = get_db_config()
url = cfg.pop("url")
engine = create_engine(url, **cfg)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    """Dépendance FastAPI : fournit une session DB par requête."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
