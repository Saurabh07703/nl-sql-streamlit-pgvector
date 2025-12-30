import streamlit as st
from nlp_sql import parse_query
from db import run_query
from hybrid_search import semantic_product_search, semantic_customer_search

st.title("🧠 Local Natural Language Search (PostgreSQL + pgvector)")

query = st.text_input("Enter your query")

if st.button("Search") and query:

    sql, params = parse_query(query)

    if sql:
        st.subheader("SQL Result")
        df = run_query(sql, params)
        st.dataframe(df)

    st.subheader("Semantic Matches")

    ql = query.lower()

    if "product" in ql or "price" in ql:
            st.dataframe(semantic_product_search(query))

    elif "customer" in ql or "order" in ql:
            st.dataframe(semantic_customer_search(query))

    else:
        st.info("Vector search applies to products & customers only.")
