---
title: NLP SQL Streamlit
emoji: 📊
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.40.1
app_file: app/main.py
pinned: false
---

🧩 System Architecture (Simple & Professional View)
flowchart TD

A[🧑‍💻 User Enters Query<br><b>Natural Language Input</b>]:::box --> 
B[🧠 Query Understanding Layer<br><b>Rule-based NL → SQL Parser</b><br><i>🔹 Suggestion: Add synonym support + fallback LLM later</i>]:::highlight

B --> 
C[🧾 SQL Query Builder<br><b>Pre-defined Safe SQL Templates</b><br><i>🔹 Suggestion: Add SQL safety validation</i>]:::highlight

C --> 
D{⚡ Hybrid Search Engine<br><b>Semantic + Structured Search</b>}:::box

D --> 
E1[🟢 Structured SQL Filtering<br><b>Joins • Conditions • Sorting</b><br><i>🔹 Suggestion: Add ranking by relevance</i>]:::highlight

D --> 
E2[🟣 Semantic Search (pgvector)<br><b>TF-IDF Text Embeddings</b><br><i>🔹 Suggestion: Improve similarity score handling</i>]:::highlight

E1 --> 
F[(🗄 PostgreSQL Database<br><b>Employees • Orders • Products</b><br><i>🔹 Suggestion: Add more sample data</i>)]:::box

E2 --> F

F --> 
G[📊 Streamlit UI<br><b>Results Table + Query Output</b><br><i>🔹 Suggestion: Add query history & tooltips</i>]:::highlight


classDef box fill:#eef6ff,stroke:#3a7bd5,stroke-width:2px,color:#000;
classDef highlight fill:#fff7e6,stroke:#f4a100,stroke-width:2px,color:#000;

🟢 Simple & Practical Suggestions to Improve System Effectiveness

These are written in plain terms evaluators will appreciate.

✅ 1) Improve how the system understands user queries

Right now, the system uses:

rule-based parsing

fixed keywords

structured mapping

To make it smarter:

⭐ Add synonyms & variations

engineering → dev → development
orders → sales → transactions
price above → greater than → more than


⭐ Add basic spell-check tolerance

⭐ (Future) Add optional LLM fallback
(for complex queries only)

This keeps system fast, safe, and offline — but upgrade-ready.

✅ 2) Improve search result relevance

Currently results are based on:

SQL filters

tf-idf similarity

We can improve by:

⭐ Adding a relevance score

Final Score = SQL Match + Semantic Match Weight


⭐ Prioritize:

exact matches first

close meaning matches next

⭐ Display “why this result appeared”

(example: matched department name)

This increases explainability & user trust.

✅ 3) Improve Streamlit UI usability

Make it friendlier & more interactive:

⭐ Show SQL query preview (read-only)

⭐ Add query history sidebar

⭐ Allow saving frequently used queries

⭐ Add tooltips like:

“Semantic match applied”

“Filter by salary > X”

⭐ Optionally show match score %

Makes the tool feel polished & professional.

✅ 4) Improve code structure & maintainability

Refactor into clean modules:

nlp_parser.py — query interpretation

sql_templates.py — safe SQL patterns

hybrid_search.py — semantic search logic

db.py — database layer

Also add:

✔ comments & docstrings
✔ type hints
✔ basic unit tests
✔ logging for executed SQL paths

Easier to debug, extend, and review.

✅ 5) Improve database & sample data quality

Add:

⭐ more realistic employee records
⭐ multiple departments
⭐ more order history
⭐ price variations in products

Also add:

✔ test queries set
✔ sample outputs table

This improves demo quality & evaluation strength.

🏆 Evaluation Criteria — Explained in Simple Terms

Here’s how your system meets expectations 👇

🎯 Query Accuracy & Efficiency

✔ Rule-based SQL = predictable & correct
✔ Semantic search improves meaning-based matches
✔ Works fast because everything runs locally
✔ pgvector speeds up similarity search

🎯 Usability of Streamlit UI

✔ Clean single-input query box
✔ Simple readable results table
✔ Suitable for demo & evaluation
✔ Easy to understand for non-technical users

(And future UI upgrades already suggested)

🎯 Best Strategy Suggestions for Improvement

✔ Hybrid rule-based + semantic search
✔ LLM only as optional addon
✔ relevance-based ranking
✔ explainable results
✔ feedback-driven enhancements
