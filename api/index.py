from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
import sys
import os

from fastapi.middleware.cors import CORSMiddleware

# Add the parent directory to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "app"))

from app.nlp_sql import parse_query
from app.db import run_query
from app.hybrid_search import semantic_product_search, semantic_customer_search

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    text: str
    data: Optional[List[dict]] = None
    type: str = "text" # "text", "table", "error"

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    query = request.message
    
    # 1. Smart Chat / Greetings
    # We reuse the logic from app/main.py
    # Note: We need to make sure get_conversational_response is importable
    # If app/main.py has global code (st.set_page_config), importing it might run it.
    # Ideally, we should refactor get_conversational_response to a separate util, 
    # but to keep HF unchanged, I will duplicate the simple logic here OR import it if safe.
    # Looking at app/main.py, it runs code at module level. Importing it WILL cause Streamlit errors.
    # So I will DUPLICATE the conversational logic here to be safe and avoid touching app/main.py.
    
    # --- DUPLICATED LOGIC START ---
    text = query.lower()
    conversational_reply = None
    
    greetings = ["hi", "hello", "hey", "hola", "good morning", "good evening", "greetings"]
    if any(text.startswith(g) for g in greetings):
        import random
        conversational_reply = random.choice([
            "Hello there! How can I help you with the database today?",
            "Hi! Ask me anything about our products or orders.",
            "Greetings! I'm ready to search the database for you.",
            "Hello! I'm listening."
        ])
    elif "how are you" in text:
        conversational_reply = "I'm just a computer program, but I'm fully operational and ready to help you query your data!"
    elif "help" in text or "what can you do" in text:
        conversational_reply = "I can help you find information in your database. You can ask things like:\n- 'Show me all orders from John Doe'\n- 'Find products related to sports'\n- 'Who is our top customer?'"
    elif "who are you" in text or "what are you" in text:
        conversational_reply = "I am an AI assistant powered by PostgreSQL and pgvector. I translate your natural language questions into SQL queries."
    # --- DUPLICATED LOGIC END ---

    if conversational_reply:
         return ChatResponse(text=conversational_reply, type="text")

    # 2. SQL / Semantic Search
    try:
        # SQL Search
        sql, params, _ = parse_query(query)
        if sql:
            df = run_query(sql, params)
            if not df.empty:
                # Convert DataFrame to JSON-compatible list of dicts
                data_records = df.to_dict(orient="records")
                return ChatResponse(
                    text=f"Found {len(df)} results via SQL.",
                    data=data_records,
                    type="table"
                )
        
        # Semantic Search Fallback
        ql = query.lower()
        semantic_df = None
        search_type = ""
        
        if "product" in ql or "price" in ql:
             semantic_df = semantic_product_search(query)
             search_type = "products"
        elif "customer" in ql or "order" in ql:
             semantic_df = semantic_customer_search(query)
             search_type = "customers"
             
        if semantic_df is not None and not semantic_df.empty:
             data_records = semantic_df.to_dict(orient="records")
             return ChatResponse(
                 text=f"Found semantic matches for {search_type}.",
                 data=data_records,
                 type="table"
             )

        # No results
        return ChatResponse(
            text="I wasn't able to find a direct answer to that in the database. Could you try rephrasing?",
            type="text"
        )
        
    except Exception as e:
        print(f"Error processing request: {e}")
        return ChatResponse(text="An error occurred while processing your request.", type="error")

# Vercel needs 'app' to be exposed
