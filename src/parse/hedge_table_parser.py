"""Extract hedge book details from 10-Q/10-K tables."""
import pandas as pd
from bs4 import BeautifulSoup

HEDGE_HEADERS = [
    "weighted average price",
    "swap",
    "collar",
    "barrels per day",
    "mmbtu",
    "fixed price",
]


def find_hedge_tables(html: str):
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")
    candidates = []
    for t in tables:
        text = t.get_text(" ", strip=True).lower()
        score = sum(1 for h in HEDGE_HEADERS if h in text)
        if score >= 2:
            candidates.append((score, t))
    candidates.sort(reverse=True, key=lambda x: x[0])
    return [c[1] for c in candidates[:5]]


def parse_hedge_table(table) -> pd.DataFrame:
    try:
        df = pd.read_html(str(table))[0]
        return df
    except Exception:
        return pd.DataFrame()


def summarize_hedge_book(html: str):
    """Return raw hedge tables for downstream parsing."""
    tables = find_hedge_tables(html)
    if not tables:
        return None
    parsed = [parse_hedge_table(t) for t in tables]
    return {"raw_tables": parsed, "table_count": len(tables)}
