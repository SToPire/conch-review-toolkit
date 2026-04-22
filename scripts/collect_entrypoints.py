#!/usr/bin/env python3
"""Collect likely Conch review entrypoints across code and docs."""

from __future__ import annotations

import argparse
from pathlib import Path

from lib.common import emit_json, repo_root_from


KEYWORDS = {
    "lifecycle": ("create", "pause", "resume", "delete", "sandbox"),
    "image_snapshot": ("build", "unpack", "snapshot", "rootfs", "kernel"),
    "sdk": ("Sandbox", "create", "execute", "delete"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=".", help="Path inside the Conch repo")
    return parser.parse_args()


def collect_files(root: Path, base: str) -> list[str]:
    path = root / base
    if not path.exists():
        return []
    ignored_parts = {"__pycache__"}
    ignored_suffixes = {".pyc"}
    return sorted(
        str(p.relative_to(root))
        for p in path.rglob("*")
        if p.is_file()
        and not any(part in ignored_parts for part in p.parts)
        and p.suffix not in ignored_suffixes
    )


def classify(files: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {name: [] for name in KEYWORDS}
    for filename in files:
        lowered = filename.lower()
        for label, words in KEYWORDS.items():
            if any(word.lower() in lowered for word in words):
                result[label].append(filename)
    return {label: sorted(set(entries)) for label, entries in result.items()}


def main() -> None:
    args = parse_args()
    root = repo_root_from(Path(args.target))
    files = []
    for base in ("cmd", "internal", "sdk", "api", "docs", "config"):
        files.extend(collect_files(root, base))

    payload = {
        "repo_root": str(root),
        "file_count": len(files),
        "entrypoints": classify(files),
    }
    emit_json(payload)


if __name__ == "__main__":
    main()
