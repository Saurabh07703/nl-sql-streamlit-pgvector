import streamlit as st
import time
import json
import os
import uuid
import random
import pandas as pd
from nlp_sql import parse_query
from db import run_query
from hybrid_search import semantic_product_search, semantic_customer_search
from migration import run_migration
from nlp_sql import parse_query, rewrite_query_with_llm

# 1. Set Page Config (MUST BE FIRST)
st.set_page_config(page_title="NLP SQL Chat", page_icon="💬")

# 2. Run Migration (Once)
@st.cache_resource
def sync_data():
    try:
        run_migration()
    except Exception as e:
        print(f"Migration failed: {e}")

sync_data()

st.title("💬 AI Database Assistant")

# Custom Sidebar CSS to match screenshot exactly
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #11131a;
    }
    
    [data-testid="stSidebar"] div.stButton > button {
        background-color: transparent !important;
        border: none !important;
        color: white !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 15px !important;
        padding-left: 0 !important;
        box-shadow: none !important;
    }
    
    [data-testid="stSidebar"] div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    
    [data-testid="stSidebar"] div.stButton:first-of-type > button {
        justify-content: center !important;
        font-weight: 600 !important;
        padding-top: 15px !important;
        padding-bottom: 15px !important;
    }
    
    [data-testid="stSidebar"] hr {
        margin-top: 0 !important;
        margin-bottom: 25px !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# Setup Chat History File
CHAT_HISTORY_FILE = "app/chat_history.json"

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
            json.dump(sessions, f, default=str)
    except Exception as e:
        print(f"Error saving chat sessions: {e}")

def sync_history_to_disk():
    save_data = {}
    for sid, sdata in st.session_state.chat_sessions.items():
        save_data[sid] = {
            "title": sdata["title"],
            "context_entity": sdata["context_entity"],
            "messages": [
                {
                    "role": m["role"],
                    "content": m["content"],
                    "data": m.get("data").to_dict(orient="records") if isinstance(m.get("data"), pd.DataFrame) else (m.get("data") if isinstance(m.get("data"), list) else None)
                }
                for m in sdata["messages"]
            ]
        }
    save_chat_sessions(save_data)

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = load_chat_sessions()

if "current_session_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.current_session_id = new_id
    st.session_state.chat_sessions[new_id] = {
        "title": "New Chat",
        "messages": [{"role": "assistant", "content": "Hello! I can help you query the database. Ask me about products, customers, or orders.", "data": None}],
        "context_entity": None
    }

current_session = st.session_state.chat_sessions[st.session_state.current_session_id]

# Sidebar Chat Sessions
if st.sidebar.button("+ New Chat", use_container_width=True):
    new_id = str(uuid.uuid4())
    st.session_state.current_session_id = new_id
    st.session_state.chat_sessions[new_id] = {
        "title": "New Chat",
        "messages": [{"role": "assistant", "content": "Hello! I can help you query the database. Ask me about products, customers, or orders.", "data": None}],
        "context_entity": None
    }
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("<p style='font-size: 0.75rem; font-weight: 700; color: #fff; letter-spacing: 0.5px; margin-bottom: 10px;'>RECENT CHATS</p>", unsafe_allow_html=True)

for session_id, session_data in reversed(list(st.session_state.chat_sessions.items())):
    title = session_data.get("title", "Chat")
    if title == "New Chat" and len(session_data["messages"]) <= 1:
        if session_id != st.session_state.current_session_id:
            continue # Hide empty new chats from history
        
    if len(title) > 20:
        title = title[:17] + "..."
        
    col1, col2 = st.sidebar.columns([0.85, 0.15])
    with col1:
        if st.button(f"🗨️ {title}", key=f"btn_{session_id}", use_container_width=True):
            st.session_state.current_session_id = session_id
            st.rerun()
    with col2:
        if st.button("✕", key=f"del_{session_id}", use_container_width=True):
            del st.session_state.chat_sessions[session_id]
            sync_history_to_disk()
            if st.session_state.current_session_id == session_id:
                new_id = str(uuid.uuid4())
                st.session_state.current_session_id = new_id
                st.session_state.chat_sessions[new_id] = {
                    "title": "New Chat",
                    "messages": [{"role": "assistant", "content": "Hello! I can help you query the database. Ask me about products, customers, or orders.", "data": None}],
                    "context_entity": None
                }
            st.rerun()

def stream_text(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.04)

def get_conversational_response(text):
    text = text.lower()
    greetings = ["hi", "hello", "hey", "hola", "good morning", "good evening", "greetings"]
    if any(text.startswith(g) for g in greetings):
        return random.choice([
            "Hello there! How can I help you with the database today?",
            "Hi! Ask me anything about our products or orders.",
            "Greetings! I'm ready to search the database for you.",
            "Hello! I'm listening."
        ])
    if "how are you" in text:
        return "I'm just a computer program, but I'm fully operational and ready to help you query your data!"
    if "help" in text or "what can you do" in text:
         return "I can help you find information in your database. You can ask things like:\n- 'Show me all orders from John Doe'\n- 'Find products related to sports'\n- 'Who is our top customer?'"
    if "who are you" in text or "what are you" in text:
        return "I am an AI assistant powered by PostgreSQL and pgvector. I translate your natural language questions into SQL queries."
    return None

# Display chat messages from history
for message in current_session["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("data") is not None:
            if isinstance(message["data"], pd.DataFrame):
                st.dataframe(message["data"])
            elif isinstance(message["data"], list):
                st.dataframe(pd.DataFrame(message["data"]))

if prompt := st.chat_input("Ask a question (e.g., 'Show me all orders from John Doe')"):
    if current_session["title"] == "New Chat":
        current_session["title"] = prompt[:20] + ("..." if len(prompt) > 20 else "")
        
    current_session["messages"].append({"role": "user", "content": prompt, "data": None})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        chit_chat_response = get_conversational_response(prompt)
        
        if chit_chat_response:
            st.write_stream(stream_text(chit_chat_response))
            current_session["messages"].append({"role": "assistant", "content": chit_chat_response, "data": None})
            
        else:
            response_text = "I wasn't able to find a direct answer to that in the database. Could you try rephrasing?"
            results_found = False
            response_data = None
            
            # Application Logic
            sql, params, extracted_entity = parse_query(prompt)
            
            # Option A: Rule-Based Context Injection
            if not sql or (not params and len(prompt.split()) < 5 and current_session.get("context_entity")):
                pronouns = ["he", "him", "his", "she", "her", "hers", "they", "them", "their", "it", "that", "this"]
                has_pronoun = any(p in prompt.lower().split() for p in pronouns)
                
                if has_pronoun or not sql:
                    ctx = current_session["context_entity"]
                    if ctx:
                        injected_prompt = f"{prompt} for {ctx['type']} {ctx['value']}"
                        sql_inj, params_inj, ext_inj = parse_query(injected_prompt)
                        if sql_inj and params_inj:
                            sql, params, extracted_entity = sql_inj, params_inj, ext_inj
                            print(f"[Option A] Rewrote to: {injected_prompt}")
                            
            # Option B: LLM Fallback Rewrite
            if not sql or (not params and len(prompt.split()) < 5):
                rewritten_prompt = rewrite_query_with_llm(prompt, current_session["messages"])
                if rewritten_prompt and rewritten_prompt.lower() != prompt.lower():
                    print(f"[Option B] LLM Rewrote to: {rewritten_prompt}")
                    sql_llm, params_llm, ext_llm = parse_query(rewritten_prompt)
                    if sql_llm:
                        sql, params, extracted_entity = sql_llm, params_llm, ext_llm
            
            if extracted_entity:
                current_session["context_entity"] = extracted_entity
            
            if sql:
                df = run_query(sql, params)
                if not df.empty:
                    response_data = df
                    response_text = f"Found {len(df)} results via SQL."
                    results_found = True
                    st.write_stream(stream_text(response_text))
                    st.dataframe(df)
                else:
                    response_text = "Executed SQL but found no results."
                    st.write_stream(stream_text(response_text))

            if not results_found:
                ql = prompt.lower()
                if "product" in ql or "price" in ql or "item" in ql:
                    df = semantic_product_search(prompt)
                    if not df.empty:
                         response_data = df
                         response_text = "Found semantic matches for products."
                         st.write_stream(stream_text(response_text))
                         st.dataframe(df)
                         results_found = True
                elif "customer" in ql or "order" in ql:
                    df = semantic_customer_search(prompt)
                    if not df.empty:
                         response_data = df
                         response_text = "Found semantic matches for customers."
                         st.write_stream(stream_text(response_text))
                         st.dataframe(df)
                         results_found = True
                         
            if not results_found and not sql:
                st.write_stream(stream_text(response_text))
            
            # Save interaction to history
            msg_obj = {"role": "assistant", "content": response_text, "data": response_data}
            current_session["messages"].append(msg_obj)
            
    # Serialize to JSON and save
    sync_history_to_disk()
