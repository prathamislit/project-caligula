"""Pillar 7: Market & Sentiment Signals."""
import pandas as pd
import numpy as np
from ..ingest.edgar_client import get_filing_index
from ..ingest.price_client import get_prices


def insider_net_buying_6mo(cik: str, as_of: pd.Timestamp):
    """Insider net purchase activity proxied by Form 4 filing frequency in the trailing 180 days."""
    try:
        filings = get_filing_index(cik, "4")
    except Exception:
        return None

    if not filings:
        return 0.0

    six_mo_ago = as_of - pd.Timedelta(days=180)
    recent = [
        f for f in filings
        if pd.Timestamp(f["date"]) >= six_mo_ago
        and pd.Timestamp(f["date"]) <= as_of
    ]
    return float(len(recent))


def institutional_ownership_change(ticker: str, as_of: pd.Timestamp):
    """Institutional accumulation proxy using equity volume trend. Higher is bullish."""
    px = get_prices(ticker)
    if px is None or px.empty:
        return None
    px = px.copy()
    px["date"] = pd.to_datetime(px["date"])
    px = px[px["date"] <= as_of].sort_values("date")
    if len(px) < 120:
        return None
    
    # Compare recent 60 days vs prior 60 days volume trend
    recent_vol = px["volume"].tail(60).mean()
    prior_vol = px["volume"].iloc[-120:-60].mean()
    if prior_vol == 0:
        return None
    return float((recent_vol - prior_vol) / prior_vol)


def short_interest_relative(ticker: str, as_of: pd.Timestamp):
    """Short interest proxy calculated as down-volume vs up-volume trailing 30 days. Lower is better."""
    px = get_prices(ticker)
    if px is None or px.empty:
        return None
    px = px.copy()
    px["date"] = pd.to_datetime(px["date"])
    px = px[px["date"] <= as_of].sort_values("date")
    if len(px) < 30:
        return None

    recent = px.tail(30).copy()
    recent["ret"] = recent["close"].pct_change()
    down_vol = recent.loc[recent["ret"] < 0, "volume"].sum()
    up_vol = recent.loc[recent["ret"] > 0, "volume"].sum()
    if up_vol == 0:
        return None
    return float(down_vol / up_vol)


def options_put_call_skew(ticker: str, as_of: pd.Timestamp):
    """Options put-call skew proxy derived from trailing price volatility. Higher is more fearful."""
    px = get_prices(ticker)
    if px is None or px.empty:
        return None
    px = px.copy()
    px["date"] = pd.to_datetime(px["date"])
    px = px[px["date"] <= as_of].sort_values("date")
    if len(px) < 20:
        return None
    
    # Volatility of daily returns as a proxy for premium/skew fear
    returns = px["close"].pct_change().tail(20)
    return float(returns.std() * np.sqrt(252))


def analyst_revision_breadth(ticker: str, as_of: pd.Timestamp):
    """Consensus analyst sentiment breadth proxied by momentum of returns trailing 60 days. Higher is bullish."""
    px = get_prices(ticker)
    if px is None or px.empty:
        return None
    px = px.copy()
    px["date"] = pd.to_datetime(px["date"])
    px = px[px["date"] <= as_of].sort_values("date")
    if len(px) < 60:
        return None
    
    # Price change ratio representing revision momentum
    recent_px = px["close"].iloc[-1]
    prior_px = px["close"].iloc[-60]
    if prior_px == 0:
        return None
    return float((recent_px - prior_px) / prior_px)


def all_sentiment_metrics(cik: str, ticker: str, as_of: pd.Timestamp) -> dict:
    return {
        "insider_net_buying_6mo": insider_net_buying_6mo(cik, as_of),
        "institutional_ownership_change": institutional_ownership_change(ticker, as_of),
        "short_interest_relative": short_interest_relative(ticker, as_of),
        "options_put_call_skew": options_put_call_skew(ticker, as_of),
        "analyst_revision_breadth": analyst_revision_breadth(ticker, as_of),
    }
