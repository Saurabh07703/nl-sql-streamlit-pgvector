"""
Accuracy Test Suite for nlp_sql.py
====================================
Measures:
  1. Intent Accuracy   — Did it pick the right SQL branch?
  2. Parameter Accuracy — Did regex extract the right value?
  3. SQL Accuracy      — Does the output SQL contain the expected clause?

Run with:
    python tests/test_accuracy.py
"""
import sys
import os

# ── Stub out langsmith if not installed (test environment) ──
try:
    import langsmith
except ImportError:
    import types
    langsmith = types.ModuleType("langsmith")
    langsmith.traceable = lambda **kw: (lambda f: f)  # no-op decorator
    sys.modules["langsmith"] = langsmith

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from nlp_sql import parse_query

# ─────────────────────────────────────────────────────────────
# TEST CASES  (input, expected_sql_fragment, expected_param_key, expected_param_value)
# expected_sql_fragment = substring that MUST appear in the generated SQL (case-insensitive)
# expected_param_key    = key in params dict (None if no params expected)
# expected_param_value  = expected value for that key (None if no params expected)
# ─────────────────────────────────────────────────────────────

TEST_CASES = [

    # ── EMPLOYEE QUERIES ─────────────────────────────────────
    {
        "input":           "show all employees",
        "intent":          "employee",
        "expect_sql":      "FROM employees",
        "expect_param":    None,
        "expect_value":    None,
        "label":           "All employees (no filter)"
    },
    {
        "input":           "list employees in Engineering",
        "intent":          "employee",
        "expect_sql":      "WHERE d.name = :dept",
        "expect_param":    "dept",
        "expect_value":    "Engineering",
        "label":           "Employee dept filter (in)"
    },
    {
        "input":           "employees from Marketing",
        "intent":          "employee",
        "expect_sql":      "WHERE d.name = :dept",
        "expect_param":    "dept",
        "expect_value":    "Marketing",
        "label":           "Employee dept filter (from)"
    },
    {
        "input":           "who has the highest salary",
        "intent":          "employee",
        "expect_sql":      "ORDER BY e.salary DESC LIMIT 5",
        "expect_param":    None,
        "expect_value":    None,
        "label":           "Top salary (highest)"
    },
    {
        "input":           "top salary earners",
        "intent":          "employee",
        "expect_sql":      "ORDER BY e.salary DESC LIMIT 5",
        "expect_param":    None,
        "expect_value":    None,
        "label":           "Top salary (top)"
    },
    # FIX 1: staff/worker synonyms + salary range + 'most' keyword
    {
        "input":           "which staff member earns the most",
        "intent":          "employee",
        "expect_sql":      "ORDER BY e.salary DESC LIMIT 5",
        "expect_param":    None,
        "expect_value":    None,
        "label":           "[FIX 1a] 'staff' synonym now recognized"
    },
    {
        "input":           "employees earning above 50000",
        "intent":          "employee",
        "expect_sql":      "WHERE e.salary > :sal",
        "expect_param":    "sal",
        "expect_value":    50000,
        "label":           "[FIX 1b] Salary range filter: above"
    },
    {
        "input":           "employees earning below 30000",
        "intent":          "employee",
        "expect_sql":      "WHERE e.salary < :sal",
        "expect_param":    "sal",
        "expect_value":    30000,
        "label":           "[FIX 1b] Salary range filter: below"
    },
    {
        "input":           "employees with salary more than 70000",
        "intent":          "employee",
        "expect_sql":      "WHERE e.salary > :sal",
        "expect_param":    "sal",
        "expect_value":    70000,
        "label":           "[FIX 1b] Salary range filter: more than"
    },

    # ── ORDER QUERIES ────────────────────────────────────────
    {
        "input":           "show all orders",
        "intent":          "order",
        "expect_sql":      "FROM orders",
        "expect_param":    None,
        "expect_value":    None,
        "label":           "All orders (no filter)"
    },
    {
        "input":           "orders handled by Alice",
        "intent":          "order",
        "expect_sql":      "WHERE e.name LIKE :emp",
        "expect_param":    "emp",
        "expect_value":    "%Alice%",
        "label":           "Order by employee name"
    },
    {
        "input":           "show orders by John",
        "intent":          "order",
        "expect_sql":      "WHERE e.name LIKE :emp",
        "expect_param":    "emp",
        "expect_value":    "%John%",
        "label":           "Order filter (by John)"
    },
    {
        "input":           "list customer orders",
        "intent":          "order",
        "expect_sql":      "FROM orders",
        "expect_param":    None,
        "expect_value":    None,
        "label":           "Customer orders (no employee filter)"
    },
    # FIX 2: purchases synonym + 'named X' / 'from X' regex expansion
    {
        "input":           "show me all purchases",
        "intent":          "order",
        "expect_sql":      "FROM orders",
        "expect_param":    None,
        "expect_value":    None,
        "label":           "[FIX 2a] 'purchases' synonym now recognized"
    },
    {
        "input":           "orders for customer named Bob",
        "intent":          "order",
        "expect_sql":      "WHERE e.name LIKE :emp",
        "expect_param":    "emp",
        "expect_value":    "%Bob%",
        "label":           "[FIX 2b] 'named Bob' now triggers name filter"
    },
    {
        "input":           "show orders from Alice",
        "intent":          "order",
        "expect_sql":      "WHERE e.name LIKE :emp",
        "expect_param":    "emp",
        "expect_value":    "%Alice%",
        "label":           "[FIX 2b] 'from Alice' now triggers name filter"
    },

    # ── PRODUCT QUERIES ──────────────────────────────────────
    {
        "input":           "show all products",
        "intent":          "product",
        "expect_sql":      "FROM products",
        "expect_param":    None,
        "expect_value":    None,
        "label":           "All products (no filter)"
    },
    {
        "input":           "products above 500",
        "intent":          "product",
        "expect_sql":      "WHERE price > :p",
        "expect_param":    "p",
        "expect_value":    500,
        "label":           "Product price above"
    },
    {
        "input":           "items above 1000",
        "intent":          "product",
        "expect_sql":      "WHERE price > :p",
        "expect_param":    "p",
        "expect_value":    1000,
        "label":           "Product price above 1000"
    },
    {
        "input":           "products below 200",
        "intent":          "product",
        "expect_sql":      "WHERE price < :p",
        "expect_param":    "p",
        "expect_value":    200,
        "label":           "Product price below"
    },
    {
        "input":           "cheap products below 50",
        "intent":          "product",
        "expect_sql":      "WHERE price < :p",
        "expect_param":    "p",
        "expect_value":    50,
        "label":           "Cheap products below 50"
    },
    # FIX 3: 'item'/'items' synonym for product
    {
        "input":           "items costing more than 500",
        "intent":          "product",   # 'items' now triggers product branch
        "expect_sql":      "FROM products",  # 'costing more than' not a price regex → returns all
        "expect_param":    None,
        "expect_value":    None,
        "label":           "[FIX 3] 'items' recognized; no price regex match → all products"
    },
    {
        "input":           "show me all items",
        "intent":          "product",
        "expect_sql":      "FROM products",
        "expect_param":    None,
        "expect_value":    None,
        "label":           "[FIX 3] 'items' synonym triggers product branch"
    },
    {
        "input":           "items above 750",
        "intent":          "product",
        "expect_sql":      "WHERE price > :p",
        "expect_param":    "p",
        "expect_value":    750,
        "label":           "[FIX 3] 'items above 750' fully resolved"
    },
    {
        "input":           "price above 200",
        "intent":          "product",
        "expect_sql":      "WHERE price > :p",
        "expect_param":    "p",
        "expect_value":    200,
        "label":           "Price keyword triggers product branch"
    },

    # ── NO MATCH ─────────────────────────────────────────────
    {
        "input":           "what is the weather today",
        "intent":          None,
        "expect_sql":      None,
        "expect_param":    None,
        "expect_value":    None,
        "label":           "No match — irrelevant question"
    },
    {
        "input":           "tell me a joke",
        "intent":          None,
        "expect_sql":      None,
        "expect_param":    None,
        "expect_value":    None,
        "label":           "No match — off-topic"
    },
]

