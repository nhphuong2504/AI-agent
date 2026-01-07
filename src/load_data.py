import pandas as pd
from src.config import settings

def load_online_retail(nrows: int | None = None) -> pd.DataFrame:
    """
    Load the Online Retail dataset from Excel.
    nrows: load only this many rows for quick tests.
    """
    excel_path = settings.online_retail_csv
    # For .xlsx we use read_excel; engine auto-detected if openpyxl is installed
    df = pd.read_excel(excel_path, nrows=nrows)
    return df

if __name__ == "__main__":
    df = load_online_retail(nrows=5)
    print("Loaded rows:", len(df))
    print(df.head())
