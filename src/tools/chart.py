from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd


CHART_DIR = Path("data/charts")
CHART_DIR.mkdir(parents=True, exist_ok=True)


def _safe_filename(name: str) -> str:
    keep = "".join(c if c.isalnum() or c in "-_." else "_" for c in name)
    return keep[:120] or "chart"


def make_chart(df: pd.DataFrame, title: str = "Chart") -> Optional[Path]:
    """
    Heuristic charting:
    - If 2 columns and first is time-like -> line chart
    - Else if 2 columns and second numeric -> bar chart
    Returns path to saved PNG, or None if we can't chart.
    """
    if df is None or df.empty:
        return None
    if df.shape[1] < 2:
        return None

    xcol = df.columns[0]
    ycol = df.columns[1]

    # Try to parse x as datetime (works for 'YYYY-MM' strings too)
    x = df[xcol]
    x_dt = None
    try:
        x_dt = pd.to_datetime(x, errors="coerce")
    except Exception:
        x_dt = None

    y = pd.to_numeric(df[ycol], errors="coerce")

    if y.isna().all():
        return None

    plt.figure()
    if x_dt is not None and x_dt.notna().mean() > 0.8:
        # line chart
        plt.plot(x_dt, y)
        plt.xlabel(xcol)
        plt.ylabel(ycol)
    else:
        # bar chart (top-k)
        df2 = df.copy()
        df2[ycol] = y
        df2 = df2.dropna(subset=[ycol]).head(25)
        plt.bar(df2[xcol].astype(str), df2[ycol])
        plt.xlabel(xcol)
        plt.ylabel(ycol)
        plt.xticks(rotation=45, ha="right")

    plt.title(title)
    plt.tight_layout()

    out = CHART_DIR / f"{_safe_filename(title)}.png"
    plt.savefig(out, dpi=160)
    plt.close()
    return out
