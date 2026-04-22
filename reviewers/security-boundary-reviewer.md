# security-boundary-reviewer

## Purpose

Audit isolation and trust boundaries in a sandbox engine.

The primary target is where Conch crosses privilege, isolation, filesystem, network, process, or host-resource boundaries.

## Owned Surface

This reviewer owns boundary questions across:

- daemon request handling in `internal/`
- sandbox launch and configuration paths
- CLI-exposed knobs in `cmd/`
- SDK options that influence trust or isolation
- config defaults and override handling
- public docs that advertise or downplay isolation-related behavior

## Primary Questions

- Which inputs cross privilege boundaries?
- Which commands or config values can widen isolation unexpectedly?
- Where are host resources mounted, shared, or reused?
- Are dangerous defaults documented and gated?
- Which operations assume trust in caller-provided paths, images, or commands?
- Are privileged actions clearly separated from unprivileged control logic?
- Are reuse and sharing mechanisms bounded and observable?

## Boundary Model To Audit

At minimum, the reviewer should reason about these boundary classes:

1. caller input to daemon control path
2. daemon control path to host resource manipulation
3. host resources to sandbox runtime
4. shared cache, snapshot, or network reuse across sandboxes
5. config or flags that alter the above boundaries

## Evidence Sources

Primary evidence sources:

- request validation and execution paths in `internal/`
- launch or isolation-related code in runtime-facing modules
- CLI flags and config wiring in `cmd/` and `config/`
- SDK methods that expose isolation-affecting settings
- docs and examples that present trust or safety assumptions
- tests for path validation, config handling, and privilege-sensitive flows

Secondary evidence sources:

- log messages tied to sandbox launch or host resource operations
- comments that describe intended trust assumptions
- helper wrappers around command execution, mounts, networking, or snapshots

## Execution Mode

Default mode is static review using code, config, docs, and tests.

Optional support mode:

- consume smoke or integration evidence from dynamic workflows
- consume future normalized reports about mount, namespace, or command surfaces

This reviewer should not require live sandbox execution for its first useful version.

## Analysis Phases

`<toolkit_root>` refers to the `conch-review-toolkit/` directory that contains this reviewer spec.

### Phase 1: Repository Discovery

Run repository discovery first:

```bash
python <toolkit_root>/scripts/discover_conch.py <target_repo>
```

Use the output to confirm the expected boundary-relevant surfaces exist:

- `cmd/`
- `internal/`
- `config/`
- `sdk/`
- `docs/`

### Phase 2: Entrypoint Collection

Run entrypoint collection:

```bash
python <toolkit_root>/scripts/collect_entrypoints.py <target_repo>
```

Use the `lifecycle`, `image_snapshot`, and `sdk` groups to prioritize trust-boundary review. Focus first on:

- launch and runtime-facing code
- image or path inputs crossing into privileged operations
- config or flag surfaces that can widen isolation

### Phase 3: Boundary Reconstruction

For each chosen path:

1. identify caller-controlled inputs
2. identify where those inputs cross into privileged or host-affecting code
3. identify mounts, host paths, commands, images, or shared-state reuse
4. identify defaults or flags that change isolation posture
5. identify whether the behavior is documented and observable

Separate findings by boundary class:

- input-validation
- host-resource
- runtime-launch
- cross-sandbox-sharing
- config-default
- docs-safety

### Phase 4: Triage Findings

Classify findings using the finding types in this spec.

When later smoke or runtime evidence exists, use it as supporting confirmation for practical impact, but do not require live execution to complete the first-pass review.

## Finding Types

| Finding Type | Description |
|---|---|
| `unguarded_isolation_widening` | A config value, flag, or code path can weaken isolation without clear gating |
| `host_resource_exposure` | Host paths, mounts, devices, or shared state appear exposed more broadly than intended |
| `privileged_operation_trust_gap` | Privileged actions rely on caller-controlled input without sufficient validation |
| `unsafe_default` | A default behavior weakens safety or isolation unexpectedly |
| `cross_sandbox_sharing_risk` | Reuse or sharing mechanisms appear insufficiently bounded or explained |
| `boundary_observability_gap` | Operators or callers lack a clear way to understand what trust boundary was crossed |
| `docs_safety_mismatch` | Documentation understates, omits, or contradicts an isolation-related behavior |
| `command_surface_risk` | External command, image, or path invocation surfaces appear broader than intended |

## Severity Rules

| Severity | When to use |
|---|---|
| `critical` | A flaw plausibly breaks sandbox or host isolation boundaries in a dangerous way |
| `high` | A flaw significantly weakens trust boundaries or exposes host resources unexpectedly |
| `medium` | Trust assumptions are too implicit, weakly validated, or inconsistently enforced |
| `low` | Safety posture is confusing, weakly documented, or insufficiently observable but not clearly broken |
| `info` | Notes on boundary hardening, threat modeling, or follow-up review ideas |

## Explicit Out Of Scope

This reviewer is not primarily responsible for:

- generic lifecycle correctness
  That belongs to `lifecycle-reviewer`.
- low-level race analysis
  That belongs to `concurrency-reviewer`.
- artifact relationship semantics
  That belongs to `image-snapshot-reviewer`.
- general docs drift not tied to safety or trust assumptions
  That belongs to `docs-implementation-auditor`.
- full runtime penetration or adversarial execution testing
  That belongs to future dynamic validation or dedicated security testing.

## Cross-Reviewer Boundaries

### With `lifecycle-reviewer`

This reviewer asks:

- does a lifecycle path cross trust boundaries safely?

The lifecycle reviewer asks:

- is the lifecycle contract itself coherent?

### With `docs-implementation-auditor`

This reviewer owns documentation mismatches specifically when they affect safety claims, trust assumptions, or dangerous defaults.

The docs auditor owns general documentation parity.

## Expected Output

The final review should include:

- a short summary of the most important trust boundaries
- findings grouped by boundary class
- explicit note on dangerous defaults
- explicit note on shared-resource reuse assumptions
- explicit note on operator visibility into isolation-affecting settings

## Output Contract

Each finding should include at least:

- `finding_type`
- `severity`
- `boundary_class`
- `component`
- `summary`
- `evidence`
- `user_impact`
- `suggested_followup`

Where:

- `boundary_class` is one of `input-validation`, `host-resource`, `runtime-launch`, `cross-sandbox-sharing`, `config-default`, or `docs-safety`
- `component` is a subsystem or surface such as `daemon`, `cli`, `sdk`, `config`, or `docs`
- `evidence` points to concrete files and code paths

## Script Wiring

Preferred scripts for this reviewer:

- `discover_conch.py`
- `collect_entrypoints.py`

Optional supporting evidence:

- `run_smoke.py` output when it exposes readiness or boundary-adjacent failures
- `normalize_findings.py` for command-level synthesis
