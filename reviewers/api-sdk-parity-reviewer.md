# api-sdk-parity-reviewer

## Purpose

Compare behavior across public interaction surfaces:

- API contracts
- daemon handlers
- CLI behavior
- Python SDK behavior

The primary target is user-visible behavioral parity, not internal code style or implementation detail.

## Owned Surface

This reviewer owns parity questions across:

- `api/` contract definitions
- request and response handling in `internal/`
- CLI entrypoints in `cmd/`
- Python SDK calls and wrappers in `sdk/`
- usage examples in `README.md` and `docs/` when they express API behavior

## Primary Questions

- Do all surfaces expose the same lifecycle semantics?
- Are errors, defaults, and validation rules aligned?
- Do parameter names and meanings match?
- Are return values and failure modes meaningfully equivalent?
- Does the SDK encode hidden assumptions not present in the daemon?
- Do CLI affordances imply behaviors not backed by the API?

## Parity Model To Audit

For each important operation, the reviewer should compare:

1. documented or declared input shape
2. CLI argument behavior
3. SDK call shape and defaults
4. daemon validation and execution semantics
5. returned result or error surface

The first-wave focus should be on:

- create
- exec
- pause
- resume
- delete
- build and unpack if these are exposed through multiple surfaces

## Evidence Sources

Primary evidence sources:

- `api/*.proto` and related types
- daemon handlers and validation logic in `internal/`
- CLI flags and command logic in `cmd/`
- SDK wrapper methods and config handling in `sdk/`
- public examples in `README.md` and `docs/`
- tests that compare or indirectly exercise multiple surfaces

Secondary evidence sources:

- CLI help text
- comments or docstrings that define preconditions
- integration logs showing request or error shapes

## Execution Mode

Default mode is static review using code, docs, and tests.

Optional support mode:

- consume smoke or integration traces from dynamic workflows
- consume normalized flag and method extraction from future scripts

This reviewer should not require a runnable environment for first-wave usefulness.

## Analysis Phases

`<toolkit_root>` refers to the `conch-review-toolkit/` directory that contains this reviewer spec.

### Phase 1: Repository Discovery

Run repository discovery first:

```bash
python <toolkit_root>/scripts/discover_conch.py <target_repo>
```

Confirm that the target exposes the expected parity surfaces:

- `api/`
- `internal/`
- `cmd/`
- `sdk/`
- `docs/`

### Phase 2: Entrypoint Collection

Run entrypoint collection:

```bash
python <toolkit_root>/scripts/collect_entrypoints.py <target_repo>
```

Use the `sdk` and `lifecycle` entrypoint groups to prioritize which operations to compare first. Focus first on:

- create
- exec
- pause
- resume
- delete

### Phase 3: Cross-Surface Comparison

For each chosen operation:

1. inspect API contract shape
2. inspect daemon validation and execution
3. inspect CLI flags and behavior
4. inspect SDK wrapper behavior and defaults
5. inspect examples or docs that express a user-facing contract

### Phase 4: Triage Findings

Group findings by operation and classify them using the finding types in this spec.

When later smoke or integration evidence exists, use it to validate whether a mismatch is user-visible in practice.

## Finding Types

| Finding Type | Description |
|---|---|
| `parameter_semantics_mismatch` | Two surfaces expose the same operation but interpret a parameter differently |
| `default_behavior_mismatch` | Defaults differ across CLI, API, SDK, or docs in a user-visible way |
| `validation_rule_mismatch` | One surface accepts or rejects inputs differently from another |
| `error_surface_mismatch` | Failure types, messages, or success criteria differ materially across surfaces |
| `hidden_sdk_assumption` | The SDK adds an undocumented precondition, default, or transformation not reflected in the API contract |
| `cli_api_contract_gap` | CLI behavior implies a contract not actually present in daemon or API handling |
| `docs_example_behavior_mismatch` | Public examples encode behavior that does not match implementation |
| `lifecycle_parity_gap` | Lifecycle operations differ across surfaces in a user-visible way |

## Severity Rules

| Severity | When to use |
|---|---|
| `critical` | A parity bug can cause destructive or irrecoverable behavior because different surfaces disagree on what an operation means |
| `high` | A mismatch is likely to break real usage, automation, or client code in a reproducible way |
| `medium` | Behavior differs materially but the impact is narrower or recoverable |
| `low` | The mismatch is confusing or surprising but not likely to break common usage |
| `info` | Notes on API surface simplification, consistency opportunities, or follow-up checks |

## Explicit Out Of Scope

This reviewer is not primarily responsible for:

- low-level lifecycle state-machine soundness
  That belongs to `lifecycle-reviewer`.
- trust-boundary or isolation analysis
  That belongs to `security-boundary-reviewer`.
- general docs drift unrelated to behavior parity
  That belongs to `docs-implementation-auditor`.
- proving dynamic environment correctness
  That belongs to `sandbox-e2e-validator`.

## Cross-Reviewer Boundaries

### With `lifecycle-reviewer`

This reviewer owns cross-surface lifecycle mismatches.

The lifecycle reviewer owns whether the lifecycle contract itself is sound.

### With `docs-implementation-auditor`

This reviewer references docs when they express a behavioral contract.

The docs auditor owns broader documentation coverage and staleness.

## Expected Output

The final review should include:

- a short list of operations compared across surfaces
- findings grouped by operation
- explicit note on default mismatches
- explicit note on error and validation mismatches
- explicit note on SDK-only assumptions

## Output Contract

Each finding should include at least:

- `finding_type`
- `severity`
- `operation`
- `surfaces`
- `summary`
- `evidence`
- `user_impact`
- `suggested_followup`

Where:

- `operation` is an action such as `create`, `exec`, `pause`, `resume`, `delete`, `build`, or `unpack`
- `surfaces` is a list such as `api`, `daemon`, `cli`, `sdk`, `docs`
- `evidence` points to concrete files and code paths

## Script Wiring

Preferred scripts for this reviewer:

- `discover_conch.py`
- `collect_entrypoints.py`

Optional supporting evidence:

- `normalize_findings.py` for command-level synthesis
