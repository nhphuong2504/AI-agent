from __future__ import annotations

import os
import re
from typing import Optional

from openai import OpenAI

from src.tools.schema import get_db_schema

# Basic guardrails
DISALLOWED = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|DETACH|PRAGMA)\b",
    re.IGNORECASE,
)

SYSTEM_PROMPT = """You are a senior analytics engineer writing SQLite SQL for business questions.

Rules:
- Output ONLY SQL, no explanation, no markdown.
- Use ONLY the tables and columns provided in the schema.
- Only write SELECT queries.
- Prefer using the 'orders' table for purchase-level questions (one row per invoice).
- Exclude cancellations unless user explicitly asks: add WHERE is_cancelled = 0 (or false).
- Always LIMIT results to at most 200 rows unless the question asks for aggregates (still limit when returning raw rows).
- Use SQLite functions: strftime('%Y-%m', invoice_date) for monthly grouping.
"""

def _validate_sql(sql: str) -> str:
    q = sql.strip().strip(";")
    if not q.lower().startswith("select"):
        raise ValueError("Generated SQL is not a SELECT query.")
    if DISALLOWED.search(q):
        raise ValueError("Generated SQL contains a disallowed keyword.")
    return q

def question_to_sql(question: str, model: str = "gpt-4o-mini") -> str:
    """
    Convert natural language question to SQLite SQL.
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file.")

    schema = get_db_schema()

    client = OpenAI(api_key=api_key)

    resp = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Schema:\n{schema}\n\nQuestion:\n{question}\n\nSQL:"},
        ],
    )

    sql = resp.choices[0].message.content or ""
    sql = _validate_sql(sql)

    # Ensure a LIMIT exists for safety (unless it’s purely aggregated; still safe to add)
    if re.search(r"\blimit\b", sql, re.IGNORECASE) is None:
        sql = f"{sql} LIMIT 200"

    return sql
