import pandas as pd
from sqlalchemy import text
from src.db import engine, init_db


def build_customers_table() -> None:
    """
    Aggregate transactions into a customers table.

    For each CustomerID:
    - Country: most frequent country (or any, if tied)
    - first_purchase_date: earliest InvoiceDate
    - last_purchase_date: latest InvoiceDate
    - num_transactions: number of distinct invoices
    - total_quantity: sum of Quantity
    - total_revenue: sum of Revenue
    - avg_order_value: total_revenue / num_transactions
    """
    # Ensure tables exist
    init_db()

    # Load all transactions into pandas
    print("Loading transactions from DB...")
    with engine.begin() as conn:
        df = pd.read_sql(text("SELECT * FROM transactions"), conn)

    if df.empty:
        print("No transactions found. Did you run load_to_db?")
        return

    # Convert InvoiceDate back to datetime for proper min/max
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    # Aggregate at customer level
    # num_transactions = number of distinct InvoiceNo
    customer_group = df.groupby("CustomerID")

    # Basic aggregates
    first_purchase = customer_group["InvoiceDate"].min()
    last_purchase = customer_group["InvoiceDate"].max()
    num_transactions = customer_group["InvoiceNo"].nunique()
    total_quantity = customer_group["Quantity"].sum()
    total_revenue = customer_group["Revenue"].sum()

    # Derive avg_order_value (avoid division by zero)
    avg_order_value = total_revenue / num_transactions.replace(0, pd.NA)

    # Country: take the most frequent country per customer
    country_mode = customer_group["Country"].agg(lambda x: x.mode().iat[0] if not x.mode().empty else None)

    customers_df = pd.DataFrame({
        "CustomerID": first_purchase.index,
        "Country": country_mode.values,
        "first_purchase_date": first_purchase.values,
        "last_purchase_date": last_purchase.values,
        "num_transactions": num_transactions.values,
        "total_quantity": total_quantity.values,
        "total_revenue": total_revenue.values,
        "avg_order_value": avg_order_value.values,
    })

    # Convert dates to ISO strings for storage
    customers_df["first_purchase_date"] = customers_df["first_purchase_date"].astype(str)
    customers_df["last_purchase_date"] = customers_df["last_purchase_date"].astype(str)

    print(f"Built customers_df with {len(customers_df)} rows.")

    # Write to DB (replace existing customers table content)
    with engine.begin() as conn:
        print("Clearing existing customers table...")
        conn.execute(text("DELETE FROM customers"))

        print("Inserting aggregated customer records...")
        customers_df.to_sql(
            "customers",
            con=conn.connection,
            if_exists="append",
            index=False,
        )

    print("Done. customers table updated.")


if __name__ == "__main__":
    build_customers_table()
