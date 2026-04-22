# Severity Policy

## Levels

- `critical`: data loss, privilege boundary break, unrecoverable sandbox lifecycle corruption, destructive cleanup bug
- `high`: likely runtime failure, leaked host resource, broken artifact chain, invalid state transition
- `medium`: behavior mismatch, incomplete cleanup coverage, concurrency smell with plausible impact
- `low`: maintainability issue, weak documentation, incomplete observability
- `info`: neutral observations and follow-up ideas

## Reporting rules

- Dynamic validation failures should state whether the root cause looks environmental or product-related.
- Documentation mismatches should specify which side appears stale.
- Cross-reviewer duplicate findings should be merged in the final report.
