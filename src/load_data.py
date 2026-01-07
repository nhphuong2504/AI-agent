import pandas as pd
from src.config import settings

def load_online_retail(nrows: int | None = None) -> pd.DataFrame:
    """
    Load the Online Retail dataset from Excel and add Revenue.
    Excludes cancellations (InvoiceNo starting with 'C').
    """
    excel_path = settings.online_retail_csv

    # Parse InvoiceDate as datetime
    df = pd.read_excel(
        excel_path,
        nrows=nrows,
        parse_dates=["InvoiceDate"],
    )

    # 1) Exclude cancellations: InvoiceNo starting with 'C'
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]

    # 2) Add Revenue = Quantity * UnitPrice
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]

    return df

if __name__ == "__main__":
    df = load_online_retail(nrows=10)
    print("Rows loaded:", len(df))
    print("Columns:", list(df.columns))
    print(df.head())
