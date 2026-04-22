---
name: conch-review-smoke
description: Run minimal runtime validation for Conch and separate environment-readiness problems from product behavior problems. Use when the user wants to actually bring Conch up, run a smoke path, or verify whether failures are environmental or implementation-related.
---

# Conch Review Smoke

Use this skill when the user wants runtime evidence rather than a purely static review.

## Inputs

- `target_repo`: path to the Conch repository
- optional `mode`: `probe-only` or `execute`

Default target repo: `/home/stopire/Conch`
Default mode: `probe-only`

## Load These Assets

- `policies/severity.md`
- `policies/report-template.md`
- `reviewers/sandbox-e2e-validator.md`

Support reviewers when interpretation needs them:

- `reviewers/lifecycle-reviewer.md`
- `reviewers/docs-implementation-auditor.md`

Use these scripts:

- `scripts/discover_conch.py`
- `scripts/run_smoke.py`
- `scripts/normalize_findings.py` when you need a unified findings envelope

## Workflow

### 1. Discover the repo shape

Run:

```bash
python3 scripts/discover_conch.py <target_repo>
```

### 2. Run readiness probe

Run:

```bash
python3 scripts/run_smoke.py <target_repo> --mode probe-only
```

If readiness fails, stop there and report the result as an environment-readiness outcome unless there is clear evidence of a product defect.

### 3. Run execution mode when requested

If the user asked for execution mode and readiness passed, run:

```bash
python3 scripts/run_smoke.py <target_repo> --mode execute
```

### 4. Interpret the result

Use `sandbox-e2e-validator` as the primary reviewer for diagnosis. Pull in:

- `lifecycle-reviewer` when a runtime failure suggests a lifecycle contract problem
- `docs-implementation-auditor` when the runtime failure contradicts operator-facing instructions or examples

### 5. Report a step-by-step smoke outcome

Use `policies/report-template.md` as the output skeleton.

Produce:

- environment readiness status
- smoke steps attempted
- pass/fail/skipped per step
- environment versus product diagnosis
- current smoke-runner limitations
- recommended next action

## Constraints

- Be explicit about what was actually executed versus only probed.
- Do not overclaim product correctness from a shallow smoke pass.
- If deeper static reasoning is required, recommend `conch-review-deep-review`.
