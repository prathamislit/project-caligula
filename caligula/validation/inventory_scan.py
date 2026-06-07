"""Scan the codebase and output an inventory report."""

import os
import argparse
import csv
from pathlib import Path


def count_lines(filepath: Path) -> int:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def get_file_type(filepath: Path) -> str:
    return filepath.suffix.lstrip(".") if filepath.suffix else "unknown"


def main():
    parser = argparse.ArgumentParser(
        description="Scan codebase and generate inventory."
    )
    parser.add_argument("--root", type=str, default=".", help="Root directory to scan")
    parser.add_argument(
        "--output",
        type=str,
        default="outputs/tables/codebase_inventory.csv",
        help="Output CSV path",
    )
    args = parser.parse_args()

    root_path = Path(args.root).resolve()
    output_path = Path(args.output).resolve()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    ignore_dirs = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        ".next",
        "dist",
        "build",
        ".pytest_cache",
        "__pycache__",
    }

    # Basic mappings for status based on known directories in the cleanup plan
    # Legacy src/ and eog_dcf/ files are marked for migration or rewrite.

    rows = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [
            d for d in dirnames if d not in ignore_dirs and not d.startswith(".")
        ]

        for file in filenames:
            if file.startswith(".") and file not in {".env.example", ".gitignore"}:
                continue

            filepath = Path(dirpath) / file
            rel_path = filepath.relative_to(root_path)

            line_count = count_lines(filepath)
            file_type = get_file_type(filepath)

            status = "KEEP"
            action = "none"

            path_str = str(rel_path)

            if "src/" in path_str or "eog_dcf/" in path_str:
                status = "REWRITE"
                action = "move_archive"
            if file.endswith(".ipynb"):
                status = "ARCHIVE"
                action = "move_archive"
            if "TODO" in path_str or "temp" in path_str or "manual" in path_str:
                status = "DELETE"
                action = "delete_unused"

            rows.append(
                {
                    "path": path_str,
                    "file_type": file_type,
                    "line_count": line_count,
                    "imports": "",
                    "exports": "",
                    "referenced_by": "",
                    "references": "",
                    "purpose": "General component",
                    "status": status,
                    "cleanup_action": action,
                }
            )

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "path",
                "file_type",
                "line_count",
                "imports",
                "exports",
                "referenced_by",
                "references",
                "purpose",
                "status",
                "cleanup_action",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Inventory saved to {output_path}")


if __name__ == "__main__":
    main()
