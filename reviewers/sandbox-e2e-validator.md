# sandbox-e2e-validator

## Purpose

Run a minimal dynamic validation path against a real or launchable Conch environment.

The primary target is to separate:

- environment readiness failures
- daemon startup failures
- lifecycle execution failures
- cleanup residue after a minimal run

This reviewer is a dynamic validator, not a static code reviewer.

## Owned Surface

This reviewer owns execution-time validation across:

- `conchd` launch or connectivity
- minimal sandbox creation
- minimal command execution in a sandbox
- minimal delete and residue check
- environment dependency readiness relevant to that path

## Primary Questions

- Is the target environment ready enough to attempt a minimal run?
- Can the validator connect to or launch `conchd`?
- Can Conch create a sandbox successfully?
- Can it run a minimal command in that sandbox?
- Can it delete the sandbox cleanly?
- Is there obvious residue after teardown?
- If the run fails, does the evidence point to environment setup or product behavior?

## Minimum Validation Path

1. Verify prerequisites
2. Start or connect to `conchd`
3. Create a sandbox
4. Execute a minimal command
5. Delete the sandbox
6. Check for obvious residual state

## Evidence Sources

Primary evidence sources:

- structured smoke-run step results
- daemon startup output or connection failures
- command output from the sandbox
- residue checks after delete

Secondary evidence sources:

- config used for the run
- environment-probe results
- prior lifecycle or resource-review findings used for interpretation

## Execution Mode

This reviewer is dynamic by default.

It should support two modes:

- `probe-only`: inspect readiness and planned steps without changing runtime state
- `execute`: actually run the minimal smoke path

## Analysis Phases

`<toolkit_root>` refers to the `conch-review-toolkit/` directory that contains this reviewer spec.

### Phase 1: Repository Discovery

Run repository discovery first:

```bash
python <toolkit_root>/scripts/discover_conch.py <target_repo>
```

Use the output to confirm the expected local prerequisites are present:

- `bin/`
- `config/`
- `sdk/`

### Phase 2: Probe-Only Smoke

Run the smoke script in probe-only mode first:

```bash
python <toolkit_root>/scripts/run_smoke.py <target_repo> --mode probe-only
```

Use this run to separate:

- repository readiness problems
- missing local prerequisites
- missing runtime dependencies in `PATH`

If probe-only fails at readiness, stop and report an environment-readiness result before attempting execution mode.

### Phase 3: Execute Smoke

If probe-only is acceptable, run execute mode:

```bash
python <toolkit_root>/scripts/run_smoke.py <target_repo> --mode execute
```

Interpret the result by step:

- `daemon`
- `create`
- `exec`
- `delete`
- `residue`

Current v0.1 limitation:

- the smoke runner can probe readiness and attempt daemon launch
- concrete create/exec/delete support is still incomplete

The reviewer must report that limitation explicitly instead of overstating dynamic coverage.

### Phase 4: Triage Validation Results

Classify failures using the finding types in this spec.

Always distinguish:

- likely environment failures
- likely product failures
- inconclusive results caused by current smoke-runner limitations

## Finding Types

| Finding Type | Description |
|---|---|
| `environment_not_ready` | Required runtime dependencies or inputs are missing or unusable |
| `daemon_start_failure` | `conchd` could not be started or connected to |
| `sandbox_create_failure` | Sandbox creation failed in the smoke path |
| `sandbox_exec_failure` | A minimal command could not run successfully inside the sandbox |
| `sandbox_delete_failure` | Delete failed or did not complete cleanly |
| `post_delete_residue` | Residual state appears to remain after delete |
| `readiness_docs_gap` | The environment failure reveals a missing or misleading documented prerequisite |
| `smoke_flake_or_ambiguity` | The result is inconclusive or unstable and needs follow-up investigation |

## Severity Rules

| Severity | When to use |
|---|---|
| `critical` | The smoke path breaks in a way that leaves unsafe or unrecoverable runtime residue |
| `high` | The minimal runnable workflow fails reproducibly in a user-visible way |
| `medium` | The run is blocked by recoverable environment issues or ambiguous runtime behavior |
| `low` | The smoke path mostly works but reveals cleanup or usability rough edges |
| `info` | Probe-only observations, environment notes, or follow-up suggestions |

## Explicit Out Of Scope

This reviewer is not primarily responsible for:

- proving lifecycle soundness from static code alone
  That belongs to `lifecycle-reviewer`.
- proving every resource leak root cause from code inspection
  That belongs to `resource-leak-reviewer`.
- broad documentation parity outside readiness and smoke prerequisites
  That belongs to `docs-implementation-auditor`.
- exhaustive load, stress, or race testing
  That belongs to future dynamic test tooling.

## Cross-Reviewer Boundaries

### With `lifecycle-reviewer`

This reviewer asks:

- does the minimal lifecycle actually work in a real run?

The lifecycle reviewer asks:

- does the code imply a sound lifecycle contract?

### With `docs-implementation-auditor`

This reviewer can surface environment-readiness documentation gaps discovered during execution.

The docs auditor owns the broader documentation fix set.

## Expected Output

The final validation should include:

- readiness summary
- per-step status for connect or launch, create, exec, delete, and residue checks
- clear separation between environment issues and likely product issues
- explicit note on whether the run was probe-only or execute mode

## Output Contract

Each result or finding should include at least:

- `finding_type`
- `severity`
- `step`
- `mode`
- `summary`
- `evidence`
- `user_impact`
- `suggested_followup`

Where:

- `step` is one of `readiness`, `daemon`, `create`, `exec`, `delete`, or `residue`
- `mode` is either `probe-only` or `execute`
- `evidence` includes relevant stdout, stderr, return code, or observed residue data

## Script Wiring

Primary script for this reviewer:

- `run_smoke.py`

Supporting script:

- `discover_conch.py`

Optional supporting evidence:

- `normalize_findings.py` for command-level synthesis
