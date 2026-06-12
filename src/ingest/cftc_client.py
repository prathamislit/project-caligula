"""CFTC Commitment of Traders — WTI managed money positioning."""
import requests
import pandas as pd
from io import StringIO
from ..utils.io import write_cache, read_cache

COT_URL = "https://www.cftc.gov/dea/newcot/deafut.txt"


def fetch_cot_latest():
    key = "cot_latest"
    cached = read_cache("cftc", key)
    if cached is not None:
        return cached
    r = requests.get(COT_URL, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(StringIO(r.text))
    wti = df[df["CFTC_Contract_Market_Code"].astype(str).str.startswith("067")].copy()
    write_cache(wti, "cftc", key)
    return wti


def fetch_cot_historical(years: list = None):
    """Pull annual COT archives for backtest."""
    import zipfile, io as _io
    if years is None:
        years = list(range(2014, 2026))
    frames = []
    for yr in years:
        url = f"https://www.cftc.gov/files/dea/history/deahistfo{yr}.zip"
        r = requests.get(url, timeout=60)
        if r.status_code != 200:
            continue
        z = zipfile.ZipFile(_io.BytesIO(r.content))
        name = z.namelist()[0]
        df = pd.read_csv(z.open(name))
        wti = df[df["CFTC_Contract_Market_Code"].astype(str).str.startswith("067")].copy()
        frames.append(wti)
    if not frames:
        return None
    combined = pd.concat(frames, ignore_index=True)
    write_cache(combined, "cftc", "cot_historical")
    return combined
