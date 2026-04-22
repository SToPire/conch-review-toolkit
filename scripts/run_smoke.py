#!/usr/bin/env python3
"""Run a minimal Conch smoke validation in probe-only or execute mode."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from lib.common import emit_json, repo_root_from, safe_exists


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=".", help="Path inside the Conch repo")
    parser.add_argument(
        "--mode",
        choices=("probe-only", "execute"),
        default="probe-only",
        help="Only probe readiness or actually attempt a smoke path",
    )
    parser.add_argument(
        "--conchd",
        default=None,
        help="Path to conchd binary. Defaults to <repo>/bin/conchd if present.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="Timeout in seconds for daemon launch and smoke commands.",
    )
    return parser.parse_args()


def step(name: str, status: str, summary: str, **extra: Any) -> dict[str, Any]:
    payload = {"step": name, "status": status, "summary": summary}
    payload.update(extra)
    return payload


def probe_environment(root: Path, conchd_path: Path) -> list[dict[str, Any]]:
    steps = []
    required = {
        "repo_root": root.exists(),
        "bin_dir": safe_exists(root / "bin"),
        "config_dir": safe_exists(root / "config"),
        "sdk_dir": safe_exists(root / "sdk"),
        "conchd": safe_exists(conchd_path),
    }
    missing = [name for name, ok in required.items() if not ok]
    if missing:
        steps.append(
            step(
                "readiness",
                "failed",
                "Missing required local prerequisites for smoke validation.",
                missing=missing,
            )
        )
    else:
        steps.append(step("readiness", "passed", "Local repository prerequisites look present."))

    deps = {
        "containerd": shutil.which("containerd") is not None,
        "cloud-hypervisor": shutil.which("cloud-hypervisor") is not None,
    }
    missing_deps = [name for name, ok in deps.items() if not ok]
    if missing_deps:
        steps.append(
            step(
                "environment",
                "warning",
                "Some external runtime dependencies are missing from PATH.",
                missing=missing_deps,
            )
        )
    else:
        steps.append(step("environment", "passed", "Basic external runtime dependencies are present."))
    return steps


def try_launch_daemon(conchd_path: Path, timeout: int) -> dict[str, Any]:
    try:
        proc = subprocess.Popen(
            [str(conchd_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError as exc:
        return step("daemon", "failed", "Failed to start conchd.", error=str(exc))

    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.terminate()
        return step(
            "daemon",
            "passed",
            "conchd stayed alive long enough to satisfy a minimal launch probe.",
            note="Process terminated after timeout window to avoid leaking a daemon during smoke validation.",
        )

    return step(
        "daemon",
        "failed" if proc.returncode else "passed",
        "conchd exited during launch probe." if proc.returncode else "conchd exited cleanly during probe.",
        returncode=proc.returncode,
        stdout=stdout.strip(),
        stderr=stderr.strip(),
    )


def main() -> None:
    args = parse_args()
    root = repo_root_from(Path(args.target))
    conchd_path = Path(args.conchd) if args.conchd else root / "bin" / "conchd"

    steps: list[dict[str, Any]] = []
    steps.extend(probe_environment(root, conchd_path))

    if args.mode == "execute":
        if all(item["status"] != "failed" for item in steps if item["step"] == "readiness"):
            steps.append(try_launch_daemon(conchd_path, args.timeout))
            steps.append(
                step(
                    "create",
                    "skipped",
                    "Concrete sandbox create/exec/delete is not implemented yet in v0.1 smoke runner.",
                )
            )
            steps.append(
                step(
                    "residue",
                    "skipped",
                    "Residue inspection is deferred until create/delete support exists.",
                )
            )
        else:
            steps.append(step("daemon", "skipped", "Skipped daemon launch due to readiness failure."))
    else:
        steps.append(step("daemon", "skipped", "Probe-only mode does not launch conchd."))

    failures = [item for item in steps if item["status"] == "failed"]
    warnings = [item for item in steps if item["status"] == "warning"]
    payload = {
        "repo_root": str(root),
        "mode": args.mode,
        "conchd": str(conchd_path),
        "steps": steps,
        "summary": {
            "failed_steps": len(failures),
            "warning_steps": len(warnings),
            "status": "failed" if failures else "warning" if warnings else "passed",
        },
        "environment": {
            "cwd": os.getcwd(),
        },
    }
    emit_json(payload)


if __name__ == "__main__":
    main()
