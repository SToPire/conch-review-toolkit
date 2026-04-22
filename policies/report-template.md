# Report Template Policy

Every skill should shape its final answer around a stable report structure. The exact content varies by skill, but the section order and naming intent should stay consistent enough that users can quickly scan different review modes.

## Global Rules

- Start with the review mode and target.
- Prefer short section titles and short paragraphs.
- Keep findings evidence-backed; do not emit unsupported conclusions.
- Merge duplicate findings before reporting.
- When uncertainty remains, call it out explicitly instead of smoothing it over.
- When runtime checks were not executed, say so explicitly.

## Required Header

The report should begin by identifying:

- review mode
- target repository
- focus or scope, if any
- whether the result is static-only, runtime-assisted, or runtime-first

## Core Sections

Every skill report should contain these sections in this order, though some skills may compress them:

### 1. Summary

State the top-line conclusion in 2-5 sentences.

### 2. Repository Context

Summarize the repo shape or scope that was actually reviewed.

### 3. Findings

List the substantive findings. Each finding should include:

- a short title
- severity
- affected component or path
- why it matters
- evidence

### 4. Open Questions

List unresolved points, missing evidence, or reasons confidence is limited.

### 5. Next Action

End with the next concrete step:

- fix now
- run another skill
- gather runtime evidence
- narrow scope and re-run

## Skill-Specific Expectations

### `conch-review-health`

Add:

- per-dimension status
- top 3 priorities
- explicit hotspot ranking
- why each hotspot is ranked where it is
- recommended next skill

### `conch-review-deep-review`

Add:

- explicit focus definition
- participating reviewers
- evidence grouped by concern

### `conch-review-smoke`

Add:

- steps attempted
- pass/fail/skipped per step
- environment versus product diagnosis
- current smoke-runner limitations

## Finding Shape

When a skill emits multiple findings, prefer this pattern:

```text
<Finding Title> [severity]
Affected: <component/path>
Why it matters: <impact>
Evidence: <files, commands, or runtime observations>
```

## Evidence Rules

- Static findings should cite files or reviewer evidence.
- Runtime findings should cite executed commands or observed outcomes.
- Documentation findings should cite both the documented claim and the implementation surface.
