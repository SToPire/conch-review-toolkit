# Conch Review Toolkit

Review toolkit scaffold for the `Conch` project.

- `https://atomgit.com/openeuler/Conch`

It currently centers on three installable skills:

- `conch-review-health`: broad health snapshot, top priorities, and hotspot ranking
- `conch-review-deep-review`: focused evidence-heavy review for one subsystem, path, or failure class
- `conch-review-smoke`: minimal runtime validation and environment-versus-product diagnosis

The shared assets behind those skills are:

- `reviewers/`: reusable reviewer specs and subagent guides
- `scripts/`: shared discovery, normalization, and smoke-runner logic
- `policies/`: common severity and report-shape rules

## Reviewers

The first reviewer set is:

- `lifecycle-reviewer`
- `image-snapshot-reviewer`
- `resource-leak-reviewer`
- `concurrency-reviewer`
- `api-sdk-parity-reviewer`
- `security-boundary-reviewer`
- `docs-implementation-auditor`
- `sandbox-e2e-validator`

## Scripts

The first script set is:

- `discover_conch.py`
- `collect_entrypoints.py`
- `normalize_findings.py`
- `run_smoke.py`

## Acknowledgement

This toolkit was heavily inspired by `cext-review-toolkit`:

- `https://github.com/devdanzin/cext-review-toolkit`
