import pandas as pd
from lifetimes import BetaGeoFitter, GammaGammaFitter  # type: ignore
from sqlalchemy import text

from src.db import engine


def load_clv_features() -> pd.DataFrame:
    """
    Load CLV features from the clv_features table.
    """
    with engine.begin() as conn:
        df = pd.read_sql(text("SELECT * FROM clv_features"), conn)

    # lifetimes expects:
    # frequency, recency, T, monetary_value
    # Ensure correct dtypes
    df["frequency"] = df["frequency"].astype(float)
    df["recency"] = df["recency"].astype(float)
    df["T"] = df["T"].astype(float)
    df["monetary_value"] = df["monetary_value"].astype(float)

    return df


def fit_bg_nbd_gg(df: pd.DataFrame):
    """
    Fit BG/NBD and Gamma-Gamma models to the provided CLV features DataFrame.
    Returns fitted bgf, ggf and the df filtered for valid monetary_value.
    """
    # BG/NBD works with all customers (including frequency=0)
    bgf = BetaGeoFitter(penalizer_coef=0.0)
    bgf.fit(
        frequency=df["frequency"],
        recency=df["recency"],
        T=df["T"],
    )
    print("Fitted BG/NBD model.")

    # Gamma-Gamma requires customers with:
    # - frequency > 0
    # - monetary_value > 0
    df_gg = df[(df["frequency"] > 0) & (df["monetary_value"] > 0)].copy()

    ggf = GammaGammaFitter(penalizer_coef=0.0)
    ggf.fit(
        frequency=df_gg["frequency"],
        monetary_value=df_gg["monetary_value"],
    )
    print("Fitted Gamma-Gamma model on", len(df_gg), "customers.")

    return bgf, ggf, df_gg


def compute_predicted_clv(
    bgf: BetaGeoFitter,
    ggf: GammaGammaFitter,
    df_gg: pd.DataFrame,
    time: float = 12.0,
    freq: str = "D",
    discount_rate: float = 0.01,
) -> pd.DataFrame:
    """
    Compute predicted customer lifetime value using BG/NBD + Gamma-Gamma.

    Parameters:
    - time: prediction horizon (e.g., 12 months if freq='M' and you adjust units)
    - freq: transaction frequency unit, must match how recency/T are expressed. [web:22][web:27]
    - discount_rate: per-period discount rate.

    Returns:
    A DataFrame with CustomerID, predicted_clv and the original features.
    """
    # lifetimes has a helper for CLV:
    # ggf.customer_lifetime_value(bgf, frequency, recency, T, monetary_value, time, freq, discount_rate)
    clv_values = ggf.customer_lifetime_value(
        bgf,
        df_gg["frequency"],
        df_gg["recency"],
        df_gg["T"],
        df_gg["monetary_value"],
        time=time,
        freq=freq,
        discount_rate=discount_rate,
    )  

    result = df_gg.copy()
    result["predicted_clv"] = clv_values
    return result


def main():
    # 1) Load CLV features
    df = load_clv_features()
    print("Loaded clv_features with", len(df), "rows.")

    # 2) Fit models
    bgf, ggf, df_gg = fit_bg_nbd_gg(df)

    # 3) Compute CLV over a 1-month horizon 
    clv_df = compute_predicted_clv(
        bgf,
        ggf,
        df_gg,
        time=30,      # 12 periods
        freq="D",     # since recency/T are in days
        discount_rate=0.01,
    )

    # 4) Rank customers by predicted CLV
    clv_df = clv_df.sort_values("predicted_clv", ascending=False)

    print("\nTop 10 customers by predicted CLV:")
    print(clv_df[["CustomerID", "frequency", "recency", "T", "monetary_value", "predicted_clv"]].head(10))

    # Optional: write back to DB as clv_predictions table
    # with engine.begin() as conn:
    #     print("\nWriting CLV predictions to clv_predictions table...")
    #     conn.execute(text("DROP TABLE IF EXISTS clv_predictions"))
    #     clv_df.to_sql(
    #         "clv_predictions",
    #         con=conn.connection,
    #         if_exists="replace",
    #         index=False,
    #     )
    #     print("Done.")


if __name__ == "__main__":
    main()
