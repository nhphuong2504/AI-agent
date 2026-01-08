from textwrap import dedent
from src.schema_description import SCHEMA_DESCRIPTION


def build_sql_prompt(question: str) -> str:
    """
    Build a prompt for an LLM that should output ONLY a SQL query.

    The SQL must:
    - be valid SQLite SQL,
    - reference only existing tables/columns in the schema,
    - not modify data (no INSERT/UPDATE/DELETE/DDL),
    - answer the user's question using SELECT queries.
    """
    prompt = f"""
    You are an expert SQL analyst working with a SQLite database.

    Below is the database schema and business rules:

    {SCHEMA_DESCRIPTION}

    Your task:
    - Read the user's question.
    - Write ONE SQL query that answers the question.
    - The SQL must be valid for SQLite.
    - Use only the tables and columns described in the schema.
    - Do NOT use any tables or columns that are not described.
    - Do NOT modify the database (no INSERT, UPDATE, DELETE, DROP, ALTER, CREATE).
    - Do NOT use views, CTEs, or functions that are not supported by SQLite.
    - Prefer simple, readable SELECT queries with explicit column names.
    - If aggregation is needed, use GROUP BY and appropriate aggregate functions.

    Output format:
    - Return ONLY the SQL query.
    - Do not include explanations, comments, or markdown.
    - Do not wrap the SQL in backticks.
    - Do not add any text before or after the SQL.

    User question:
    {question}
    """
    return dedent(prompt).strip()


def example_prompt():
    """
    Build and print an example prompt for a simple question.
    For debugging and inspection.
    """
    question = "Show the top 10 customers by total_revenue."
    prompt = build_sql_prompt(question)
    print(prompt)


if __name__ == "__main__":
    example_prompt()
