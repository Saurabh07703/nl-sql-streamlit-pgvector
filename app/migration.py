import pandas as pd
from db import execute, fetch_all
from hybrid_search import embed

def run_migration():
    print("Running migration sync...")
    
    # 1. Check if Sports data exists
    rows = fetch_all("SELECT id FROM products WHERE name = 'Football'")
    
    if not rows:
        print("Inserting Sports data...")
        execute("""
            INSERT INTO products (name, price) VALUES
            ('Football', 1500),
            ('Cricket Bat', 3000),
            ('Tennis Racket', 4500),
            ('Soccer Shoes', 2500);
        """)
    else:
        print("Sports data already exists.")

    # 2. Update Vectors for ALL products (Jewelry + Sports)
    # This ensures the DB vectors match the new vectorizer.pkl vocabulary
    print("Updating all product vectors...")
    products = fetch_all("SELECT id, name FROM products")
    
    for row in products:
        pid, name = row[0], row[1]
        vec = embed(name)
        # Convert list to string format for SQL vector
        # pgvector expects '[0.1, 0.2, ...]'
        # Using string interpolation carefully
        execute(
            "UPDATE products SET name_vector = :v WHERE id = :id",
            {"v": str(vec), "id": pid}
        )
    
    print("Migration complete.")
