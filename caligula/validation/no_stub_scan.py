"""Scans production folders for forbidden stub tokens and patterns."""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime

FORBIDDEN_PATTERNS = [
    r"\bTODO\b",
    r"\bFIXME\b",
    r"placeholder",
    r"dummy",
    r"mock",
    r"fake",
    r"sample data",
    r"coming soon",
    r"not implemented",
    r"pass\s*$",
    r"raise NotImplementedError",
    r"except Exception:\s*pass",
    r"console\.log",
    r"print\(",
]

# Paths to scan
SCAN_FOLDERS = ["caligula", "app", "src", "components", "pages", "lib", "scripts"]
IGNORE_FOLDERS = {
    "docs",
    "archive",
    "tests",
    "examples",
    "node_modules",
    ".venv",
    "venv",
    ".next",
    "dist",
    "build",
    "__pycache__",
}


def load_allowlist(root_dir: Path) -> dict:
    allowlist_path = root_dir / "caligula" / "validation" / "stub_allowlist.yml"
    if allowlist_path.exists():
        with open(allowlist_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def scan_directory(root_dir: Path):
    allowlist = load_allowlist(root_dir)
    compiled_patterns = [(p, re.compile(p, re.IGNORECASE)) for p in FORBIDDEN_PATTERNS]

    errors = []

    for folder in SCAN_FOLDERS:
        folder_path = root_dir / folder
        if not folder_path.exists() or not folder_path.is_dir():
            continue

        for dirpath, dirnames, filenames in os.walk(folder_path):
            dirnames[:] = [
                d for d in dirnames if d not in IGNORE_FOLDERS and not d.startswith(".")
            ]

            for filename in filenames:
                if filename.endswith(".pyc") or filename.startswith("."):
                    continue

                filepath = Path(dirpath) / filename
                rel_path = str(filepath.relative_to(root_dir))

                # Check if file is in allowlist and not expired
                if rel_path in allowlist:
                    entry = allowlist[rel_path]
                    expiry = entry.get("expiry_date")
                    if expiry:
                        exp_date = datetime.strptime(str(expiry), "%Y-%m-%d").date()
                        if datetime.now().date() <= exp_date:
                            continue  # Allowed

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                except Exception:
                    continue

                for i, line in enumerate(lines, 1):
                    for pattern_str, regex in compiled_patterns:
                        if regex.search(line):
                            # Avoid safe strings like "passing"; regex handles
                            # most of the matching details.
                            errors.append(
                                f"{rel_path}:{i} - Forbidden pattern: " f"{pattern_str}"
                            )

    if errors:
        print("❌ STUB SCAN FAILED. Found forbidden patterns in production code:")
        for e in errors:
            print(f"  - {e}")
        exit(1)
    else:
        print("✅ STUB SCAN PASSED. No forbidden patterns found in production paths.")


if __name__ == "__main__":
    scan_directory(Path(".").resolve())