# ─────────────────────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────────────────────

def determine_intent(sql):
    """Reverse-engineer intent from SQL output."""
    if sql is None:
        return None
    sql_lower = sql.lower()
    if "from employees" in sql_lower:
        return "employee"
    if "from orders" in sql_lower:
        return "order"
    if "from products" in sql_lower:
        return "product"
    return None


def run_tests():
    total        = len(TEST_CASES)
    intent_pass  = 0
    param_pass   = 0
    sql_pass     = 0
    intent_tests = 0
    param_tests  = 0
    sql_tests    = 0

    print("=" * 70)
    print(f"{'NLP → SQL ACCURACY REPORT':^70}")
    print("=" * 70)

    for i, tc in enumerate(TEST_CASES, 1):
        sql, params, _ = parse_query(tc["input"])
        got_intent  = determine_intent(sql)

        # ── Intent check ──
        intent_ok = (got_intent == tc["intent"])
        intent_tests += 1
        if intent_ok:
            intent_pass += 1

        # ── SQL clause check ──
        sql_ok = True
        if tc["expect_sql"] is not None:
            sql_tests += 1
            if sql and tc["expect_sql"].lower() in sql.lower():
                sql_pass += 1
            else:
                sql_ok = False

        # ── Parameter check ──
        param_ok = True
        if tc["expect_param"] is not None:
            param_tests += 1
            got_val = params.get(tc["expect_param"])
            if got_val == tc["expect_value"]:
                param_pass += 1
            else:
                param_ok = False

        # ── Status symbol ──
        if intent_ok and sql_ok and param_ok:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"

        print(f"\n[{i:02d}] {status} — {tc['label']}")
        print(f"      Input  : \"{tc['input']}\"")
        print(f"      Intent : expected={tc['intent']!r:12s}  got={got_intent!r}")
        if tc["expect_sql"]:
            found = tc["expect_sql"].lower() in (sql or "").lower()
            print(f"      SQL    : expected clause={'YES' if found else 'NO '} → '{tc['expect_sql']}'")
        if tc["expect_param"]:
            got_val = params.get(tc["expect_param"], "MISSING")
            match = "✅" if got_val == tc["expect_value"] else "❌"
            print(f"      Param  : {tc['expect_param']}={got_val!r} (expected {tc['expect_value']!r}) {match}")

    # ── Summary ──
    print("\n" + "=" * 70)
    print(f"{'ACCURACY SUMMARY':^70}")
    print("=" * 70)
    intent_acc = (intent_pass / intent_tests * 100) if intent_tests else 0
    param_acc  = (param_pass  / param_tests  * 100) if param_tests  else 0
    sql_acc    = (sql_pass    / sql_tests    * 100) if sql_tests    else 0
    overall    = ((intent_pass + param_pass + sql_pass) /
                  (intent_tests + param_tests + sql_tests) * 100)

    print(f"  Intent  Accuracy : {intent_pass}/{intent_tests} = {intent_acc:.1f}%")
    print(f"  SQL     Accuracy : {sql_pass}/{sql_tests}  = {sql_acc:.1f}%")
    print(f"  Param   Accuracy : {param_pass}/{param_tests}   = {param_acc:.1f}%")
    print(f"  ─────────────────────────────────")
    print(f"  Overall Accuracy : {overall:.1f}%")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
