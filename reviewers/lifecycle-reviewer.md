# lifecycle-reviewer

## Purpose

Audit the sandbox lifecycle as a stateful system, not as isolated functions.

The primary target is the end-to-end lifecycle contract for a sandbox object:

- create
- start or first exec
- pause and resume
- delete
- failure rollback
- repeated calls and idempotency

This reviewer is responsible for whether the lifecycle model is coherent, enforceable, and recoverable under failure.

It is not responsible for reviewing every low-level cleanup primitive or for running the full dynamic environment itself.

## Owned Surface

This reviewer owns lifecycle semantics across the following Conch surfaces:

- daemon request handlers and lifecycle orchestration in `internal/`
- CLI lifecycle entrypoints in `cmd/`
- SDK lifecycle wrappers in `sdk/`
- API contract shape in `api/`
- lifecycle-related user documentation in `README.md` and `docs/`

It should treat the lifecycle as one cross-layer contract, not as separate Go, Python, and docs reviews.

## Primary Questions

- Are state transitions explicit and legal?
- Do partial failures roll back cleanly?
- Are lifecycle preconditions and postconditions consistent across layers?
- Are repeated operations safe and well-defined?
- Are cleanup expectations explicit at the lifecycle level?
- Do CLI, daemon, and SDK expose the same lifecycle semantics?
- Are invalid transitions rejected consistently?

## Lifecycle Model To Audit

At minimum, the reviewer should reason about these lifecycle checkpoints:

1. request accepted
2. sandbox identity allocated
3. host-side resources prepared
4. runtime or VM launched
5. sandbox ready for command execution
6. sandbox paused
7. sandbox resumed
8. sandbox deletion requested
9. sandbox fully removed or rolled back

The exact internal state names may differ in code. The reviewer should map implementation details back to these conceptual checkpoints.

## Evidence Sources

Primary evidence sources:

- lifecycle handlers and orchestration code in `internal/`
- public entrypoints in `cmd/`
- SDK wrapper logic in `sdk/`
- API contracts in `api/`
- lifecycle examples and docs in `README.md` and `docs/`
- unit and integration tests that exercise lifecycle transitions

Secondary evidence sources:

- log messages tied to lifecycle transitions
- cleanup helper calls
- comments that define lifecycle intent
- smoke or e2e outputs produced by other workflows

## Execution Mode

Default mode is static review with evidence from code, tests, and docs.

Optional support mode:

- consume smoke results from `sandbox-e2e-validator`
- consume residue or cleanup evidence from `resource-leak-reviewer`

This reviewer should not require a runnable environment to produce value, but it should be able to incorporate runtime evidence when available.

## Analysis Phases

`<toolkit_root>` refers to the `conch-review-toolkit/` directory that contains this reviewer spec.

### Phase 1: Repository Discovery

Run the repository discovery script first:

```bash
python <toolkit_root>/scripts/discover_conch.py <target_repo>
```

Use the output to confirm that the target repo exposes the expected lifecycle surfaces:

- `cmd/`
- `internal/`
- `sdk/`
- `api/`
- `docs/`

If the target does not look like a Conch repository, stop and report that the reviewer cannot reconstruct the lifecycle contract reliably.

### Phase 2: Entrypoint Collection

Run entrypoint collection:

```bash
python <toolkit_root>/scripts/collect_entrypoints.py <target_repo>
```

Use the `lifecycle` and `sdk` entrypoint groups to build an initial review set. Focus first on:

- sandbox manager and cleanup code
- CLI lifecycle entrypoints
- SDK lifecycle wrappers

### Phase 3: Cross-Layer Lifecycle Reconstruction

Read the relevant code, docs, and tests to reconstruct:

1. how a sandbox is created
2. when it becomes executable
3. how pause and resume behave
4. how delete behaves
5. what rollback or cleanup happens on partial failure

At this stage, map implementation details back to the conceptual lifecycle checkpoints defined above.

### Phase 4: Triage Findings

Group findings by lifecycle phase and classify them using the finding types in this spec.

When smoke evidence is available, use it to confirm or refute static concerns, but do not require smoke execution to complete the review.

