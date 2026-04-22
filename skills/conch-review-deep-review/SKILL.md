---
name: conch-review-deep-review
description: Run an evidence-heavy deep review of a specific Conch subsystem, operation, or failure class. Use when the user wants a focused investigation such as lifecycle correctness, snapshot behavior, cleanup bugs, parity drift, docs drift, or trust-boundary analysis.
---

# Conch Review Deep Review

Use this skill when the question is no longer "where should we look?" but "what is actually wrong in this specific area?"

## Inputs

- `target_repo`: path to the Conch repository
- `focus`: required subsystem, operation, or failure class
- optional `scope`: narrower file or directory set
- optional `reviewers`: explicit reviewer subset if already known

Default target repo: `/home/stopire/Conch`

## Load These Assets

- `policies/severity.md`
- `policies/report-template.md`

Load reviewers based on focus:

- lifecycle -> `reviewers/lifecycle-reviewer.md`
- image or snapshot -> `reviewers/image-snapshot-reviewer.md`
- cleanup -> `reviewers/resource-leak-reviewer.md`
- concurrency -> `reviewers/concurrency-reviewer.md`
- parity -> `reviewers/api-sdk-parity-reviewer.md`
- docs -> `reviewers/docs-implementation-auditor.md`
- safety -> `reviewers/security-boundary-reviewer.md`
- runtime validation -> `reviewers/sandbox-e2e-validator.md`

Use these scripts:

- `scripts/discover_conch.py`
- `scripts/collect_entrypoints.py`
- `scripts/run_smoke.py` when runtime evidence is needed
- `scripts/normalize_findings.py` when you need a unified findings envelope

## Workflow

### 1. Require a clear focus

If the user did not provide a real focus, stop and ask for one concise target such as:

- sandbox create/delete lifecycle
- build -> unpack -> snapshot chain
- cleanup after failed create
- SDK/API parity
- docs versus implementation

Do not silently degrade into a broad health review.

### 2. Discover the repo shape

Run:

```bash
python3 scripts/discover_conch.py <target_repo>
```

### 3. Collect likely entrypoints

Run:

```bash
python3 scripts/collect_entrypoints.py <target_repo>
```

Use the result to narrow the evidence set before dispatching reviewers.

### 4. Select and dispatch reviewers

Pick the reviewer subset that matches the focus. Use reviewer boundaries strictly. Deep review means tracing the path with enough surrounding code and documentation to support a strong conclusion.

### 5. Add runtime evidence when needed

If static evidence is not enough, run:

```bash
python3 scripts/run_smoke.py <target_repo> --mode probe-only
```

or, if appropriate:

```bash
python3 scripts/run_smoke.py <target_repo> --mode execute
```

Use runtime evidence to support the review, not to replace static reasoning.

### 6. Synthesize a focused report

Use `policies/report-template.md` as the output skeleton.

Produce:

- clear focus definition
- participating reviewers
- evidence-backed findings grouped by concern
- open questions
- recommended next action: fix, investigate further, or validate more deeply

## Constraints

- Preserve reviewer boundaries.
- Call out uncertainty explicitly.
- Do not broaden into a general dashboard.
- If the task turns into pure runtime validation, switch to `conch-review-smoke`.
