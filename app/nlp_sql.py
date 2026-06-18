import re
from langsmith import traceable

@traceable(name="Parse Natural Language to SQL")
def parse_query(q: str):
    ql = q.lower()
    
    # ---------- Employees ----------
    if "employee" in ql or "salary" in ql or "staff" in ql or "worker" in ql:
        sql = """
        SELECT e.name, d.name AS department, e.email, e.salary
        FROM employees e
        JOIN departments d ON e.department_id = d.id
        """
        # FIX 1a: Department filter
        m = re.search(r"(in|from)\s+([a-z]+)", ql)
        if m:
            dept = m.group(2).capitalize()
            sql += " WHERE d.name = :dept"
            return sql, {"dept": dept}, {"type": "dept", "value": dept}

        # FIX 1b: Salary range filters (above / below / earning more/less than)
        m = re.search(r"(above|more than|greater than|over)\s+(\d+)", ql)
        if m:
            sql += " WHERE e.salary > :sal"
            return sql, {"sal": int(m.group(2))}, None

        m = re.search(r"(below|less than|under)\s+(\d+)", ql)
        if m:
            sql += " WHERE e.salary < :sal"
            return sql, {"sal": int(m.group(2))}, None

        if "top" in ql or "highest" in ql or "most" in ql or "earns the most" in ql:
            sql += " ORDER BY e.salary DESC LIMIT 5"
        return sql, {}, None

    # ---------- Orders ----------
    if "order" in ql or "customer" in ql or "purchase" in ql or "purchases" in ql:
        sql = """
        SELECT o.customer_name, e.name AS handled_by,
               o.order_total, o.order_date
        FROM orders o
        JOIN employees e ON o.employee_id = e.id
        """
        # FIX 2: Catch 'by X', 'named X', 'from X'
        m = re.search(r"(?:by|named|from)\s+([a-z]+)", ql)
        if m:
            emp = m.group(1).capitalize()
            sql += " WHERE e.name LIKE :emp"
            return sql, {"emp": f"%{emp}%"}, {"type": "emp", "value": emp}

        return sql, {}, None

    # ---------- Products ----------
    if "product" in ql or "price" in ql or "item" in ql or "items" in ql:
        sql = "SELECT name, price FROM products"

        m = re.search(r"above\s+(\d+)", ql)
        if m:
            sql += " WHERE price > :p"
            return sql, {"p": int(m.group(1))}, None

        m = re.search(r"below\s+(\d+)", ql)
        if m:
            sql += " WHERE price < :p"
            return sql, {"p": int(m.group(1))}, None

        return sql, {}, None

    return None, {}, None

import os
from openai import OpenAI

def rewrite_query_with_llm(query, history_messages):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
    if not client.api_key:
        return None # No LLM available
        
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history_messages[-6:-1] if m['role'] != 'system'])
    prompt = f"Given the chat history:\n{history_text}\n\nRewrite the following user query to make it fully self-contained without pronouns, keeping the same intent:\nUser: {query}\nRewritten Query:"
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM rewrite failed: {e}")
        return None
