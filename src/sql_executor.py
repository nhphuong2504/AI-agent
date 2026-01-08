from typing import List, Dict, Any
import pandas as pd
from sqlalchemy import text

from src.db import engine
from src.llm_client import is_sql_safe


def run_select_query(sql: str, params: Dict[str, Any] | None = None) -> pd.DataFrame:
    """
    Execute a read-only SQL query safely and return a DataFrame.

    - Validates that the SQL contains no dangerous keywords.
    - Assumes the SQL is a SELECT query.
    """
    if not is_sql_safe(sql):
        raise ValueError("SQL failed safety checks; potentially unsafe statement.")

    params = params or {}

    with engine.begin() as conn:
        df = pd.read_sql(text(sql), conn, params=params)

    return df
