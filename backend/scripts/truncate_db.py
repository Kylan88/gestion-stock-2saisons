import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    tables = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'")).fetchall()
    for t in tables:
        conn.execute(text(f"TRUNCATE TABLE {t[0]} CASCADE"))
        print(f"Truncated: {t[0]}")
    conn.commit()
print("Done.")
