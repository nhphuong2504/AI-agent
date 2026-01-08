"""
LLM client stub for SQL generation.

This module is responsible for:
- building a prompt using the schema description,
- (eventually) calling a real LLM API to get SQL,
- performing basic safety checks on the returned SQL.

Right now, it returns a hard-coded example SQL for testing the flow.
"""

from typing import Tuple

from src.sql_generation import build_sql_prompt


def is_sql_safe(sql: str) -> bool:
    """
    Basic safety check: disallow data-changing or DDL statements.
    This is a simple substring-based filter; you can improve it later.

    Disallowed keywords (case-insensitive):
    - INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE
    """
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"]
    upper_sql = sql.upper()
    return not any(keyword in upper_sql for keyword in forbidden)


def generate_sql_stub(question: str) -> Tuple[str, str]:
    """
    Temporary stub that:
    - builds a prompt,
    - returns a simple SQL query depending on the question,
    - along with the prompt (for debugging).

    Replace this later with a real LLM call.
    """
    prompt = build_sql_prompt(question)

    # Super simple pattern matching to simulate different queries.
    # This is just to test the end-to-end flow before integrating a real LLM.
    q_lower = question.lower()

    if "top" in q_lower and "customer" in q_lower and "revenue" in q_lower:
        sql = """
        SELECT
            CustomerID,
            total_revenue
        FROM customers
        ORDER BY total_revenue DESC
        LIMIT 10;
        """
    elif "top" in q_lower and "product" in q_lower:
        sql = """
        SELECT
            StockCode,
            Description,
            SUM(Revenue) AS total_revenue
        FROM transactions
        GROUP BY StockCode, Description
        ORDER BY total_revenue DESC
        LIMIT 10;
        """
    else:
        # Default fallback: simple total revenue query
        sql = """
        SELECT
            SUM(Revenue) AS total_revenue
        FROM transactions;
        """

    sql = sql.strip()

    if not is_sql_safe(sql):
        raise ValueError("Generated SQL failed safety checks.")

    return prompt, sql
