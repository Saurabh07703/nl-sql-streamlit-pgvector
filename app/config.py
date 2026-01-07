import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Try os.getenv first (local .env)
DB_URL = os.getenv("DATABASE_URL")

# If not found in env, try Streamlit secrets (for Streamlit Cloud)
if not DB_URL:
    try:
        if "DATABASE_URL" in st.secrets:
            DB_URL = st.secrets["DATABASE_URL"]
    except (FileNotFoundError, AttributeError):
        # FileNotFound: secrets.toml not found
        # AttributeError: st.secrets might be not initialized in some contexts (unlikely in streamlit app)
        pass

if not DB_URL:
    # This might fail the app if DB is required immediately
    print("Warning: DATABASE_URL not found in environment or secrets.")
