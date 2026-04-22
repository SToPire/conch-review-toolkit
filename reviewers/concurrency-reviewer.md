# concurrency-reviewer

## Purpose

Audit concurrency, shared state, and teardown races in the Go daemon and helpers.

The primary target is whether Conch's control plane and teardown flows remain coherent under concurrent use.

## Owned Surface

This reviewer owns concurrency questions across:

- goroutine-spawning daemon paths in `internal/`
- shared state in manager, handler, or runtime coordination code
- teardown and cleanup paths that can overlap with requests
- helper packages that coordinate async work or cancellation

## Primary Questions

- Which state is shared across goroutines?
- Are lock boundaries coherent?
- Can cleanup race with request handling?
- Are background tasks cancellable and drained?
- Are state transitions synchronized at the right granularity?
- Can one sandbox's teardown affect another request path?
- Are long-running operations interruptible or abandoned cleanly?

## Concurrency Model To Audit

At minimum, the reviewer should reason about:

1. request handler concurrency
2. manager or registry shared state
3. async launch or teardown workers
4. cancellation and shutdown propagation
5. cleanup occurring concurrently with active operations

## Evidence Sources

Primary evidence sources:

- `internal/` daemon, manager, and helper packages
- goroutine creation sites
- locking and synchronization primitives
- context propagation and cancellation code
- tests that cover concurrent behavior or shutdown

Secondary evidence sources:

- logs describing concurrent operations or teardown
- comments describing lock intent or thread-safety assumptions
- smoke failures that hint at race-prone transitions

## Execution Mode

Default mode is static review using code, tests, comments, and logs.

Optional support mode:

- consume smoke or stress-run traces from future dynamic workflows
- consume future normalized lock, goroutine, or context summaries

This reviewer should produce first-wave value without dedicated race testing.

## Analysis Phases

`<toolkit_root>` refers to the `conch-review-toolkit/` directory that contains this reviewer spec.

### Phase 1: Repository Discovery

Run repository discovery first:

```bash
python <toolkit_root>/scripts/discover_conch.py <target_repo>
```

Use the output to confirm the expected concurrency-relevant surfaces exist:

- `internal/`
- `cmd/`
- `config/`

### Phase 2: Entrypoint Collection

Run entrypoint collection:

```bash
python <toolkit_root>/scripts/collect_entrypoints.py <target_repo>
```

Use the `lifecycle` group to prioritize the first-pass review set. Focus first on:

- sandbox manager paths
- cleanup and teardown paths
- request handlers that can overlap with teardown

### Phase 3: Shared-State and Shutdown Reconstruction

For each chosen area:

1. identify shared state and its owner
2. identify where goroutines are spawned
3. identify synchronization primitives and their intended scope
4. identify cancellation and shutdown propagation
5. identify where teardown can overlap with active request processing

Look explicitly for:

- lock coverage gaps
- background tasks with unclear lifetime
- state transitions that can race
- shutdown sequences without drain or join behavior

### Phase 4: Triage Findings

Group findings by concurrency area and classify them using the finding types in this spec.

When dynamic evidence exists later, use it as supporting confirmation rather than as a first-pass requirement.

## Finding Types

| Finding Type | Description |
|---|---|
| `shared_state_unsafeguarded` | Shared mutable state appears accessed without coherent synchronization |
| `cleanup_request_race` | Teardown or cleanup can plausibly race with an active request path |
| `lock_scope_mismatch` | Lock coverage appears too narrow, too broad, or inconsistent for the protected state |
| `cancellation_not_propagated` | Background work appears not to respect request or shutdown cancellation |
| `background_task_not_drained` | Async work may outlive the owning operation without clear handoff or join semantics |
| `cross_sandbox_interference_risk` | Shared concurrency control can let one sandbox operation affect another unexpectedly |
| `state_transition_race` | Lifecycle-relevant state updates appear vulnerable to concurrent mutation |
| `shutdown_coordination_gap` | Service shutdown and worker cleanup do not appear coordinated |

## Severity Rules

| Severity | When to use |
|---|---|
| `critical` | A race or shutdown bug can corrupt shared state, break isolation, or leave unrecoverable runtime state |
| `high` | A bug is likely to cause real request failures, teardown breakage, or orphaned concurrent work |
| `medium` | Synchronization intent is weak, partial, or inconsistent, but the impact is not yet clearly severe |
| `low` | Concurrency design is confusing or hard to verify but not clearly broken on common paths |
| `info` | Notes on concurrency design simplification or follow-up stress checks |

## Explicit Out Of Scope

This reviewer is not primarily responsible for:

- abstract lifecycle semantics
  That belongs to `lifecycle-reviewer`.
- concrete per-resource cleanup correctness
  That belongs to `resource-leak-reviewer`.
- safety boundary analysis
  That belongs to `security-boundary-reviewer`.
- running dedicated race or load tests
  That belongs to future dynamic validation tooling.

## Cross-Reviewer Boundaries

### With `resource-leak-reviewer`

This reviewer asks:

- can concurrent teardown or request handling make cleanup unsafe?

The resource reviewer asks:

- was the resource actually reclaimed on all paths?

### With `lifecycle-reviewer`

This reviewer owns race-driven lifecycle instability.

The lifecycle reviewer owns the nominal lifecycle contract.

## Expected Output

The final review should include:

- shared-state domains inspected
- findings grouped by concurrency risk class
- explicit note on teardown versus request overlap
- explicit note on cancellation and shutdown coordination
- explicit note on cross-sandbox interference risk

## Output Contract

Each finding should include at least:

- `finding_type`
- `severity`
- `concurrency_area`
- `component`
- `summary`
- `evidence`
- `user_impact`
- `suggested_followup`

Where:

- `concurrency_area` is one of `shared-state`, `locking`, `request-cleanup-overlap`, `cancellation`, `background-work`, or `shutdown`
- `component` is a subsystem such as `daemon`, `manager`, `runtime-helper`, or `registry`
- `evidence` points to concrete files and code paths

## Script Wiring

Preferred scripts for this reviewer:

- `discover_conch.py`
- `collect_entrypoints.py`

Optional supporting evidence:

- `run_smoke.py` output when it reveals shutdown or overlap symptoms
- `normalize_findings.py` for command-level synthesis
