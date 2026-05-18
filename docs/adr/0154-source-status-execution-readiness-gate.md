# ADR-0154: Source-Status Execution Readiness Gate

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0153 narrowed the write-buffer command-token frontier to two unresolved
execution semantics questions: `buffer-full-boundary` and
`post-append-clearing`.

Those questions are currently visible as resolution questions, but the
operator-facing source-status reports do not have a direct execution-readiness
field. A future implementation could therefore confuse "runtime surface
settled as unsupported" with "execution semantics are ready."

## Decision

Add an optional `execution_readiness` object to source-status records and carry
it through both project-status and source-status frontier reports.

For write-buffer, the object records:

- the execution decision is `blocked`;
- execution changes are not allowed yet;
- the live blockers are `buffer-full-boundary` and `post-append-clearing`; and
- the summary explicitly says write-buffer append execution must not be
  implemented until those questions are resolved.

The source-status schema rejects malformed readiness objects and rejects
readiness blockers that do not match current unresolved
`required_resolution_questions`.

## Consequences

The write-buffer frontier remains blocked, but the reason is now machine
visible as an execution gate rather than only prose.

Project-status JSON moves to schema 15, and focused source-status frontier JSON
moves to schema 2 because both reports expose the new readiness payload.

## Verification Plan

- Red: add project-status, source-status frontier, and source-status schema
  tests that expect `execution_readiness` in payload/text and reject malformed
  readiness metadata.
- Green: add readiness extraction, rendering, and schema validation; update
  the write-buffer source-status artifact.
- Regression: run focused tests, both status CLIs in JSON mode, `py_compile`,
  `git diff --check`, and the full unittest suite.

## After Action Report

Implemented in `autarkic_systems/project_status.py`,
`autarkic_systems/source_status.py`, and
`sources/write_buffer_command_semantics_status.json`.

The red focused run executed 80 project-status and source-status frontier
tests and failed because project-status still reported schema 14, the focused
source-status frontier still reported schema 1, execution-readiness text was
absent, and malformed readiness fixtures were accepted.

The green focused run passed 80 tests. Source-status JSON accepted schema 2
and reported write-buffer `execution_readiness.decision` as `blocked`, with
execution changes disallowed and blockers `buffer-full-boundary` plus
`post-append-clearing`. Project-status JSON accepted schema 15 with the same
readiness payload. `sources/write_buffer_command_semantics_status.json` parsed
as JSON. `py_compile`, `git diff --check`, and `python -m unittest discover`
passed; the full suite ran 666 tests.
