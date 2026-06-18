# 🧠 NLP → SQL Explainer

> **File:** `app/nlp_sql.py`  
> **Purpose:** Converts natural language user messages into SQL queries using keyword detection and regex pattern matching.  
> **Test Suite:** `tests/test_accuracy.py`

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [How NLP Message → SQL Query Works](#2-how-nlp-message--sql-query-works)
3. [What is Regex?](#3-what-is-regex)
4. [Every Regex Pattern Explained](#4-every-regex-pattern-explained)
5. [Complete Test Examples](#5-complete-test-examples)
6. [Accuracy Testing](#6-accuracy-testing)
7. [Accuracy Results](#7-accuracy-results)
8. [Understanding the 100% Score](#8-understanding-the-100-score)
9. [Real-World Limitations](#9-real-world-limitations)

---

## 1. System Architecture

```
User types message
      │
      ▼
[Step 1] Chit-chat check (main.py / api/index.py)
      │ hi/hello/help/who are you?
      ├── YES → Return friendly reply, STOP
      └── NO  ↓

[Step 2] parse_query(message)  ←── app/nlp_sql.py
      │
      ├── "employee"/"salary"/"staff"/"worker" → Employee SQL
      │       ├── re.search("(in|from)\s+([a-z]+)")       → Filter by department
      │       ├── re.search("(above|more than|over)\s+(\d+)") → WHERE salary > N
      │       ├── re.search("(below|less than|under)\s+(\d+)") → WHERE salary < N
      │       └── "top"/"highest"/"most"                  → ORDER BY salary DESC
      │
      ├── "order"/"customer"/"purchase" → Orders SQL
      │       └── re.search("(?:by|named|from)\s+([a-z]+)") → Filter by employee name
      │
      ├── "product"/"price"/"item"/"items" → Products SQL
      │       ├── re.search("above\s+(\d+)")  → WHERE price > N
      │       └── re.search("below\s+(\d+)")  → WHERE price < N
      │
      └── None → No SQL match
                    │
                    ▼
         [Step 3] Semantic/Vector Search  ←── app/hybrid_search.py
                    │
            embed(text) via TF-IDF vectorizer.pkl
                    │
            pgvector cosine distance query (<#> operator)
                    │
            Return top 5 nearest matches
```

---

## 2. How NLP Message → SQL Query Works

### Step-by-Step: `"show all orders"` → SQL

**Step 1 — Chit-chat check fails:**
```python
text = "show all orders"
# "hi"/"hello"/"help"/"who are you"? → ❌ None match → continue
```

**Step 2 — Enters `parse_query()`:**
```python
ql = "show all orders"   # .lower() applied

# Branch 1 — Employee?
if "employee" in ql or "salary" in ql or "staff" in ql or "worker" in ql:
    # ❌ None of these in "show all orders" → SKIP

# Branch 2 — Order?
if "order" in ql or "customer" in ql or "purchase" in ql or "purchases" in ql:
    # ✅ "order" found → ENTER
```

**Step 3 — Hardcoded SQL is assigned:**
```python
sql = """
SELECT o.customer_name, e.name AS handled_by,
       o.order_total, o.order_date
FROM orders o
JOIN employees e ON o.employee_id = e.id
"""
```
> ⚠️ The SQL is **not generated** — it is a pre-written string. The system only decides *which* string to use.

**Step 4 — Regex runs, finds nothing:**
```python
m = re.search(r"(?:by|named|from)\s+([a-z]+)", "show all orders")
# No "by", "named", or "from" → m = None → if m: SKIPPED
```

**Step 5 — Returns plain SQL with empty params:**
```python
return sql, {}   # {} = no WHERE clause = fetch ALL rows
```

**Step 6 — `run_query(sql, {})` executes in PostgreSQL:**
```sql
SELECT o.customer_name, e.name AS handled_by, o.order_total, o.order_date
FROM orders o
JOIN employees e ON o.employee_id = e.id
-- No WHERE = all rows returned
```

---

## 3. What is Regex?

**Regex (Regular Expression)** is a pattern-matching mini-language built into Python via `import re`.

```python
import re

re.search(pattern, string)  # Find first match anywhere in string
m.group(0)                  # Full match
m.group(1)                  # First () captured group
m.group(2)                  # Second () captured group
```

### Pattern Syntax Reference

| Symbol | Meaning | Example | Matches |
|--------|---------|---------|---------|
| `\d+`  | One or more digits | `\d+` | `42`, `500`, `1999` |
| `[a-z]+` | One or more lowercase letters | `[a-z]+` | `john`, `sales` |
| `\s+`  | One or more spaces | `\s+` | ` `, `  ` |
| `(a\|b)` | Either a or b | `(in\|from)` | `in` or `from` |
| `(?:...)` | Non-capturing group | `(?:by\|named)` | Groups without capturing |
| `above\s+(\d+)` | "above" + spaces + capture digits | `above 500` | captures `500` |

---

## 4. Every Regex Pattern Explained

### Pattern 1 — Department name (Employee branch)

```python
m = re.search(r"(in|from)\s+([a-z]+)", ql)
dept = m.group(2).capitalize()
```

| User says | What regex matches | `.group(2)` | SQL added |
|---|---|---|---|
| `"employees in Engineering"` | `"in engineering"` | `engineering` → `Engineering` | `WHERE d.name = 'Engineering'` |
| `"staff from Marketing"` | `"from marketing"` | `marketing` → `Marketing` | `WHERE d.name = 'Marketing'` |
| `"list employees"` | ❌ No match | — | No filter, returns ALL |

---

### Pattern 2 — Salary range above (Employee branch)

```python
m = re.search(r"(above|more than|greater than|over)\s+(\d+)", ql)
sal = int(m.group(2))
```

| User says | Keyword matched | `.group(2)` | SQL added |
|---|---|---|---|
| `"employees earning above 50000"` | `above` | `50000` | `WHERE e.salary > 50000` |
| `"employees with salary more than 70000"` | `more than` | `70000` | `WHERE e.salary > 70000` |
| `"staff over 60000"` | `over` | `60000` | `WHERE e.salary > 60000` |

---

### Pattern 3 — Salary range below (Employee branch)

```python
m = re.search(r"(below|less than|under)\s+(\d+)", ql)
sal = int(m.group(2))
```

| User says | Keyword matched | `.group(2)` | SQL added |
|---|---|---|---|
| `"employees earning below 30000"` | `below` | `30000` | `WHERE e.salary < 30000` |
| `"workers less than 25000"` | `less than` | `25000` | `WHERE e.salary < 25000` |

---

### Pattern 4 — Employee name filter (Orders branch)

```python
m = re.search(r"(?:by|named|from)\s+([a-z]+)", ql)
emp = m.group(1).capitalize()
# Used as: WHERE e.name LIKE '%Alice%'
```

| User says | Keyword | `.group(1)` | SQL added |
|---|---|---|---|
| `"orders handled by Alice"` | `by` | `alice` → `Alice` | `WHERE e.name LIKE '%Alice%'` |
| `"orders for customer named Bob"` | `named` | `bob` → `Bob` | `WHERE e.name LIKE '%Bob%'` |
| `"show orders from Alice"` | `from` | `alice` → `Alice` | `WHERE e.name LIKE '%Alice%'` |
| `"all orders"` | ❌ No match | — | No filter, returns ALL |

> **Why `LIKE '%Alice%'`?** The `%` wildcards allow partial matches — "Alice Smith" still matches even if you only typed "Alice".

---

### Pattern 5 — Product price above (Products branch)

```python
m = re.search(r"above\s+(\d+)", ql)
p = int(m.group(1))
```

| User says | `.group(1)` | SQL added |
|---|---|---|
| `"products above 500"` | `500` | `WHERE price > 500` |
| `"items above 1000"` | `1000` | `WHERE price > 1000` |

---

### Pattern 6 — Product price below (Products branch)

```python
m = re.search(r"below\s+(\d+)", ql)
p = int(m.group(1))
```

| User says | `.group(1)` | SQL added |
|---|---|---|
| `"products below 200"` | `200` | `WHERE price < 200` |
| `"cheap items below 50"` | `50` | `WHERE price < 50` |

---

## 5. Complete Test Examples

### 🟢 Greetings / Chit-Chat (No SQL Generated)

| Input | Expected Response |
|---|---|
| `hi` | Random welcome message |
| `hello` | Random welcome message |
| `good morning` | Random welcome message |
| `how are you` | "I'm fully operational..." |
| `help` | Lists capabilities |
| `what can you do` | Lists capabilities |
| `who are you` | "I am an AI assistant..." |

---

### 🔵 Employee Queries

| Input | SQL Generated |
|---|---|
| `show all employees` | Full employee list (no filter) |
| `list employees in Engineering` | `+ WHERE d.name = 'Engineering'` |
| `employees from Marketing` | `+ WHERE d.name = 'Marketing'` |
| `staff from HR` | `+ WHERE d.name = 'Hr'` |
| `who has the highest salary` | `+ ORDER BY e.salary DESC LIMIT 5` |
| `top salary earners` | `+ ORDER BY e.salary DESC LIMIT 5` |
| `which staff member earns the most` | `+ ORDER BY e.salary DESC LIMIT 5` |
| `employees earning above 50000` | `+ WHERE e.salary > 50000` |
| `employees earning below 30000` | `+ WHERE e.salary < 30000` |
| `employees with salary more than 70000` | `+ WHERE e.salary > 70000` |
| `workers less than 25000` | `+ WHERE e.salary < 25000` |

---

### 🟠 Order / Customer Queries

| Input | SQL Generated |
|---|---|
| `show all orders` | Full orders list (no filter) |
| `list customer orders` | Full orders list (no filter) |
| `show me all purchases` | Full orders list (no filter) |
| `orders handled by Alice` | `+ WHERE e.name LIKE '%Alice%'` |
| `show orders by John` | `+ WHERE e.name LIKE '%John%'` |
| `orders for customer named Bob` | `+ WHERE e.name LIKE '%Bob%'` |
| `show orders from Alice` | `+ WHERE e.name LIKE '%Alice%'` |

---

### 🟡 Product / Price Queries

| Input | SQL Generated |
|---|---|
| `show all products` | `SELECT name, price FROM products` |
| `show me all items` | `SELECT name, price FROM products` |
| `products above 500` | `+ WHERE price > 500` |
| `items above 1000` | `+ WHERE price > 1000` |
| `items above 750` | `+ WHERE price > 750` |
| `products below 200` | `+ WHERE price < 200` |
| `cheap products below 50` | `+ WHERE price < 50` |
| `price above 200` | `+ WHERE price > 200` |
| `items costing more than 500` | All products (no price range parsed — "costing more than" not in regex) |

---

### 🔴 Semantic / Vector Search Fallback

These fire when `parse_query()` returns `None` but message contains product/customer keywords:

| Input | Search Type | Mechanism |
|---|---|---|
| `find me something sporty` | Product semantic | TF-IDF → cosine distance on `name_vector` |
| `gaming accessories` | Product semantic | Vector similarity on product names |
| `customer who spends the most` | Customer semantic | Vector search on `customer_vector` in orders |

---

### ⚫ No Match (Fallback Message)

| Input | Result |
|---|---|
| `what is the weather today` | "I wasn't able to find..." |
| `tell me a joke` | Fallback message |

---

## 6. Accuracy Testing

### How to Run

```bash
# Windows
$env:PYTHONIOENCODING="utf-8"
.\.venv\Scripts\python.exe tests/test_accuracy.py

# Mac / Linux
PYTHONIOENCODING=utf-8 python tests/test_accuracy.py
```

### What is Measured

The test suite in `tests/test_accuracy.py` measures **3 parameters**:

#### Parameter 1: Intent Accuracy
> Did the system route to the **correct SQL branch**?

```
"show all orders" → orders branch?   YES ✅
"show all orders" → employee branch? NO  ❌
```

Formula:
```
Intent Accuracy = (Correct branch selections / Total tests) × 100
```

#### Parameter 2: SQL Accuracy
> Does the generated SQL contain the **correct clause**?

```
Input: "employees in Engineering"
Expected clause: "WHERE d.name = :dept"
Got:             "WHERE d.name = :dept"  → PASS ✅
```

Formula:
```
SQL Accuracy = (Correct SQL clauses / Total SQL tests) × 100
```

#### Parameter 3: Parameter Accuracy
> Was the **extracted value** (name, number, department) correct?

```
Input: "orders by John"
Expected: emp = '%John%'
Got:      emp = '%John%'  → PASS ✅
```

Formula:
```
Param Accuracy = (Correct param values / Total param tests) × 100
```

#### Overall Accuracy
```
Overall = (Intent Passes + SQL Passes + Param Passes)
          ────────────────────────────────────────────  × 100
          (Intent Tests + SQL Tests + Param Tests)
```

---

## 7. Accuracy Results

### Before Fixes (Original Code)

| Metric | Score | Tests |
|---|---|---|
| Intent Accuracy | 95.5% | 21/22 |
| SQL Accuracy | 82.4% | 14/17 |
| Param Accuracy | 80.0% | 8/10 |
| **Overall** | **87.8%** | |

**Failures:**
- `"which staff member earns the most"` → `None` (staff not recognized)
- `"employees earning above 50000"` → No salary filter
- `"items above 1000"` → `None` (items not recognized)
- `"show me all purchases"` → `None` (purchases not recognized)
- `"orders for customer named Bob"` → No name filter (missing "by")

---

### After Fix Run 1 (Synonyms + Salary Range + Items)

| Metric | Score | Tests |
|---|---|---|
| Intent Accuracy | 100.0% | 27/27 |
| SQL Accuracy | 100.0% | 25/25 |
| Param Accuracy | 93.3% | 14/15 |
| **Overall** | **98.5%** | |

**Remaining failure:**
- `"orders for customer named Bob"` → captured `"Named"` not `"Bob"` (regex greediness bug)

---

### After Fix Run 2 (Regex Greediness Fixed)

| Metric | Score | Tests |
|---|---|---|
| Intent Accuracy | 100.0% | 27/27 |
| SQL Accuracy | 100.0% | 25/25 |
| Param Accuracy | 100.0% | 15/15 |
| **Overall** | **💯 100.0%** | |

---

### Accuracy Journey Summary

```
87.8%  →  98.5%  →  100.0%
  ↑           ↑          ↑
Original   Fix Run 1   Fix Run 2
```

---

## 8. Understanding the 100% Score

### ✅ What 100% Means

The system is **deterministic** — same input always gives the same output. The test cases were written to exactly cover what the code handles. So 100% = the code and tests are perfectly aligned.

### ⚠️ What 100% Does NOT Mean

It is **closed-set accuracy** — 100% on 27 hand-crafted cases, not on all possible human language.

```
TIER 1 — Test Set Accuracy    : 100%  ✅  (our 27 cases)
TIER 2 — Synonym Coverage     :  ~60% ⚠️  (common rephrasings)
TIER 3 — True NLP Accuracy    :  ~30% ❌  (arbitrary natural language)
```

### The Root Cause of the Last Bug (Regex Greediness)

```
Pattern: (?:by|named|for customer|from)\s+([a-z]+)
Input:   "orders for customer named bob"

Before fix:
  "for customer" matches → captures next word → "named"  ❌ WRONG

After fix (removed "for customer"):
  "named" matches → captures next word → "bob"  ✅ CORRECT
```

**Lesson:** In regex alternation, order and specificity matter. A broader match can consume words that a later, more specific alternative was meant to capture.

---

## 9. Real-World Limitations

| Input | System Returns | Should Return |
|---|---|---|
| `"workers earning fifty thousand"` | `None` | Employee salary filter |
| `"show me the priciest items"` | All products | `ORDER BY price DESC` |
| `"who placed the most orders?"` | All orders | `GROUP BY + COUNT` |
| `"list orders from last month"` | All orders | `WHERE order_date >= ...` |
| `"items costing more than 500"` | All products | `WHERE price > 500` |

### Approaches to Improve Beyond Rule-Based

| Approach | Real-World Accuracy | Complexity |
|---|---|---|
| Keyword + Regex (current) | ~30–40% | Simple |
| + Synonym expansion | ~50–60% | Moderate |
| LLM (GPT/Gemini) Text-to-SQL | ~85–95% | Needs API key |
| Fine-tuned Text-to-SQL model | ~90–98% | Complex training |

---

## Key Concepts Summary

| Concept | File | Purpose |
|---|---|---|
| `re.search()` | `nlp_sql.py` | Find pattern anywhere in string |
| `.group(1)` | `nlp_sql.py` | Extract first captured `()` group |
| `.capitalize()` | `nlp_sql.py` | `"sales"` → `"Sales"` for DB match |
| `int(m.group(1))` | `nlp_sql.py` | `"500"` string → `500` integer |
| `LIKE '%Name%'` | Orders query | Partial name match |
| `<#>` operator | `hybrid_search.py` | pgvector cosine distance |
| `VEC.transform()` | `hybrid_search.py` | TF-IDF text → numeric vector |
| `:p`, `:dept`, `:emp`, `:sal` | All SQL | Parameterized queries (SQL injection safe) |

---

*Generated from live accuracy testing on `tests/test_accuracy.py` — 27 test cases, 100% pass rate.*
