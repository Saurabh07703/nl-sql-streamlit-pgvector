import re

def parse_query(q: str):
    ql = q.lower()

    # ---------- Employees ----------
    if "employee" in ql or "salary" in ql:
        sql = """
        SELECT e.name, d.name AS department, e.email, e.salary
        FROM employees e
        JOIN departments d ON e.department_id = d.id
        """
        m = re.search(r"(in|from)\s+([a-z]+)", ql)
        if m:
            dept = m.group(2).capitalize()
            sql += " WHERE d.name = :dept"
            return sql, {"dept": dept}

        if "top" in ql or "highest" in ql:
            sql += " ORDER BY e.salary DESC LIMIT 5"
        return sql, {}

    # ---------- Orders ----------
    if "order" in ql or "customer" in ql:
        sql = """
        SELECT o.customer_name, e.name AS handled_by,
               o.order_total, o.order_date
        FROM orders o
        JOIN employees e ON o.employee_id = e.id
        """
        m = re.search(r"by\s+([a-z]+)", ql)
        if m:
            emp = m.group(1).capitalize()
            sql += " WHERE e.name LIKE :emp"
            return sql, {"emp": f"%{emp}%"}

        return sql, {}

    # ---------- Products ----------
    if "product" in ql or "price" in ql:
        sql = "SELECT name, price FROM products"

        m = re.search(r"above\s+(\d+)", ql)
        if m:
            sql += " WHERE price > :p"
            return sql, {"p": int(m.group(1))}

        m = re.search(r"below\s+(\d+)", ql)
        if m:
            sql += " WHERE price < :p"
            return sql, {"p": int(m.group(1))}

        return sql, {}

    return None, {}
