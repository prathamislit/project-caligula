"""FINRA short interest data via bulk downloads."""
import requests
import pandas as pd
from io import StringIO
from ..utils.io import write_cache, read_cache


def short_sale_volume(date_yyyymmdd: str):
    key = f"finra_{date_yyyymmdd}"
    cached = read_cache("finra", key)
    if cached is not None:
        return cached
    url = f"https://cdn.finra.org/equity/regsho/daily/CNMSshvol{date_yyyymmdd}.txt"
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        return None
    df = pd.read_csv(StringIO(r.text), sep="|")
    df = df[df["Symbol"].notna()]
    write_cache(df, "finra", key)
    return df


def get_short_interest_for_tickers(tickers: list, date_yyyymmdd: str) -> dict:
    df = short_sale_volume(date_yyyymmdd)
    if df is None or df.empty:
        return {}
    out = {}
    for t in tickers:
        row = df[df["Symbol"] == t]
        if not row.empty:
            out[t] = {
                "short_volume": row["ShortVolume"].iloc[0],
                "total_volume": row["TotalVolume"].iloc[0],
                "short_pct": row["ShortVolume"].iloc[0] / row["TotalVolume"].iloc[0],
            }
    return out
