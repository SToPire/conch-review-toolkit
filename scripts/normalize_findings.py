#!/usr/bin/env python3
"""Normalize finding payloads from different reviewers into one JSON envelope."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lib.common import emit_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", help="JSON files to normalize")
    return parser.parse_args()


def load_payload(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        if isinstance(data.get("findings"), list):
            return [item for item in data["findings"] if isinstance(item, dict)]
        return [data]
    return []


def normalize(item: dict[str, Any], source: str) -> dict[str, Any]:
    return {
        "source": source,
        "finding_type": item.get("finding_type", "untyped"),
        "severity": item.get("severity", "info"),
        "summary": item.get("summary", ""),
        "evidence": item.get("evidence", []),
        "raw": item,
    }


def main() -> None:
    args = parse_args()
    findings: list[dict[str, Any]] = []
    for raw_path in args.inputs:
        path = Path(raw_path)
        for item in load_payload(path):
            findings.append(normalize(item, str(path)))
    emit_json({"count": len(findings), "findings": findings})


if __name__ == "__main__":
    main()
