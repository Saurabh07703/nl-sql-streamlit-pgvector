# Interview Preparation: Natural Language to SQL with Hybrid Search

## 1. Project Overview
**"I built a search-enabled database assistant that allows users to query business data (Employees, Orders, Products) using natural language. Instead of writing complex SQL queries, users can ask 'Show me orders by John' or 'Find cheap products', and the system intelligently retrieves the data using a hybrid approach combining Rule-Based NLP and Vector Semantic Search powered by PostgreSQL and FastAPI."**

---

## 2. Workflow Execution & Diagram
The following diagram illustrates the data flow from the user's request to the final response.

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Frontend (React/UI)
    participant API as FastAPI Backend
    participant NLP as Intent Classifier (Regex)
    participant Vector as Vector Search (TF-IDF)
    participant DB as PostgreSQL DB

    User->>Frontend: "Show me products above $50"
    Frontend->>API: POST /api/chat
    
    API->>API: Check for Greetings (Hello/Hi)
    alt is Greeting
        API-->>Frontend: Return Conversational Reply (Streaming)
    else is Query
        API->>NLP: Parse Query with Regex
        
        alt Regex Match Found (Structured Query)
            NLP->>DB: Execute SQL (e.g., SELECT * FROM products WHERE price > 50)
            DB-->>NLP: Return Results
            NLP-->>API: Return Structured Data
        else No Regex Match (Unstructured/Semantic/Incomplete)
            API->>NLP: Use History for Context (e.g., "what about bob?")
            NLP->>LLM: Rewrite Query (OpenAI Fallback)
            LLM-->>NLP: Return Self-Contained Query
            API->>Vector: specific "product"/"customer" keywords?
            Vector->>Vector: Convert Query to Vector (TF-IDF)
            Vector->>DB: pgvector Similarity Search (Cosine Distance)
            DB-->>Vector: Return Nearest Neighbors
            Vector-->>API: Return Semantic Matches
        end
        
        API-->>Frontend: Return JSON/Streamed Response
    end
    Frontend-->>User: Display Dictionary/Table with Chat History Saved
```

### Step-by-Step Flow:
1.  **User Request**: User sends a natural language query.
2.  **Context Injection**: The system maintains a `chat_history.json` and loads the previous entities.
3.  **Intent Classification & Rewrite**:
    *   **Greeting Check**: Simple string matching for "hi", "hello" with word-by-word streaming responses.
    *   **Regex Parsing**: `app/nlp_sql.py` checks patterns (e.g., `above \d+`) to build precise SQL.
    *   **LLM Fallback Rewrite**: If the query is incomplete or contains pronouns ("he", "his"), it is rewritten using OpenAI based on recent chat history.
    *   **Fallback (Vector Search)**: If regex fails, `app/hybrid_search.py` converts text to vectors and queries the DB using `pgvector`.
4.  **Execution**: The appropriate SQL is run against Postgres.
5.  **Response**: Results are streamed to the frontend and saved to history.

---

## 3. Methodologies & Techniques

### A. Rule-Based NLP (Regular Expressions)
*   **What**: Using patterns like `r"above\s+(\d+)"` to extract specific constraints.
*   **Why**:
    *   **Precision**: 100% accurate for numerical/logic filters.
    *   **Cost/Speed**: Zero latency, no API costs compared to LLMs.
    *   **Safety**: Prevents hallucinated queries.

### B. Semantic Search (TF-IDF + Embeddings)
*   **What**: converting text into numerical vectors that represent meaning.
*   **Why**: Handles fuzzy matching (e.g., "phone" matches "smartphone").
*   **How**:
    *   **TF-IDF**: Calculates word importance (rare words weigh more).
    *   **pgvector**: Postgres extension to store vectors and perform similarity searches.
    *   **Cosine Similarity**: Used to find the "closest" product vector to the query vector.

### C. Context-Aware LLM Fallback (OpenAI)
*   **What**: Using `gpt-3.5-turbo` to rewrite queries that are incomplete or contain pronouns based on recent chat history.
*   **Why**: Makes the chatbot conversational. A user can say "Show me John's orders" and then follow up with "What is his salary?" without breaking the SQL parser.

### D. Hybrid Search Architecture
*   **What**: Combining **Structured Rules** (SQL) with **Unstructured Similarity** (Vectors) and **LLM Rewrites**.
*   **Why**: Provides the robustness of traditional databases with the flexibility of modern AI search.

---

## 4. Key Technical Terms

| Term | project definition |
| :--- | :--- |
| **FastAPI** | High-performance Python web framework used for the backend API. |
| **PostgreSQL** | Primary relational database used for storing business data. |
| **pgvector** | PostgreSQL extension enabling vector storage and similarity search (AI capabilities). |
| **TF-IDF** | *Term Frequency-Inverse Document Frequency*. Algorithm used to vectorize text. |
| **Cosine Distance `<#>`** | Metric used by Postgres to rank how similar two vectors are. |
| **Parameterized Queries** | Security technique (using `:value` placeholders) to prevent SQL Injection attacks. |
| **REST API** | The architectural style used for communication between the frontend and backend. |
