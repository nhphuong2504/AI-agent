from __future__ import annotations

from pathlib import Path
from sqlalchemy import create_engine, text

DB_PATH = Path("data") / "online_retail.db"


def get_db_schema() -> str:
    """
    Returns a compact schema string for prompting the LLM.
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    engine = create_engine(f"sqlite:///{DB_PATH}")
    lines: list[str] = []

    with engine.connect() as conn:
        tables = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        ).fetchall()

        for (tname,) in tables:
            cols = conn.execute(text(f"PRAGMA table_info('{tname}')")).fetchall()
            # PRAGMA table_info: cid, name, type, notnull, dflt_value, pk
            col_str = ", ".join([f"{c[1]} {c[2]}" for c in cols])
            lines.append(f"TABLE {tname}({col_str})")

    return "\n".join(lines)


print(get_db_schema())