# ADR-0214: Vertical Demo Digest

Date: 2026-05-18

## Status

Accepted.

## Context

The repository now has accepted transition evidence, transition-chain
evidence, network-sequence evidence, claim/proof validation, object-language
validation, and source-status frontier reporting. Those pieces are useful, but
the first-run story remains scattered across specialized commands.

A reader can run `project_status` to see that the stack is accepted, and can
run focused demo commands for network-sequence evidence, but there is no small
top-level demonstration command that says what AS currently demonstrates,
which checked layers support it, and which command-token boundary remains
closed.

## Decision

Add a top-level vertical demo digest command that delegates acceptance to the
existing project-status report and formats the current cross-layer
demonstration in one place.

The digest will report:

- project acceptance;
- the current demonstration name;
- transition, chain, and network-sequence evidence counts;
- claim/proof counts and proof-rule mix;
- the blocked command-token frontier;
- the canonical registry and source-status artifact paths; and
- the sequence evidence bundle that ties the currently checked end-to-end path
  together.

This does not change runtime behavior, claims, proof rules, validation
authority, source-status decisions, registry schemas, project-status schema,
trace/SVG rendering, scheduler, topology, timing, or command semantics.

## Success Criteria

- Red tests fail before implementation because the vertical demo module is
  absent.
- Text output names the current demonstration, evidence counts, proof-rule
  mix, blocked command frontier, and canonical artifact paths.
- JSON output exposes the same digest in structured form and reports accepted
  status from project status.
- Module execution works through `python -m autarkic_systems.vertical_demo`.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_vertical_demo_digest`.
- Green: the same focused suite passes after implementation.
- Regression: run adjacent project-status and network-sequence demo tests,
  `python -m compileall -q autarkic_systems tests`, `git diff --check`, and
  the full default suite.

## After Action Report

Implemented in `autarkic_systems/vertical_demo.py`, with focused coverage in
`tests/test_vertical_demo_digest.py` and operator notes in
`docs/vertical-demo-digest.md`.

The red focused run failed as intended because
`autarkic_systems.vertical_demo` did not exist. The green implementation adds a
thin first-run digest over `build_project_status_report`, so acceptance remains
delegated to the existing project-status validator.

The text report now names the current post-handoff signal routing
demonstration, transition/chain/sequence evidence counts, claim/proof counts,
proof-rule mix, blocked `standard-signal` command frontier, canonical
registries, and the checked network-sequence evidence bundle. JSON output
carries the same digest, and module execution works through
`python -m autarkic_systems.vertical_demo`.

Focused vertical-demo tests passed 4 tests. Adjacent vertical-demo,
project-status, and network-sequence demo tests passed 103 tests. Live text and
JSON demo commands reported accepted status, 11 transition bundles, 2 chain
bundles, 1 sequence bundle, 52 `predicate-result` proof steps, and the
remaining `standard-signal` frontier. `compileall`, `git diff --check`, and
the full default suite passed; the full suite ran 906 tests.
