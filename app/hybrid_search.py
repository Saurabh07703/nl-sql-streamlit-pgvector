import pickle
from db import run_query

VEC = pickle.load(open("db/vectorizer.pkl", "rb"))

def embed(text: str):
    return VEC.transform([text]).toarray()[0].tolist()

def semantic_product_search(text):
    sql = """
    SELECT id, name, price,
           (name_vector <#> (:v)::vector) AS distance
    FROM products
    ORDER BY distance ASC
    LIMIT 5;
    """
    return run_query(sql, {"v": embed(text)})

def semantic_customer_search(text):
    sql = """
    SELECT id, customer_name, order_total,
           (customer_vector <#> (:v)::vector) AS distance
    FROM orders
    ORDER BY distance ASC
    LIMIT 5;
    """
    return run_query(sql, {"v": embed(text)})
