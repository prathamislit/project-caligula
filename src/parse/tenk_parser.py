"""Extract structured data from 10-K filings."""
import re
from bs4 import BeautifulSoup
import pandas as pd


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(separator="\n")


def find_section(text: str, heading_patterns: list, max_chars: int = 50000):
    for pat in heading_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return text[m.start():m.start() + max_chars]
    return None


def extract_reserves_section(text: str):
    return find_section(text, [
        r"reserves?\s+(replacement|disclosure)",
        r"proved\s+(developed|undeveloped)\s+reserves?",
        r"oil\s+and\s+gas\s+reserves?",
    ])


def extract_hedge_section(text: str):
    return find_section(text, [
        r"commodity\s+(price\s+)?(risk|hedg)",
        r"derivative\s+(instruments|financial)",
        r"hedging\s+activities",
    ])


def extract_xbrl_metric(facts: dict, metric: str, units: str = "USD"):
    try:
        node = facts["facts"]["us-gaap"][metric]["units"][units]
        df = pd.DataFrame(node)
        df["end"] = pd.to_datetime(df["end"])
        return df
    except KeyError:
        return None
