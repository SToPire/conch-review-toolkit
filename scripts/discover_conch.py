#!/usr/bin/env python3
"""Discover the high-level shape of a Conch repository."""

from __future__ import annotations

import argparse
from pathlib import Path

from lib.common import emit_json, list_children, repo_root_from, safe_exists


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=".", help="Path inside the Conch repo")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = repo_root_from(Path(args.target))

    payload = {
        "repo_root": str(root),
        "detected": {
            "cmd": safe_exists(root / "cmd"),
            "internal": safe_exists(root / "internal"),
            "sdk": safe_exists(root / "sdk"),
            "api": safe_exists(root / "api"),
            "docs": safe_exists(root / "docs"),
            "config": safe_exists(root / "config"),
        },
        "cmd_entries": list_children(root / "cmd"),
        "internal_entries": list_children(root / "internal"),
        "sdk_entries": list_children(root / "sdk"),
        "docs_entries": list_children(root / "docs"),
        "config_entries": list_children(root / "config"),
    }
    emit_json(payload)


if __name__ == "__main__":
    main()
