"""Load YAML configs and env variables."""
from pathlib import Path
import os
import yaml
import typing
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"

load_dotenv(ROOT / ".env")


def load_universe():
    with open(CONFIG_DIR / "universe.yaml") as f:
        return yaml.safe_load(f)


def load_weights():
    with open(CONFIG_DIR / "weights.yaml") as f:
        return yaml.safe_load(f)


def env(key: str, required: bool = True) -> typing.Optional[str]:
    """Helper to load environment variables defensively.
    
    Args:
        key: The configuration key to fetch.
        required: If True, raises ValueError if the variable is missing or empty.
        
    Returns:
        The string value of the environment variable, or None if not required and missing.
    """
    val = os.getenv(key)
    if required and not val:
        raise ValueError(f"Missing env var: {key}")
    return val
