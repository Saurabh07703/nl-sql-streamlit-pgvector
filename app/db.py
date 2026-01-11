from sqlalchemy import create_engine, text
import pandas as pd
from config import DB_URL

engine = create_engine(
    DB_URL,
    pool_pre_ping=True,  # Check connection health before usage
    pool_recycle=1800,   # Recycle connections every 30 minutes
    pool_size=10,        # Standard pool size
    max_overflow=20      # Allow temporary bursts
)

def run_query(sql, params=None):
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

def execute(sql, params=None):
    with engine.begin() as conn:
        conn.execute(text(sql), params or {})

def fetch_all(sql, params=None):
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        return result.fetchall()