## Finding Types

| Finding Type | Description |
|---|---|
| `invalid_state_transition` | A lifecycle operation appears to allow or imply an illegal state transition |
| `missing_precondition_check` | A handler, CLI, or SDK call performs an operation without validating the current lifecycle state |
| `partial_create_no_rollback` | Sandbox creation allocates identity or resources but failure paths do not restore a clean pre-create state |
| `delete_not_terminal` | Delete returns success or completion without guaranteeing terminal cleanup semantics |
| `non_idempotent_lifecycle_operation` | Repeated create, pause, resume, or delete calls appear unsafe or inconsistently handled |
| `cross_layer_lifecycle_mismatch` | CLI, daemon, SDK, or docs disagree about lifecycle semantics |
| `ambiguous_terminal_state` | The implementation does not make it clear whether a failed or deleted sandbox remains addressable |
| `missing_state_observability` | There is no reliable way to infer the sandbox's current lifecycle phase for callers or operators |
| `cleanup_bound_to_happy_path_only` | Lifecycle-level cleanup appears to happen only in the success path, not in all state exits |

## Severity Rules

| Severity | When to use |
|---|---|
| `critical` | A lifecycle flaw can leave a sandbox partially alive, unowned, or undeletable in a way that risks host safety or makes recovery unsafe |
| `high` | A transition, rollback, or terminal-state bug is likely to cause orphaned runtime state, broken user-visible behavior, or repeated operational failure |
| `medium` | Semantics are inconsistent, ambiguous, or weakly enforced but not clearly destructive in the common path |
| `low` | Observability or documentation gaps make lifecycle behavior hard to understand but the implementation appears mostly sound |
| `info` | Notes about lifecycle design tradeoffs, simplification opportunities, or follow-up checks |

Severity should be driven by lifecycle impact, not by local code smell.

## Explicit Out Of Scope

The following are not primary responsibilities of this reviewer:

- proving every individual fd, mount, netns, or process cleanup path
  Those belong to `resource-leak-reviewer`.
- proving lock correctness or race-freedom
  Those belong to `concurrency-reviewer`.
- proving artifact-chain integrity for build or snapshot objects
  Those belong to `image-snapshot-reviewer`.
- proving docs parity in general
  That belongs to `docs-implementation-auditor`, though lifecycle doc mismatches should still be referenced when they affect lifecycle semantics.
- running the environment and validating real sandbox execution from scratch
  That belongs to `sandbox-e2e-validator`.

## Cross-Reviewer Boundaries

### With `resource-leak-reviewer`

This reviewer asks:

- did the lifecycle declare and invoke cleanup in the right state exits?

It does not ask:

- was every concrete resource actually released correctly?

### With `sandbox-e2e-validator`

This reviewer asks:

- does the design and implementation imply a sound lifecycle contract?

The validator asks:

- does that contract survive a real smoke run?

### With `api-sdk-parity-reviewer`

This reviewer owns lifecycle mismatches specifically.

The parity reviewer owns broader behavior mismatches outside lifecycle semantics.

## Expected Output

The final review should include:

- a short lifecycle model reconstructed from the code
- findings grouped by lifecycle checkpoint
- explicit note on create failure rollback
- explicit note on delete terminal semantics
- explicit note on idempotency of pause, resume, and delete
- cross-layer mismatch notes for daemon, CLI, SDK, and docs

## Output Contract

Each finding should include at least:

- `finding_type`
- `severity`
- `component`
- `lifecycle_phase`
- `summary`
- `evidence`
- `user_impact`
- `suggested_followup`

Where:

- `component` is a subsystem or surface such as `daemon`, `cli`, `sdk`, or `docs`
- `lifecycle_phase` is one of `create`, `exec-ready`, `pause`, `resume`, `delete`, `rollback`, or `terminal-state`
- `evidence` points to concrete files and code paths

## Script Wiring

Preferred scripts for this reviewer:

- `discover_conch.py`
- `collect_entrypoints.py`

Optional supporting evidence:

- `run_smoke.py` output from `sandbox-e2e-validator`
- `normalize_findings.py` for command-level synthesis
