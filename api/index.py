from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
import sys
import os
import json
import uuid
import asyncio

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Add the parent directory to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "app"))

from app.nlp_sql import parse_query
from app.db import run_query
from app.hybrid_search import semantic_product_search, semantic_customer_search
from app.main import rewrite_query_with_llm

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
    session_id: str

class NewSessionRequest(BaseModel):
    title: str = "New Chat"

CHAT_HISTORY_FILE = os.path.join(root_dir, "app", "chat_history.json")

def load_chat_sessions():
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading chat sessions: {e}")
            return {}
    return {}

def save_chat_sessions(sessions):
    try:
        with open(CHAT_HISTORY_FILE, "w") as f:
            json.dump(sessions, f)
    except Exception as e:
        print(f"Error saving chat sessions: {e}")

@app.get("/api/sessions")
def get_sessions():
    return load_chat_sessions()

@app.post("/api/sessions/new")
def create_session(req: NewSessionRequest):
    sessions = load_chat_sessions()
    new_id = str(uuid.uuid4())
    sessions[new_id] = {
        "title": req.title,
        "messages": [{"role": "assistant", "content": "Hello! I can help you query the database. Ask me about products, customers, or orders.", "data": None}],
        "context_entity": None
    }
    save_chat_sessions(sessions)
    return {"session_id": new_id, "session": sessions[new_id]}

async def stream_words(text: str, data: Any = None, msg_type: str = "text"):
    words = text.split(" ")
    for i, word in enumerate(words):
        chunk = word + (" " if i < len(words) - 1 else "")
        # Send word by word
        payload = {"text": chunk}
        # Attach data only on the last chunk
        if i == len(words) - 1:
            payload["data"] = data
            payload["type"] = msg_type
        
        yield f"data: {json.dumps(payload)}\n\n"
        await asyncio.sleep(0.04)

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    query = request.message
    session_id = request.session_id
    
    sessions = load_chat_sessions()
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    current_session = sessions[session_id]
    
    # Update title if it's new
    if current_session["title"] == "New Chat":
        current_session["title"] = query[:20] + ("..." if len(query) > 20 else "")
        
    current_session["messages"].append({"role": "user", "content": query, "data": None})
    
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

    async def event_generator():
        try:
            if conversational_reply:
                async for chunk in stream_words(conversational_reply):
                    yield chunk
                current_session["messages"].append({"role": "assistant", "content": conversational_reply, "data": None})
                save_chat_sessions(sessions)
                return

            response_text = "I wasn't able to find a direct answer to that in the database. Could you try rephrasing?"
            results_found = False
            response_data = None
            msg_type = "text"
            
            # Application Logic
            sql, params, extracted_entity = parse_query(query)
            
            # Option A: Rule-Based Context Injection
            if not sql or (not params and len(query.split()) < 5 and current_session.get("context_entity")):
                pronouns = ["he", "him", "his", "she", "her", "hers", "they", "them", "their", "it", "that", "this"]
                has_pronoun = any(p in query.lower().split() for p in pronouns)
                
                if has_pronoun or not sql:
                    ctx = current_session["context_entity"]
                    if ctx:
                        injected_prompt = f"{query} for {ctx['type']} {ctx['value']}"
                        sql_inj, params_inj, ext_inj = parse_query(injected_prompt)
                        if sql_inj and params_inj:
                            sql, params, extracted_entity = sql_inj, params_inj, ext_inj
                            
            # Option B: LLM Fallback Rewrite
            if not sql or (not params and len(query.split()) < 5):
                rewritten_prompt = rewrite_query_with_llm(query, current_session["messages"])
                if rewritten_prompt and rewritten_prompt.lower() != query.lower():
                    sql_llm, params_llm, ext_llm = parse_query(rewritten_prompt)
                    if sql_llm:
                        sql, params, extracted_entity = sql_llm, params_llm, ext_llm
            
            if extracted_entity:
                current_session["context_entity"] = extracted_entity
                
            if sql:
                import pandas as pd
                df = run_query(sql, params)
                if not df.empty:
                    response_data = df.to_dict(orient="records")
                    response_text = f"Found {len(df)} results via SQL."
                    results_found = True
                    msg_type = "table"
                else:
                    response_text = "Executed SQL but found no results."
            
            if not results_found:
                ql = query.lower()
                import pandas as pd
                if "product" in ql or "price" in ql or "item" in ql:
                    df = semantic_product_search(query)
                    if not df.empty:
                         response_data = df.to_dict(orient="records")
                         response_text = "Found semantic matches for products."
                         results_found = True
                         msg_type = "table"
                elif "customer" in ql or "order" in ql:
                    df = semantic_customer_search(query)
                    if not df.empty:
                         response_data = df.to_dict(orient="records")
                         response_text = "Found semantic matches for customers."
                         results_found = True
                         msg_type = "table"
                         
            async for chunk in stream_words(response_text, response_data, msg_type):
                yield chunk
                
            current_session["messages"].append({"role": "assistant", "content": response_text, "data": response_data})
            save_chat_sessions(sessions)
            
        except Exception as e:
            print(f"Error processing request: {e}")
            yield f"data: {json.dumps({'text': 'An error occurred while processing your request.', 'type': 'error'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
