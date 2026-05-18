# ADR-0135: Transition Claim CLI

Date: 2026-05-18

## Status

Accepted.

## Context

The single-transition claim manifest is the proof/evidence base beneath the
transition proof certificates, evidence bundles, chain claims, chain evidence,
and project status report. Those downstream layers now have operator-facing
commands, but the transition claim manifest itself is still validated only
through tests and library calls.

That makes the base claim surface harder to inspect than the proof and evidence
surfaces that depend on it.

## Decision

Add a `python -m autarkic_systems.claim_manifest` command.

The command will accept:

- `--claims`, defaulting to `claims/transition_claims.json`; and
- `--format text|json`, defaulting to `text`.

Text output will list one line per evaluated claim example. JSON output will
include accepted state, claim count, example count, result count, matched count,
and per-example evaluation results. The command will return `0` only when every
claim example matches its manifest expectation.

## Success Criteria

- Red tests fail before implementation because the claim manifest module has no
  CLI helpers and module execution emits no transition-claim report.
- The checked-in transition claim manifest returns exit code `0` in text and
  JSON modes.
- A manifest with a deliberately flipped expectation returns exit code `1` and
  reports the failing claim example.
- Module execution through `python -m autarkic_systems.claim_manifest` works in
  text and JSON modes.
- Full repository tests remain green.

## Consequences

The base transition claim layer becomes directly inspectable, giving operators
a shorter path for answering whether current claim examples still match their
predicate implementations.

This CLI does not widen the claim language or add new runtime behavior.

## Test Plan

- Red: add direct-run and subprocess tests for text output, JSON output, and a
  failing flipped-expectation claim manifest.
- Green: add report construction, text/JSON formatting, CLI argument parsing,
  and `__main__` execution to `autarkic_systems.claim_manifest`.
- Regression: run focused claim-manifest tests, JSON formatting, `py_compile`,
  `git diff --check`, and the full default test suite before commit.

## After Action Report

Implemented in `autarkic_systems/claim_manifest.py` by adding a
`TransitionClaimProjectReport`, text and JSON report formatters, a
`run_transition_claim_cli` entrypoint, and module execution through
`python -m autarkic_systems.claim_manifest`.

The red focused run executed 11 tests and failed because the report builder,
CLI runner, and module execution output did not exist.

The checked-in command now validates 13 transition claims and 35 claim
examples. Text mode reports each per-example result, and JSON mode reports
`accepted: true`, `claim_count: 13`, `example_count: 35`,
`matched_count: 35`, and `result_count: 35`.

Verification passed: focused claim-manifest tests ran 11 tests; JSON
formatting, `py_compile`, and `git diff --check` passed; transition-claim text
and JSON CLI output were accepted; and `python -m unittest discover` passed 617
tests.
