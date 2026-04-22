# Scripts

This directory is reserved for harness-neutral executable logic.

Planned categories:

- discovery
- static analyzers
- smoke runners
- environment probes
- report normalizers

Current v0.1 scripts:

- `discover_conch.py`
- `collect_entrypoints.py`
- `normalize_findings.py`
- `run_smoke.py`

## Design rule

Scripts should accept ordinary CLI arguments and produce machine-readable output so they can be called from Codex, Claude Code, or any future harness.
