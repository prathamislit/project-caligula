"""Cache reads/writes to local disk to avoid re-hitting APIs."""

from pathlib import Path
import pandas as pd
import json
from .config import DATA_DIR


def cache_path(category: str, key: str, ext: str = "parquet") -> Path:
    p = DATA_DIR / "raw" / category
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{key}.{ext}"


def read_cache(category: str, key: str, ext: str = "parquet"):
    p = cache_path(category, key, ext)
    if not p.exists():
        return None
    if ext == "parquet":
        return pd.read_parquet(p)
    if ext == "json":
        return json.loads(p.read_text())
    return p.read_text()


def write_cache(obj, category: str, key: str, ext: str = "parquet"):
    p = cache_path(category, key, ext)
    if ext == "parquet":
        obj.to_parquet(p)
    elif ext == "json":
        p.write_text(json.dumps(obj, default=str, indent=2))
    else:
        p.write_text(obj)
    return p
