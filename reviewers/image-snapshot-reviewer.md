# image-snapshot-reviewer

## Purpose

Audit the artifact and metadata chain for Conch image, rootfs, kernel, and snapshot workflows.

The primary target is the semantic contract between build-side outputs and unpack-side consumption, not low-level storage implementation details.

This reviewer should answer whether Conch's artifact pipeline is coherent, traceable, and recoverable when partially failing.

## Owned Surface

This reviewer owns artifact semantics across:

- build-related CLI flows in `cmd/`
- image and snapshot orchestration in `internal/`
- API types and request shapes related to artifact operations in `api/`
- config defaults or options that affect build, unpack, and snapshot behavior
- user-facing artifact workflow docs in `README.md` and `docs/`

## Primary Questions

- What are the concrete artifact types Conch creates and consumes?
- Are artifact relationships explicit and complete?
- Do build and unpack agree on artifact semantics?
- Are labels and metadata written consistently?
- Do failed operations leave half-built artifact state behind?
- Are artifact naming, tagging, and association rules stable across layers?
- Can a caller infer which artifact is authoritative for a given stage?

## Pipeline Model To Audit

At minimum, the reviewer should reconstruct this conceptual chain where applicable:

1. build input accepted
2. rootfs artifact produced
3. kernel artifact associated or selected
4. snapshot artifact produced
5. OCI index or equivalent aggregate object assembled
6. unpack resolves the aggregate object
7. unpack writes labels or metadata linking runtime state back to artifacts

The exact internal terminology may differ. The reviewer should map implementation details back to this model.

## Evidence Sources

Primary evidence sources:

- `cmd/` entrypoints for build and unpack
- `internal/` modules that create, name, resolve, or write artifact metadata
- config files and config parsing affecting image or snapshot behavior
- `api/` contracts for artifact-related operations
- `README.md` and `docs/` examples describing build, SNAP, and unpack behavior
- tests that assert artifact linkage, naming, or label writeback

Secondary evidence sources:

- sample command output in docs
- logs that mention artifact names, labels, or association decisions
- comments that describe intended build or unpack contracts

## Execution Mode

Default mode is static review using code, config, docs, and tests.

Optional support mode:

- consume smoke or integration results from future dynamic workflows
- consume normalized artifact metadata dumps from future scripts

This reviewer should produce useful findings without requiring a runnable environment.

## Analysis Phases

`<toolkit_root>` refers to the `conch-review-toolkit/` directory that contains this reviewer spec.

### Phase 1: Repository Discovery

Run repository discovery first:

```bash
python <toolkit_root>/scripts/discover_conch.py <target_repo>
```

Confirm that the target exposes the expected image and snapshot surfaces:

- `cmd/`
- `internal/`
- `config/`
- `docs/`

### Phase 2: Artifact Entrypoint Collection

Run entrypoint collection:

```bash
python <toolkit_root>/scripts/collect_entrypoints.py <target_repo>
```

Use the `image_snapshot` entrypoint group to identify the first-pass review set for:

- build
- rootfs
- kernel
- snapshot
- unpack

### Phase 3: Artifact Pipeline Reconstruction

Read the candidate code and docs to reconstruct:

1. which artifacts are created
2. how they are named or tagged
3. how they are associated with one another
4. how unpack resolves and writes metadata
5. what cleanup occurs on failure

Focus first on the most canonical path, then branch into edge cases and cleanup paths.

### Phase 4: Triage Findings

Group findings by artifact phase and classify them using the finding types in this spec.

If later workflows produce runtime artifact evidence, use that as supporting confirmation rather than as a requirement for first-pass review.

## Finding Types

| Finding Type | Description |
|---|---|
| `artifact_linkage_gap` | The code does not preserve a clear relationship between artifacts that should be associated |
| `build_unpack_contract_mismatch` | Build-side semantics and unpack-side expectations disagree |
| `metadata_writeback_incomplete` | Labels or metadata needed to reconnect runtime state to artifacts are missing or incomplete |
| `ambiguous_artifact_authority` | It is unclear which artifact or manifest should be treated as canonical at a given stage |
| `tagging_or_naming_inconsistency` | Artifact names or tags vary across CLI, daemon, docs, or config in a way that can break usage |
| `partial_artifact_cleanup_gap` | Failed build or unpack flows can leave half-complete artifact state behind |
| `cross_layer_artifact_mismatch` | Docs, CLI, API, and implementation describe different artifact relationships |
| `snapshot_dependency_implicit` | A required relationship among rootfs, kernel, and snapshot artifacts is relied upon but not made explicit |

## Severity Rules

| Severity | When to use |
|---|---|
| `critical` | Artifact-chain corruption or ambiguity can cause the wrong runtime state to be used or make cleanup and recovery unsafe |
| `high` | Build, unpack, or metadata linkage flaws are likely to break real workflows or leave orphaned artifact state |
| `medium` | Semantics are inconsistent, implicit, or weakly enforced but not clearly destructive on the common path |
| `low` | Naming, documentation, or observability issues make artifact behavior confusing but likely still usable |
| `info` | Notes on artifact design tradeoffs or follow-up verification ideas |

## Explicit Out Of Scope

This reviewer is not primarily responsible for:

- sandbox lifecycle semantics outside artifact-related phases
  Those belong to `lifecycle-reviewer`.
- verifying every concrete resource release path
  Those belong to `resource-leak-reviewer`.
- proving concurrent access correctness
  Those belong to `concurrency-reviewer`.
- general docs parity outside image and snapshot workflows
  That belongs to `docs-implementation-auditor`.
- running a real build and unpack environment from scratch
  That belongs to dynamic validation workflows and future scripts.

## Cross-Reviewer Boundaries

### With `lifecycle-reviewer`

This reviewer asks:

- is the artifact pipeline semantically coherent?

The lifecycle reviewer asks:

- does the sandbox lifecycle enforce the right state transitions?

### With `docs-implementation-auditor`

This reviewer owns artifact-related documentation mismatches specifically when they affect artifact semantics.

The docs auditor owns broader documentation drift.

## Expected Output

The final review should include:

- a short reconstructed artifact pipeline
- explicit note on rootfs, kernel, snapshot, and aggregate artifact relationships
- findings grouped by build, aggregate, unpack, and metadata phases
- explicit note on failure-path cleanup expectations
- explicit note on canonical artifact identity and authority

## Output Contract

Each finding should include at least:

- `finding_type`
- `severity`
- `component`
- `artifact_phase`
- `summary`
- `evidence`
- `user_impact`
- `suggested_followup`

Where:

- `component` is a subsystem or surface such as `cli`, `daemon`, `api`, `config`, or `docs`
- `artifact_phase` is one of `build`, `aggregate`, `snapshot`, `unpack`, `metadata`, or `cleanup`
- `evidence` points to concrete files and code paths

## Script Wiring

Preferred scripts for this reviewer:

- `discover_conch.py`
- `collect_entrypoints.py`

Optional supporting evidence:

- `normalize_findings.py` for command-level synthesis
