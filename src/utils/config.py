"""Load YAML configs and env variables."""
from pathlib import Path
import os
import yaml
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


def env(key: str, required: bool = True) -> str:
    val = os.getenv(key)
    if required and not val:
        raise ValueError(f"Missing env var: {key}")
    return val
