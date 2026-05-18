# ADR-0215: Handoff Demo Digest

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0214 added `python -m autarkic_systems.vertical_demo`, a first-run digest
that says what the accepted AS stack currently demonstrates. The end-of-month
handoff command still combines only project status and GitHub submission
status.

That means the handoff can prove the repository is green and submitted to the
fork, but it does not carry the reader-facing answer to "what does this work
demonstrate?" A final handoff should include that demonstration summary without
making the digest a separate validator.

## Decision

Extend `autarkic_systems.handoff` with the vertical demo digest:

- `build_handoff_status` accepts an injectable demo builder;
- handoff readiness requires project status, demo digest, and GitHub
  submission to be accepted;
- JSON output includes `vertical_demo_summary` and `vertical_demo`; and
- text output includes a `Vertical demo:` section before GitHub submission.

This keeps project status and the vertical demo as the validation/reporting
authorities. The handoff remains a composition layer only.

This does not change runtime behavior, claims, proof rules, project-status
schema, demo digest schema, source-status decisions, registry schemas,
trace/SVG rendering, scheduler, topology, timing, or command semantics.

## Success Criteria

- Red tests fail before implementation because handoff payload/text lacks the
  vertical demo digest.
- Handoff JSON includes the vertical demo summary text and structured digest.
- Handoff text renders the vertical demo section.
- Handoff readiness rejects when the demo digest rejects.
- Existing refresh-remotes behavior remains unchanged.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_handoff_status`.
- Green: the same focused suite passes after implementation.
- Regression: run adjacent handoff, vertical-demo, and GitHub-submission tests,
  `python -m autarkic_systems.handoff --refresh-remotes`,
  `python -m compileall -q autarkic_systems tests`, `git diff --check`, and
  the full default suite.

## After Action Report

Implemented in `autarkic_systems/handoff.py`, with focused coverage in
`tests/test_handoff_status.py` and operator notes in
`docs/vertical-demo-digest.md`.

The red focused run failed as intended because `build_handoff_status` and
`run_handoff_cli` did not accept an injectable vertical-demo builder, handoff
payloads lacked `vertical_demo_summary` and `vertical_demo`, and handoff text
lacked a `Vertical demo:` section.

The implementation imports the ADR-0214 demo builder and formatter, adds the
demo digest to `HandoffStatus`, includes text and JSON summaries, and marks
handoff readiness ready only when project status, vertical demo digest, and
GitHub submission are all accepted. Refresh-remotes behavior remains owned by
the existing GitHub-submission path.

Focused handoff tests passed 7 tests. Adjacent handoff, vertical-demo, and
GitHub-submission tests passed 19 tests. Live text and JSON handoff runs with
`--refresh-remotes` reported ready handoff state, accepted project status,
accepted vertical demo, accepted remote refresh, and submitted-to-fork GitHub
status. `compileall`, `git diff --check`, and the full default suite passed;
the full suite ran 907 tests.
