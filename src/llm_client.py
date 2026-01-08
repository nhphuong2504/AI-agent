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
import os


from openai import OpenAI
from src.config import settings

DEFAULT_MODEL = settings.openai_model


def get_openai_client() -> OpenAI:
    """
    Lazily create an OpenAI client.
    This avoids requiring OPENAI_API_KEY at import time when only safety utilities are used.
    """
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in environment or .env")
    return OpenAI(api_key=settings.openai_api_key)



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
    
def generate_sql_with_llm(question: str) -> tuple[str, str]:
    """
    Use OpenAI Chat Completions API to generate SQL from a natural-language question.
    """
    prompt = build_sql_prompt(question)

    client = get_openai_client()  # ← create client here when needed

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an expert SQL assistant. Follow the instructions in the prompt exactly.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.0,
    )
    ...

