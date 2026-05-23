"""EIA STEO basin production and rig count data via v2 API."""
import requests
import pandas as pd
from ..utils.config import env
from ..utils.io import write_cache, read_cache

BASE = "https://api.eia.gov/v2"

# Real STEO series IDs discovered via discover_eia.py
PERMIAN_SERIES = {
    "permian_oil_production": "COPRPM",
    "permian_gas_production": "NGMPPM",
    "permian_rig_count": "RIGSPM",
    "permian_duc_wells": "DUCSPM",
    "permian_new_wells_drilled": "NWDPM",
    "permian_tight_oil": "TOPRPM",
}

def get_series(name_or_steo_id, start="2014-01"):
    """Accepts either our internal name or a raw STEO series ID."""
    if name_or_steo_id in PERMIAN_SERIES:
        series_id = PERMIAN_SERIES[name_or_steo_id]
    else:
        series_id = name_or_steo_id

    key = f"eia_{series_id}"
    cached = read_cache("eia", key)
    if cached is not None:
        return cached

    url = f"{BASE}/steo/data/"
    params = {
        "api_key": env("EIA_API_KEY"),
        "frequency": "monthly",
        "data[0]": "value",
        "facets[seriesId][]": series_id,
        "start": start,
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "offset": 0,
        "length": 5000,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    j = r.json()
    rows = j.get("response", {}).get("data", [])
    df = pd.DataFrame(rows)
    if not df.empty and "period" in df.columns:
        df["date"] = pd.to_datetime(df["period"])
    write_cache(df, "eia", key)
    return df
