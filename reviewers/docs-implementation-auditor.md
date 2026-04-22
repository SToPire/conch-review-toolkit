# docs-implementation-auditor

## Purpose

Audit whether public documentation matches the implementation.

The primary target is operationally relevant documentation drift, not editorial quality.

## Owned Surface

This reviewer owns documentation parity across:

- README and architecture docs
- CLI help and real flags
- config docs and actual config parsing
- SDK examples and real SDK behavior
- API docs and handler behavior

This reviewer should focus on statements that a user or operator could act on.

## Primary Questions

- Do documented commands, flags, and config keys exist and behave as described?
- Are required preconditions documented where users need them?
- Do examples reflect the actual SDK and CLI behavior?
- Are implementation-visible constraints missing from docs?
- Are there important behaviors that exist in code but not in docs?
- Are docs still aligned with the current artifact, lifecycle, and API contracts?

## Documentation Surfaces To Audit

At minimum, compare these pairs:

1. `README.md` and CLI behavior
2. `docs/` architecture and actual subsystem boundaries
3. config docs and config loading or defaults
4. SDK examples and real SDK methods
5. API docs and handler behavior

## Evidence Sources

Primary evidence sources:

- `README.md`
- `docs/`
- CLI flag definitions and help output sources in `cmd/`
- config types and parsers in `config/` or related modules
- SDK code in `sdk/`
- API contracts in `api/`
- tests that assert documented behavior

Secondary evidence sources:

- inline comments or docstrings that define a behavior not otherwise documented
- examples under `examples/`
- sample command output embedded in docs

## Execution Mode

Default mode is static review using docs, code, config, examples, and tests.

Optional support mode:

- consume generated CLI help dumps from future scripts
- consume normalized config-schema or API summaries from future scripts

This reviewer should be fully useful without a runnable environment.

## Analysis Phases

`<toolkit_root>` refers to the `conch-review-toolkit/` directory that contains this reviewer spec.

### Phase 1: Repository Discovery

Run repository discovery first:

```bash
python <toolkit_root>/scripts/discover_conch.py <target_repo>
```

Use the output to confirm the expected documentation and implementation surfaces exist:

- `README.md`
- `docs/`
- `cmd/`
- `config/`
- `sdk/`
- `api/`

### Phase 2: Entrypoint Collection

Run entrypoint collection:

```bash
python <toolkit_root>/scripts/collect_entrypoints.py <target_repo>
```

Use the result to prioritize which documented flows to compare first. Focus first on:

- lifecycle examples
- build and unpack docs
- SDK examples

### Phase 3: Doc-to-Code Comparison

For each chosen doc surface:

1. identify the user-actionable statement in docs
2. find the matching implementation surface in CLI, config, SDK, API, or daemon code
3. compare names, defaults, required preconditions, and behavior
4. note any behavior present in code but absent from docs

At minimum compare:

- README versus CLI and lifecycle behavior
- docs versus current subsystem responsibilities
- config docs versus config parsing
- SDK examples versus actual SDK APIs
- API docs versus handler behavior

### Phase 4: Triage Findings

Group findings by doc surface and classify them using the finding types in this spec.

When later smoke or parity evidence exists, use it to validate whether the documented behavior is wrong in a user-visible way.

## Finding Types

| Finding Type | Description |
|---|---|
| `stale_example` | A documented example no longer matches the current implementation |
| `missing_precondition_doc` | A required precondition exists in practice but is not documented where a user needs it |
| `documented_flag_missing` | A documented command flag, subcommand, or config key does not exist |
| `undocumented_behavior` | Important behavior exists in implementation but is absent from docs |
| `docs_code_semantics_mismatch` | Docs describe a behavior or contract differently from the code |
| `sdk_example_mismatch` | SDK examples rely on methods, orderings, or assumptions not reflected in the SDK implementation |
| `architecture_doc_drift` | Architecture docs no longer match current module responsibilities or control flow |
| `partial_doc_update` | One doc surface was updated while related docs or examples were left stale |

## Severity Rules

| Severity | When to use |
|---|---|
| `critical` | Documentation drift is likely to cause destructive or unrecoverable user action |
| `high` | Drift is likely to break real user workflows, setup, or automation |
| `medium` | Drift materially misleads users but is recoverable without major damage |
| `low` | Drift is confusing or outdated but not likely to break common usage |
| `info` | Documentation improvement suggestions and follow-up notes |

## Explicit Out Of Scope

This reviewer is not primarily responsible for:

- proving lifecycle logic is correct
  That belongs to `lifecycle-reviewer`.
- proving API, CLI, and SDK behavioral parity in depth
  That belongs to `api-sdk-parity-reviewer`.
- proving safety or trust-boundary correctness
  That belongs to `security-boundary-reviewer`.
- running the environment to see if the docs work in practice
  That belongs to dynamic validation workflows.

## Cross-Reviewer Boundaries

### With `api-sdk-parity-reviewer`

This reviewer asks:

- do the docs match the implementation?

The parity reviewer asks:

- do the surfaces match each other, even aside from docs?

### With `security-boundary-reviewer`

This reviewer owns general documentation drift.

The security reviewer owns doc mismatches specifically when they understate risk or isolation semantics.

## Expected Output

The final review should include:

- a short map of documentation surfaces checked
- findings grouped by doc surface
- explicit note on stale examples
- explicit note on hidden preconditions
- explicit note on implementation behaviors that should be documented

## Output Contract

Each finding should include at least:

- `finding_type`
- `severity`
- `doc_surface`
- `implementation_surface`
- `summary`
- `evidence`
- `user_impact`
- `suggested_followup`

Where:

- `doc_surface` is a location such as `README`, `architecture-doc`, `config-doc`, `sdk-example`, or `api-doc`
- `implementation_surface` is a location such as `cli`, `daemon`, `sdk`, `config`, or `api`
- `evidence` points to concrete files and code paths

## Script Wiring

Preferred scripts for this reviewer:

- `discover_conch.py`
- `collect_entrypoints.py`

Optional supporting evidence:

- `run_smoke.py` output when it reveals missing prerequisites in docs
- `normalize_findings.py` for command-level synthesis
