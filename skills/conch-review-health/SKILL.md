---
name: conch-review-health
description: Produce a fast multi-dimension health snapshot for the Conch project and identify the highest-priority hotspots. Use when the user wants an overall review, quick risk scan, system health check, or guidance on what subsystem to inspect next.
---

# Conch Review Health

Use this skill when the user wants a broad status view of `Conch` plus a clear sense of what deserves attention first, not a deep audit of one narrow issue.

## Inputs

- `target_repo`: path to the Conch repository
- optional `scope`: subsystem or directory to emphasize

Default target repo: `/home/stopire/Conch`

## Load These Assets

- `policies/severity.md`
- `policies/report-template.md`
- `reviewers/lifecycle-reviewer.md`
- `reviewers/image-snapshot-reviewer.md`
- `reviewers/resource-leak-reviewer.md`
- `reviewers/concurrency-reviewer.md`
- `reviewers/api-sdk-parity-reviewer.md`
- `reviewers/security-boundary-reviewer.md`
- `reviewers/docs-implementation-auditor.md`

Use these scripts:

- `scripts/discover_conch.py`
- `scripts/collect_entrypoints.py`
- `scripts/normalize_findings.py` when you need a unified findings envelope

## Workflow

### 1. Discover the repo shape

Run:

```bash
python3 scripts/discover_conch.py <target_repo>
```

Stop if the repo does not look like `Conch` or if the result is too incomplete to support a reliable health snapshot.

### 2. Collect likely entrypoints

Run:

```bash
python3 scripts/collect_entrypoints.py <target_repo>
```

Use this output to identify the highest-signal surfaces for lifecycle, image/snapshot, and SDK-facing review.

### 3. Dispatch summary-oriented reviewers

Use the loaded reviewer specs in summary mode. Do not let any one reviewer turn this into a deep audit.

Target review dimensions:

- lifecycle soundness
- image/snapshot artifact integrity
- cleanup and residue risk
- concurrency and teardown overlap
- API/CLI/SDK parity
- security boundary posture
- docs versus implementation drift

### 4. Synthesize a dashboard

Use `policies/report-template.md` as the output skeleton.

Produce:

- repository profile
- per-dimension status: `green`, `yellow`, or `red`
- 1-3 top findings per dimension at most
- top 3 overall priorities
- ranked hotspots with short rationale
- recommended next workflow: `conch-review-deep-review` or `conch-review-smoke`

## Constraints

- Prefer breadth over depth.
- Every yellow or red dimension should cite evidence.
- Merge duplicate findings when several reviewers are describing the same operational problem.
- Include hotspot ranking, but do not turn the skill into a full evidence-heavy deep review.
- If the user really wants one path audited in detail, switch to `conch-review-deep-review`.
