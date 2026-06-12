"""Equity and futures price data via yfinance."""
import yfinance as yf
import pandas as pd
from ..utils.io import write_cache, read_cache


def get_prices(ticker: str, start="2014-01-01", end=None, force_refresh=False):
    key = f"px_{ticker}"
    if not force_refresh:
        cached = read_cache("prices", key)
        if cached is not None:
            if cached.empty:
                return None
            return cached
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    if df.empty:
        # Cache an empty DataFrame to avoid redundant yfinance API hits for delisted tickers
        write_cache(pd.DataFrame(), "prices", key)
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    df.columns = [c.lower() if isinstance(c, str) else c for c in df.columns]
    write_cache(df, "prices", key)
    return df


def get_options_chain(ticker: str):
    t = yf.Ticker(ticker)
    try:
        expirations = t.options
        if not expirations:
            return None
        exp = expirations[min(len(expirations) - 1, 4)]
        chain = t.option_chain(exp)
        return {"expiration": exp, "calls": chain.calls, "puts": chain.puts}
    except Exception:
        return None


def get_universe_prices(tickers: list, start="2014-01-01") -> dict:
    return {t: get_prices(t, start=start) for t in tickers}
