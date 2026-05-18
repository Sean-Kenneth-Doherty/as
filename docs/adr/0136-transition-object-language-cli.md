# ADR-0136: Transition Object Language CLI

Date: 2026-05-18

## Status

Accepted.

## Context

The base transition claim manifest and proof-certificate manifest now have
direct operator commands. The transition-chain claim surface already has a CLI
that validates its chain language, examples, certificates, and surface together.

The single-transition object-language layer remains library/test-only even
though it defines the syntax-class boundary for the base transition claims and
proof certificates. That makes the language surface harder to inspect than the
claim and proof surfaces it constrains.

## Decision

Add a `python -m autarkic_systems.object_language` command.

The command will accept:

- `--language`, defaulting to `language/transition_claim_language.json`;
- `--claims`, defaulting to `claims/transition_claims.json`;
- `--certificates`, defaulting to `claims/proof_certificates.json`; and
- `--format text|json`, defaulting to `text`.

Text output will list all language-manifest and claim-surface validation
results. JSON output will expose accepted state, language ID, claim count,
certificate count, result count, and per-result validation details. The command
will return `0` only when every language and surface validation result is
accepted.

## Success Criteria

- Red tests fail before implementation because the object-language module has
  no CLI helpers and module execution emits no language report.
- The checked-in transition object-language surface returns exit code `0` in
  text and JSON modes.
- A malformed language manifest returns exit code `1` and reports the failing
  syntax-class or surface detail.
- Module execution through `python -m autarkic_systems.object_language` works
  in text and JSON modes.
- Full repository tests remain green.

## Consequences

The base object-language layer becomes a first-run validation surface instead
of only a unit-test concern. This helps diagnose whether failures belong to the
language manifest, transition claims, proof certificates, or richer downstream
evidence reports.

This CLI does not broaden the language or add runtime behavior.

## Test Plan

- Red: add direct-run and subprocess tests for text output, JSON output, and a
  failing language manifest.
- Green: add report construction, text/JSON formatting, CLI argument parsing,
  and `__main__` execution to `autarkic_systems.object_language`.
- Regression: run focused object-language tests, JSON formatting,
  `py_compile`, `git diff --check`, and the full default test suite before
  commit.

## After Action Report

Implemented in `autarkic_systems/object_language.py` with focused tests in
`tests/test_object_language.py`.

The red test run executed 14 object-language tests and failed because the
module had no project report, CLI runner, or `python -m` output. The green
implementation adds a `TransitionClaimLanguageProjectReport`, text and JSON
formatters, `--language` / `--claims` / `--certificates` overrides,
accepted/rejected exit codes, and module execution.

The checked-in language surface reports `accepted: true`,
`language_id: as-transition-claim-v1`, `claim_count: 13`,
`certificate_count: 13`, and `result_count: 63` in JSON mode. A manifest
missing the `formulae` syntax class returns exit code `1` and reports
`FAIL formulae: missing syntax class: formulae`.

Verification passed: focused object-language tests ran 14 tests;
`python -m autarkic_systems.object_language` text and JSON output were
accepted; JSON formatting, `py_compile`, and `git diff --check` passed; and
`python -m unittest discover` passed 624 tests.
