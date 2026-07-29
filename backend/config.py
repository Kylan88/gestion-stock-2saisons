"""
Configuration de la base de donnees (PostgreSQL / SQLite).
Lit les variables d'environnement depuis .env
"""
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def get_db_url() -> str:
    """Retourne l'URL de connexion."""
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    db_path = os.getenv("DB_PATH", "saisons_stock.db")
    print(f"[INFO] Fallback SQLite ({db_path})")
    return f"sqlite:///{db_path}"

def get_db_config() -> dict:
    """Config moteur SQLAlchemy selon le type de base."""
    url = get_db_url()
    echo = os.getenv("DB_ECHO", "false").lower() == "true"
    config = {"url": url, "echo": echo}
    if url.startswith("postgresql"):
        config["pool_size"] = int(os.getenv("DB_POOL_SIZE", "5"))
        config["max_overflow"] = int(os.getenv("DB_MAX_OVERFLOW", "10"))
        config["pool_pre_ping"] = True
        config["pool_recycle"] = 3600
    return config

DATABASE_URL = get_db_url()
DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"
