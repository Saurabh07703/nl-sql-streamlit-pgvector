from sqlalchemy import create_engine, text
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pickle

ENGINE_URL = DB_URL = "postgresql+psycopg2://postgres:Saurabh%4012345@localhost:5432/postgres"

engine = create_engine(ENGINE_URL)

def fetch(sql):
    with engine.connect() as c:
        res = c.execute(text(sql)).fetchall()
    return res

def update_vec(table, col, vecs, rows):
    with engine.begin() as c:
        for (row_id, _), v in zip(rows, vecs):
            c.execute(
                text(f"UPDATE {table} SET {col} = :v WHERE id=:id"),
                {"v": list(map(float, v)), "id": row_id}
            )

# ---------- Products ----------
rows = fetch("SELECT id, name FROM products")
prod_texts = [r[1] for r in rows]

prod_vec = TfidfVectorizer(max_features=300)
prod_matrix = prod_vec.fit_transform(prod_texts).toarray()

pickle.dump(prod_vec, open("db/vectorizer.pkl", "wb"))

update_vec("products", "name_vector", prod_matrix, rows)

# ---------- Orders ----------
rows = fetch("SELECT id, customer_name FROM orders")
cust_texts = [r[1] for r in rows]

cust_vec = TfidfVectorizer(max_features=300)
cust_matrix = cust_vec.fit_transform(cust_texts).toarray()

update_vec("orders", "customer_vector", cust_matrix, rows)

print("Embeddings stored successfully.")
