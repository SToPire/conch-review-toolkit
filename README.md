# Conch Review Toolkit

Review toolkit scaffold for the `Conch` project.

- `https://atomgit.com/openeuler/Conch`

It currently centers on three installable skills:

- `conch-review-health`: broad health snapshot, top priorities, and hotspot ranking
- `conch-review-deep-review`: focused evidence-heavy review for one subsystem, path, or failure class
- `conch-review-smoke`: minimal runtime validation and environment-versus-product diagnosis

## How To Use This Toolkit

The toolkit is consumed as a set of local skills. A typical setup is:

1. clone this repository locally
2. install it into the agent-specific directory inside your local `Conch` checkout
3. invoke the installed skills inside `Conch`

### 1. Clone the repository

```bash
git clone https://github.com/openeuler-mirror/conch-review-toolkit.git
cd conch-review-toolkit
```

If you are working from a different remote or fork, replace the clone URL accordingly.

### 2. Install into Your Agent Directory

Assume your local `Conch` repository is at `/path/to/Conch` and this toolkit is at `/path/to/conch-review-toolkit`.

#### Codex

For Codex, use the installer script in the repository root:

```bash
python3 install_codex_toolkit.py /path/to/Conch/.codex
```

This installs:

- toolkit root symlink at `/path/to/Conch/.codex/conch-review-toolkit`
- generated skill wrappers under `/path/to/Conch/.codex/skills/`
- generated reviewer subagents under `/path/to/Conch/.codex/agents/`

Useful options:

```bash
python3 install_codex_toolkit.py /path/to/Conch/.codex --dry-run
python3 install_codex_toolkit.py /path/to/Conch/.codex --force
python3 install_codex_toolkit.py /path/to/Conch/.codex --copy-toolkit
```

#### OpenCode

```bash
mkdir -p /path/to/Conch/.opencode/skills
ln -s /path/to/conch-review-toolkit/skills/conch-review-health /path/to/Conch/.opencode/skills/conch-review-health
ln -s /path/to/conch-review-toolkit/skills/conch-review-deep-review /path/to/Conch/.opencode/skills/conch-review-deep-review
ln -s /path/to/conch-review-toolkit/skills/conch-review-smoke /path/to/Conch/.opencode/skills/conch-review-smoke
```

#### Claude Code

```bash
mkdir -p /path/to/Conch/.claude/skills
ln -s /path/to/conch-review-toolkit/skills/conch-review-health /path/to/Conch/.claude/skills/conch-review-health
ln -s /path/to/conch-review-toolkit/skills/conch-review-deep-review /path/to/Conch/.claude/skills/conch-review-deep-review
ln -s /path/to/conch-review-toolkit/skills/conch-review-smoke /path/to/Conch/.claude/skills/conch-review-smoke
```

### 3. Use the skills inside `Conch`

Open the `Conch` repository with your agent and invoke the installed skills by name:

- `conch-review-health`
- `conch-review-deep-review`
- `conch-review-smoke`

These skills share the common assets in this toolkit repository, so keep the symlinks pointing to the cloned checkout.

The shared assets behind those skills are:

- `reviewers/`: reusable reviewer specs and subagent guides
- `scripts/`: shared discovery, normalization, and smoke-runner logic
- `policies/`: common severity and report-shape rules

## Reviewers

The first reviewer set is:

- `lifecycle-reviewer`
- `image-snapshot-reviewer`
- `resource-leak-reviewer`
- `concurrency-reviewer`
- `api-sdk-parity-reviewer`
- `security-boundary-reviewer`
- `docs-implementation-auditor`
- `sandbox-e2e-validator`

## Scripts

The first script set is:

- `discover_conch.py`
- `collect_entrypoints.py`
- `normalize_findings.py`
- `run_smoke.py`

## Acknowledgement

This toolkit was heavily inspired by `cext-review-toolkit`:

- `https://github.com/devdanzin/cext-review-toolkit`
