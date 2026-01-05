from pathlib import Path
import re

import pandas as pd
from sqlalchemy import create_engine, text

# Path to your SQLite DB
DB_PATH = Path("data") / "online_retail.db"

# Very basic SQL safety for now
DISALLOWED = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|DETACH|PRAGMA)\b",
    re.IGNORECASE,
)

def run_sql(query: str, limit: int = 200) -> pd.DataFrame:
    q = query.strip().rstrip(";")

    if not q.lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed")

    if DISALLOWED.search(q):
        raise ValueError("Disallowed SQL keyword detected")

    if "limit" not in q.lower():
        q = f"{q} LIMIT {limit}"

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. Run load_online_retail.py first."
        )

    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.connect() as conn:
        df = pd.read_sql(text(q), conn)

    return df
