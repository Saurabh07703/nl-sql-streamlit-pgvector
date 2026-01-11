import streamlit as st
from nlp_sql import parse_query
from db import run_query
from hybrid_search import semantic_product_search, semantic_customer_search
import random
from migration import run_migration

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

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I can help you query the database. Ask me about products, customers, or orders."}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If the message has a dataframe, display it
        if "data" in message:
            st.dataframe(message["data"])

# Function to handle generic conversation (Smart Chat)
def get_conversational_response(text):
    text = text.lower()
    
    # Greetings
    greetings = ["hi", "hello", "hey", "hola", "good morning", "good evening", "greetings"]
    if any(text.startswith(g) for g in greetings):
        return random.choice([
            "Hello there! How can I help you with the database today?",
            "Hi! Ask me anything about our products or orders.",
            "Greetings! I'm ready to search the database for you.",
            "Hello! I'm listening."
        ])

    # Status checks
    if "how are you" in text:
        return "I'm just a computer program, but I'm fully operational and ready to help you query your data!"

    # Capabilities / Help
    if "help" in text or "what can you do" in text:
         return "I can help you find information in your database. You can ask things like:\n- 'Show me all orders from John Doe'\n- 'Find products related to sports'\n- 'Who is our top customer?'"

    # Identity
    if "who are you" in text or "what are you" in text:
        return "I am an AI assistant powered by PostgreSQL and pgvector. I translate your natural language questions into SQL queries."

    return None

# Accept user input
if prompt := st.chat_input("Ask a question (e.g., 'Show me all orders from John Doe')"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # 1. Check for Conversation/Chit-Chat
        chit_chat_response = get_conversational_response(prompt)
        
        if chit_chat_response:
            message_placeholder.markdown(chit_chat_response)
            st.session_state.messages.append({"role": "assistant", "content": chit_chat_response})
            
        else:
            # 2. Try SQL/Semantic Search
            response_text = "I wasn't able to find a direct answer to that in the database. Could you try rephrasing?"
            results_found = False
            response_data = None
            
            # Application Logic
            sql, params = parse_query(prompt)
            
            if sql:
                # message_placeholder.markdown(f"**Executing SQL:** `{sql}`")
                df = run_query(sql, params)
                if not df.empty:
                    st.dataframe(df)
                    response_data = df
                    response_text = f"Found {len(df)} results via SQL."
                    results_found = True
                else:
                     message_placeholder.markdown("Executed SQL but found no results.")

            # Semantic Search Fallback/Addition
            if not results_found: # Or run consistently if you prefer
                ql = prompt.lower()
                if "product" in ql or "price" in ql:
                    df = semantic_product_search(prompt)
                    if not df.empty:
                         st.markdown("**Semantic Product Matches:**")
                         st.dataframe(df)
                         response_data = df
                         response_text = "Found semantic matches for products."

                elif "customer" in ql or "order" in ql:
                    df = semantic_customer_search(prompt)
                    if not df.empty:
                         st.markdown("**Semantic Customer Matches:**")
                         st.dataframe(df)
                         response_data = df
                         response_text = "Found semantic matches for customers."
            
            # Save interaction to history
            msg_obj = {"role": "assistant", "content": response_text}
            if response_data is not None:
                msg_obj["data"] = response_data
            
            st.session_state.messages.append(msg_obj)
