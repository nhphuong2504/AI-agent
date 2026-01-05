from __future__ import annotations

from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

RAW_PATH = Path("data/raw/online_retail.xlsx")
DB_PATH = Path("data/online_retail.db")


def main() -> None:
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Missing file: {RAW_PATH}")

    # Read Excel
    df = pd.read_excel(RAW_PATH)

    # Basic cleaning
    df = df.dropna(subset=["CustomerID"])
    df["CustomerID"] = df["CustomerID"].astype(int)

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["is_cancelled"] = df["InvoiceNo"].astype(str).str.startswith("C")

    df["revenue"] = df["Quantity"] * df["UnitPrice"]

    # Transactions table (line-item level)
    transactions = df.rename(
        columns={
            "InvoiceNo": "invoice_no",
            "InvoiceDate": "invoice_date",
            "CustomerID": "customer_id",
            "StockCode": "stock_code",
            "Description": "description",
            "UnitPrice": "unit_price",
            "Country": "country",
        }
    )[
        [
            "invoice_no",
            "invoice_date",
            "customer_id",
            "country",
            "stock_code",
            "description",
            "Quantity",
            "unit_price",
            "revenue",
            "is_cancelled",
        ]
    ].rename(columns={"Quantity": "quantity"})

    # Orders table (invoice-level)
    orders = (
        transactions[~transactions["is_cancelled"]]
        .groupby(["invoice_no", "customer_id", "country", "invoice_date"])
        .agg(order_revenue=("revenue", "sum"))
        .reset_index()
    )

    orders["is_cancelled"] = False

    # Customers table
    customers = (
        orders.groupby("customer_id")
        .agg(
            country=("country", "first"),
            first_purchase_date=("invoice_date", "min"),
            last_purchase_date=("invoice_date", "max"),
            total_orders=("invoice_no", "nunique"),
            total_revenue=("order_revenue", "sum"),
        )
        .reset_index()
    )

    # Write to SQLite
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH}")

    transactions.to_sql("transactions", engine, if_exists="replace", index=False)
    orders.to_sql("orders", engine, if_exists="replace", index=False)
    customers.to_sql("customers", engine, if_exists="replace", index=False)

    print("Database created successfully")
    print("Tables: transactions, orders, customers")


if __name__ == "__main__":
    main()
