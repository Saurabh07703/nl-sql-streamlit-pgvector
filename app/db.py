from sqlalchemy import create_engine, text
import pandas as pd
from config import DB_URL

engine = create_engine(DB_URL)

def run_query(sql, params=None):
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

def execute(sql, params=None):
    with engine.begin() as conn:
        conn.execute(text(sql), params or {})
