import streamlit as st
from nlp_sql import parse_query
from db import run_query
from hybrid_search import semantic_product_search, semantic_customer_search
import random

st.set_page_config(page_title="NLP SQL Chat", page_icon="💬")
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

# Function to handle greetings
def is_greeting(text):
    greetings = ["hi", "hello", "hey", "hola", "good morning", "good evening", "greetings"]
    return any(text.lower().startswith(g) for g in greetings)

def get_greeting_response():
    responses = [
        "Hello there! How can I help you with the database today?",
        "Hi! Ask me anything about our products or orders.",
        "Greetings! I'm ready to search the database for you.",
        "Hello! I'm listening."
    ]
    return random.choice(responses)

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
        
        # 1. Check for Greeting
        if is_greeting(prompt):
            response_text = get_greeting_response()
            message_placeholder.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
        else:
            # 2. Try SQL/Semantic Search
            response_text = "I looked that up for you."
            results_found = False
            response_data = None
            
            # Application Logic
            sql, params = parse_query(prompt)
            
            if sql:
                message_placeholder.markdown(f"**Executing SQL:** `{sql}`")
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
