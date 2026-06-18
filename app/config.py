import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg2://postgres:Saurabh%4012345@localhost:5432/postgres")

if not DB_URL:
    print("Warning: DATABASE_URL not found.")
