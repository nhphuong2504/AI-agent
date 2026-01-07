from typing import Optional
import math

from sqlalchemy import text
from src.db import engine, init_db
from src.load_data import load_online_retail


def load_transactions_to_db(chunk_size: Optional[int] = None) -> None:
    """
    Load cleaned Online Retail data from Excel into the transactions table.

    - Uses load_online_retail() which already adds Revenue.
    - Optionally supports chunking (for very large datasets).
    """
    # Ensure table exists
    init_db()

    # Load full cleaned DataFrame
    print("Loading data from Excel via load_online_retail()...")
    df = load_online_retail()
    print(f"Total rows after cleaning: {len(df)}")

    # Normalize column types for DB insert
    df_for_db = df.copy()

    # InvoiceNo and StockCode should be text
    df_for_db["InvoiceNo"] = df_for_db["InvoiceNo"].astype(str)
    df_for_db["StockCode"] = df_for_db["StockCode"].astype(str)

    # InvoiceDate -> ISO string
    df_for_db["InvoiceDate"] = df_for_db["InvoiceDate"].astype(str)

    # CustomerID -> int (drop NA just in case)
    df_for_db = df_for_db.dropna(subset=["CustomerID"])
    df_for_db["CustomerID"] = df_for_db["CustomerID"].astype(int)

    # Only keep the columns we need in the DB schema
    df_for_db = df_for_db[
        [
            "InvoiceNo",
            "StockCode",
            "Description",
            "Quantity",
            "InvoiceDate",
            "UnitPrice",
            "CustomerID",
            "Country",
            "Revenue",
        ]
    ]

    # Insert into DB
    with engine.begin() as conn:
        # Optional: clear existing data to avoid duplicates while you iterate
        print("Clearing existing data from transactions table...")
        conn.execute(text("DELETE FROM transactions"))

        if chunk_size is None:
            print("Inserting all rows in one batch...")
            df_for_db.to_sql(
                "transactions",
                con=conn.connection,  # underlying DB-API connection
                if_exists="append",
                index=False,
            )
        else:
            print(f"Inserting in chunks of {chunk_size} rows...")
            num_rows = len(df_for_db)
            num_chunks = math.ceil(num_rows / chunk_size)
            for i in range(num_chunks):
                start = i * chunk_size
                end = min((i + 1) * chunk_size, num_rows)
                chunk = df_for_db.iloc[start:end]
                print(f"Inserting rows {start} to {end-1}...")
                chunk.to_sql(
                    "transactions",
                    con=conn.connection,
                    if_exists="append",
                    index=False,
                )

    print("Done. Data loaded into transactions table.")


if __name__ == "__main__":
    load_transactions_to_db()
