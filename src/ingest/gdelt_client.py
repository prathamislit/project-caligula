"""GDELT 2.0 event data for basin/sector sentiment."""
import requests
import pandas as pd
from io import StringIO
import zipfile
import io
from ..utils.io import write_cache, read_cache

GDELT_BASE = "http://data.gdeltproject.org/gdeltv2"
EVENT_COLS = [
    "GLOBALEVENTID", "SQLDATE", "MonthYear", "Year", "FractionDate",
    "Actor1Code", "Actor1Name", "Actor1CountryCode", "Actor1KnownGroupCode",
    "Actor1EthnicCode", "Actor1Religion1Code", "Actor1Religion2Code",
    "Actor1Type1Code", "Actor1Type2Code", "Actor1Type3Code",
    "Actor2Code", "Actor2Name", "Actor2CountryCode", "Actor2KnownGroupCode",
    "Actor2EthnicCode", "Actor2Religion1Code", "Actor2Religion2Code",
    "Actor2Type1Code", "Actor2Type2Code", "Actor2Type3Code",
    "IsRootEvent", "EventCode", "EventBaseCode", "EventRootCode",
    "QuadClass", "GoldsteinScale", "NumMentions", "NumSources",
    "NumArticles", "AvgTone", "Actor1Geo_Type", "Actor1Geo_FullName",
    "Actor1Geo_CountryCode", "Actor1Geo_ADM1Code", "Actor1Geo_ADM2Code",
    "Actor1Geo_Lat", "Actor1Geo_Long", "Actor1Geo_FeatureID",
    "Actor2Geo_Type", "Actor2Geo_FullName", "Actor2Geo_CountryCode",
    "Actor2Geo_ADM1Code", "Actor2Geo_ADM2Code", "Actor2Geo_Lat",
    "Actor2Geo_Long", "Actor2Geo_FeatureID", "ActionGeo_Type",
    "ActionGeo_FullName", "ActionGeo_CountryCode", "ActionGeo_ADM1Code",
    "ActionGeo_ADM2Code", "ActionGeo_Lat", "ActionGeo_Long",
    "ActionGeo_FeatureID", "DATEADDED", "SOURCEURL",
]


def fetch_daily_events(yyyymmdd: str):
    key = f"gdelt_{yyyymmdd}"
    cached = read_cache("gdelt", key)
    if cached is not None:
        return cached
    url = f"{GDELT_BASE}/{yyyymmdd}000000.export.CSV.zip"
    r = requests.get(url, timeout=60)
    if r.status_code != 200:
        return None
    z = zipfile.ZipFile(io.BytesIO(r.content))
    name = z.namelist()[0]
    df = pd.read_csv(z.open(name), sep="\t", names=EVENT_COLS, low_memory=False)
    mask = (
        df["ActionGeo_ADM1Code"].isin(["USTX", "USNM"]) |
        df["Actor1Name"].fillna("").str.contains("OIL|ENERGY|PETROLEUM", case=False) |
        df["Actor2Name"].fillna("").str.contains("OIL|ENERGY|PETROLEUM", case=False)
    )
    df = df[mask].copy()
    write_cache(df, "gdelt", key)
    return df


def daily_sentiment_avg(yyyymmdd: str):
    df = fetch_daily_events(yyyymmdd)
    if df is None or df.empty:
        return None
    return {
        "date": yyyymmdd,
        "avg_tone": df["AvgTone"].mean(),
        "avg_goldstein": df["GoldsteinScale"].mean(),
        "event_count": len(df),
    }
