import pandas as pd
from sqlalchemy import text

from src.db import engine, init_db


def build_clv_features() -> None:
    """
    Build CLV-ready features per customer and store in clv_features table.

    For each CustomerID:
    - num_invoices: distinct InvoiceNo
    - frequency: max(num_invoices - 1, 0)
    - recency: (last_purchase_date - first_purchase_date) in days
    - T: (observation_end_date - first_purchase_date) in days
    - monetary_value: total_revenue / num_invoices
    plus basic info: total_revenue, first/last_purchase_date.
    """
    # Ensure tables exist
    init_db()

    # Load customers table (for first/last purchase + totals)
    with engine.begin() as conn:
        customers_df = pd.read_sql(text("SELECT * FROM customers"), conn)
        transactions_df = pd.read_sql(
            text("SELECT CustomerID, InvoiceNo, InvoiceDate, Revenue FROM transactions"),
            conn,
        )

    if customers_df.empty or transactions_df.empty:
        print("customers or transactions table is empty. Did you run load_to_db and build_customers?")
        return

    # Parse dates
    customers_df["first_purchase_date"] = pd.to_datetime(customers_df["first_purchase_date"])
    customers_df["last_purchase_date"] = pd.to_datetime(customers_df["last_purchase_date"])
    transactions_df["InvoiceDate"] = pd.to_datetime(transactions_df["InvoiceDate"])

    # Determine observation end date as max InvoiceDate in the whole dataset
    observation_end_date = transactions_df["InvoiceDate"].max()
    print("Observation end date:", observation_end_date)

    # Compute num_invoices per customer from transactions (distinct InvoiceNo)
    invoice_counts = (
        transactions_df.groupby("CustomerID")["InvoiceNo"]
        .nunique()
        .rename("num_invoices")
    )

    # Merge counts into customers_df
    clv_df = customers_df.merge(
        invoice_counts,
        on="CustomerID",
        how="left",
    )

    # Fill missing num_invoices with 0 (just in case)
    clv_df["num_invoices"] = clv_df["num_invoices"].fillna(0).astype(int)

    # frequency = max(num_invoices - 1, 0)
    clv_df["frequency"] = (clv_df["num_invoices"] - 1).clip(lower=0)

    # recency = (last_purchase_date - first_purchase_date).days
    clv_df["recency"] = (
        clv_df["last_purchase_date"] - clv_df["first_purchase_date"]
    ).dt.days.astype(float)

    # T = (observation_end_date - first_purchase_date).days
    clv_df["T"] = (
        observation_end_date - clv_df["first_purchase_date"]
    ).dt.days.astype(float)

    # monetary_value = total_revenue / num_invoices
    # Avoid division by zero
    clv_df["monetary_value"] = clv_df["total_revenue"] / clv_df["num_invoices"].replace(0, pd.NA)
    clv_df["monetary_value"] = clv_df["monetary_value"].astype(float)

    # Convert dates back to strings for storage
    clv_df["first_purchase_date"] = clv_df["first_purchase_date"].astype(str)
    clv_df["last_purchase_date"] = clv_df["last_purchase_date"].astype(str)

    # Select and order columns for the clv_features table
    clv_df = clv_df[
        [
            "CustomerID",
            "frequency",
            "recency",
            "T",
            "monetary_value",
            "num_invoices",
            "total_revenue",
            "first_purchase_date",
            "last_purchase_date",
        ]
    ]

    print("Built clv_df with", len(clv_df), "rows.")

    # Write to clv_features table (replace existing content)
    with engine.begin() as conn:
        print("Clearing existing clv_features table...")
        conn.execute(text("DELETE FROM clv_features"))

        print("Inserting CLV feature records...")
        clv_df.to_sql(
            "clv_features",
            con=conn.connection,
            if_exists="append",
            index=False,
        )

    print("Done. clv_features table updated.")


if __name__ == "__main__":
    build_clv_features()
