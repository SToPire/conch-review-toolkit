# resource-leak-reviewer

## Purpose

Audit non-memory-safe resource ownership and cleanup across the Conch control plane and sandbox-management flows.

The primary target is resource lifetime correctness under normal exit, early return, partial failure, and repeated cleanup.

This reviewer is about concrete resource release behavior, not abstract lifecycle semantics.

## Owned Surface

This reviewer owns resource-lifetime questions across:

- file descriptors
- mounts
- namespaces
- processes
- snapshots
- temporary files and directories

- daemon-side resource acquisition and cleanup in `internal/`
- CLI or helper flows in `cmd/` that create runtime state
- helper scripts or wrappers that create temporary state
- config-driven behaviors that alter resource allocation or retention

## Primary Questions

- What allocates or opens the resource?
- Where is it released?
- What happens on early return or partial failure?
- Is cleanup retried or orphaned?
- Is ownership transferred explicitly or only implied?
- Are terminal cleanup paths convergent, or does each path clean different subsets?

## Resource Model To Audit

At minimum, the reviewer should reason about these resource classes:

1. file descriptors and files
2. mounts and mount points
3. namespaces and network state
4. child processes or runtime handles
5. snapshots or temporary artifact state
6. temporary directories and working files

For each resource, the reviewer should try to identify:

- acquisition point
- owner
- transfer point if any
- cleanup point
- failure-path cleanup behavior

## Evidence Sources

Primary evidence sources:

- `internal/` resource-management code
- `cmd/` entrypoints that allocate or tear down resources
- helper scripts under `scripts/`
- tests that cover cleanup behavior
- comments or logs that describe cleanup expectations

Secondary evidence sources:

- docs that describe deletion or cleanup guarantees
- smoke results from `sandbox-e2e-validator`
- lifecycle findings that indicate missing terminal cleanup

## Execution Mode

Default mode is static review using code, tests, docs, and logs.

Optional support mode:

- consume smoke-run residue evidence
- consume future normalized summaries of opened resources or cleanup helpers

This reviewer should produce useful findings without requiring full runtime execution.

## Analysis Phases

`<toolkit_root>` refers to the `conch-review-toolkit/` directory that contains this reviewer spec.

### Phase 1: Repository Discovery

Run repository discovery first:

```bash
python <toolkit_root>/scripts/discover_conch.py <target_repo>
```

Use the output to confirm the expected resource-owning surfaces exist:

- `cmd/`
- `internal/`
- `scripts/`
- `config/`

If the target does not look like a Conch repository, stop and report that resource-lifetime conclusions would be unreliable.

### Phase 2: Entrypoint Collection

Run entrypoint collection:

```bash
python <toolkit_root>/scripts/collect_entrypoints.py <target_repo>
```

Use the `lifecycle` and `image_snapshot` groups to prioritize the first-pass review set. Focus first on:

- cleanup helpers
- sandbox teardown paths
- build and unpack failure paths
- script-driven setup and cleanup logic

### Phase 3: Ownership and Cleanup Reconstruction

For each chosen path:

1. identify where the resource is acquired
2. identify the apparent owner
3. identify all normal and failure exits
4. verify whether cleanup is explicit on each exit
5. note any ownership transfer that is only implied

Track these resource classes explicitly:

- fd
- mount
- namespace
- process
- snapshot
- tempdir
- tempfile

### Phase 4: Triage Findings

Group findings by resource class and classify them using the finding types in this spec.

When smoke evidence is available, use it to confirm likely residue or cleanup gaps, but do not require smoke execution to complete the review.

## Finding Types

| Finding Type | Description |
|---|---|
| `missing_cleanup_path` | A resource is acquired but no clear cleanup path exists |
| `failure_path_resource_leak` | A resource appears to leak specifically on error or partial-failure paths |
| `orphaned_process_or_handle` | Process or runtime handles may outlive the owning request or sandbox |
| `double_cleanup_risk` | Ownership or cleanup semantics are ambiguous enough to risk double release |
| `cleanup_order_hazard` | Cleanup order appears unsafe or inconsistent with dependencies |
| `resource_ownership_implicit` | The code relies on undocumented ownership transfer semantics |
| `residue_after_terminal_operation` | Delete or teardown appears not to reclaim a resource class completely |
| `cross_layer_cleanup_mismatch` | Docs, lifecycle behavior, or implementation disagree about cleanup guarantees |

## Severity Rules

| Severity | When to use |
|---|---|
| `critical` | A leak or cleanup bug can leave dangerous runtime state, host resources, or unrecoverable residue behind |
| `high` | A bug is likely to leave orphaned resources or break repeated operations in real usage |
| `medium` | Cleanup semantics are incomplete, inconsistent, or weakly documented but not clearly catastrophic |
| `low` | Ownership or cleanup behavior is confusing but likely still safe in the common path |
| `info` | Notes on cleanup simplification, observability, or follow-up checks |

## Explicit Out Of Scope

This reviewer is not primarily responsible for:

- whether lifecycle transitions are legal
  That belongs to `lifecycle-reviewer`.
- whether locks, goroutines, and races are correct
  That belongs to `concurrency-reviewer`.
- whether artifact relationships are semantically correct
  That belongs to `image-snapshot-reviewer`.
- proving dynamic smoke success from scratch
  That belongs to `sandbox-e2e-validator`.

## Cross-Reviewer Boundaries

### With `lifecycle-reviewer`

This reviewer asks:

- were actual resources released?

The lifecycle reviewer asks:

- did the lifecycle contract invoke cleanup in the right state exits?

### With `sandbox-e2e-validator`

This reviewer reasons about likely residue from code and evidence.

The validator can confirm residue empirically after smoke runs.

## Expected Output

The final review should include:

- resource classes inspected
- findings grouped by resource class
- explicit note on failure-path cleanup
- explicit note on delete or teardown residue
- explicit note on ownership transfer assumptions

## Output Contract

Each finding should include at least:

- `finding_type`
- `severity`
- `resource_class`
- `component`
- `summary`
- `evidence`
- `user_impact`
- `suggested_followup`

Where:

- `resource_class` is one of `fd`, `mount`, `namespace`, `process`, `snapshot`, `tempdir`, or `tempfile`
- `component` is a subsystem or surface such as `daemon`, `cli`, `script`, or `runtime-helper`
- `evidence` points to concrete files and code paths

## Script Wiring

Preferred scripts for this reviewer:

- `discover_conch.py`
- `collect_entrypoints.py`

Optional supporting evidence:

- `run_smoke.py` output from `sandbox-e2e-validator`
- `normalize_findings.py` for command-level synthesis
