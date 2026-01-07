from typing import Optional

import pandas as pd
from sqlalchemy import text

from src.db import engine


def top_products_by_revenue(n: int = 10) -> pd.DataFrame:
    """
    Return top N products by total Revenue using the transactions table.
    Groups by StockCode + Description.
    """
    sql = text("""
        SELECT
            StockCode,
            Description,
            SUM(Revenue) AS Revenue
        FROM transactions
        GROUP BY StockCode, Description
        ORDER BY Revenue DESC
        LIMIT :limit;
    """)

    with engine.begin() as conn:
        result = conn.execute(sql, {"limit": n})
        rows = result.fetchall()

    # Convert result to DataFrame
    df = pd.DataFrame(rows, columns=["StockCode", "Description", "Revenue"])
    return df


if __name__ == "__main__":
    top = top_products_by_revenue(10)
    print(top)
