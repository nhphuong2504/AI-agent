from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from src.config import settings

# Create a SQLAlchemy engine for SQLite
engine: Engine = create_engine(
    settings.database_url,
    echo=False,        # set True if you want to see SQL logs
    future=True,
)

def init_db():
    """
    Create core tables if they do not exist.
    - transactions
    - customers
    """
    create_transactions_sql = text("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        InvoiceNo TEXT,
        StockCode TEXT,
        Description TEXT,
        Quantity INTEGER,
        InvoiceDate TEXT,
        UnitPrice REAL,
        CustomerID INTEGER,
        Country TEXT,
        Revenue REAL
    );
    """)

    create_customers_sql = text("""
    CREATE TABLE IF NOT EXISTS customers (
        CustomerID INTEGER PRIMARY KEY,
        Country TEXT,
        first_purchase_date TEXT,
        last_purchase_date TEXT,
        num_transactions INTEGER,
        total_quantity INTEGER,
        total_revenue REAL,
        avg_order_value REAL
    );
    """)

    create_clv_features_sql = text("""
    CREATE TABLE IF NOT EXISTS clv_features (
        CustomerID INTEGER PRIMARY KEY,
        frequency INTEGER,
        recency REAL,
        T REAL,
        monetary_value REAL,
        num_invoices INTEGER,
        total_revenue REAL,
        first_purchase_date TEXT,
        last_purchase_date TEXT
    );
    """)


    with engine.begin() as conn:
        conn.execute(create_transactions_sql)
        conn.execute(create_customers_sql)
        conn.execute(create_clv_features_sql)
