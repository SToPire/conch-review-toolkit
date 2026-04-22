#!/usr/bin/env python3
"""Shared helpers for harness-neutral Conch review scripts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def emit_json(payload: dict[str, Any]) -> None:
    """Write a JSON payload with a trailing newline."""
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def repo_root_from(start: Path) -> Path:
    """Best-effort locate the Conch repo root from a starting path."""
    current = start.resolve()
    if current.is_file():
        current = current.parent
    markers = ("go.mod", "README.md", "cmd", "internal", "sdk", "api")
    for candidate in (current, *current.parents):
        if all((candidate / marker).exists() for marker in markers):
            return candidate
    return current


def safe_exists(path: Path) -> bool:
    """Return False on permission or OS errors instead of raising."""
    try:
        return path.exists()
    except OSError:
        return False


def list_children(path: Path) -> list[str]:
    """Return sorted child names for a directory, or an empty list."""
    try:
        ignored_suffixes = (".pyc",)
        ignored_names = {"__pycache__"}
        return sorted(
            child.name
            for child in path.iterdir()
            if child.name not in ignored_names
            and not any(child.name.endswith(suffix) for suffix in ignored_suffixes)
        )
    except OSError:
        return []
