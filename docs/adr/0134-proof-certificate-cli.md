# ADR-0134: Proof Certificate CLI

Date: 2026-05-18

## Status

Accepted.

## Context

The transition proof-certificate verifier is currently usable from tests and
library calls, but not from a direct operator command. Neighbor-delivery chain
claims, evidence bundles, chain evidence bundles, demos, and project status all
have command-line validation surfaces. The transition proof-certificate layer
should have the same first-run affordance.

ADR-0133 made proof certificates slightly richer by adding
`predicate-result`. Without a CLI, that richer proof surface is still harder to
inspect than the downstream evidence and chain surfaces that depend on it.

## Decision

Add a `python -m autarkic_systems.proof_certificates` command.

The command will accept:

- `--claims`, defaulting to `claims/transition_claims.json`;
- `--certificates`, defaulting to `claims/proof_certificates.json`; and
- `--format text|json`, defaulting to `text`.

Text output will list one line per certificate verification result. JSON output
will expose accepted state, claim count, certificate count, result count, and
per-claim verification results. The command will return `0` only when every
certificate verification result is accepted.

## Success Criteria

- Red tests fail before implementation because the proof-certificate module has
  no CLI helpers and module execution emits no proof-certificate report.
- The checked-in transition proof-certificate surface returns exit code `0` in
  text and JSON modes.
- An incomplete certificate manifest returns exit code `1` and reports the
  failing proof-certificate detail.
- Module execution through `python -m autarkic_systems.proof_certificates`
  works in text and JSON modes.
- Full repository tests remain green.

## Consequences

The proof layer becomes an inspectable operator surface rather than an internal
library used only by tests and downstream evidence validators.

This CLI validates the current AS-local proof-certificate layer. It is not a
general proof checker, theorem prover, or SJAS consistency result.

## Test Plan

- Red: add subprocess and direct-run tests for text output, JSON output, and a
  failing incomplete certificate manifest.
- Green: add report construction, text/JSON formatting, CLI argument parsing,
  and `__main__` execution to `autarkic_systems.proof_certificates`.
- Regression: run focused proof-certificate tests, JSON formatting,
  `py_compile`, `git diff --check`, and the full default test suite before
  commit.

## After Action Report

Implemented in `autarkic_systems/proof_certificates.py` by adding a
`ProofCertificateProjectReport`, text and JSON report formatters, a
`run_proof_certificate_cli` entrypoint, and module execution through
`python -m autarkic_systems.proof_certificates`.

The red focused run executed 16 tests and failed because the report builder,
CLI runner, and module execution output did not exist.

The checked-in command now validates 13 transition claims and 13 proof
certificates. Text mode reports each per-claim certificate result, and JSON
mode reports `accepted: true`, `claim_count: 13`, `certificate_count: 13`, and
`result_count: 13`.

Verification passed: focused proof-certificate tests ran 16 tests; JSON
formatting, `py_compile`, and `git diff --check` passed; proof-certificate text
and JSON CLI output were accepted; and `python -m unittest discover` passed 610
tests.
