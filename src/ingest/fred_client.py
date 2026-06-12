"""FRED macro data client."""
from fredapi import Fred
from ..utils.config import env
from ..utils.io import write_cache, read_cache

SERIES = {
    "wti_spot": "DCOILWTICO",
    "hh_gas": "DHHNGSP",
    "ig_spread": "BAMLC0A0CM",
    "hy_spread": "BAMLH0A0HYM2",
    "dxy": "DTWEXBGS",
    "ust_10y": "DGS10",
    "ust_2y": "DGS2",
}


def get_series(series_id: str, start="2014-01-01"):
    key = f"fred_{series_id}"
    cached = read_cache("fred", key)
    if cached is not None:
        return cached
    fred = Fred(api_key=env("FRED_API_KEY"))
    s = fred.get_series(series_id, observation_start=start)
    df = s.to_frame(name=series_id).reset_index().rename(columns={"index": "date"})
    write_cache(df, "fred", key)
    return df


def get_all_macros(start="2014-01-01"):
    return {name: get_series(sid, start) for name, sid in SERIES.items()}
