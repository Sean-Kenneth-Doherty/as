# ADR-0085: Chain Evidence CLI Target Selection

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0084 added `--registry` support to
`python -m autarkic_systems.chain_evidence_bundle` while preserving the
existing single-bundle default. The command can now validate either one chain
evidence bundle or a chain evidence registry.

That creates a small operator ambiguity: if both `--bundle` and `--registry`
are supplied, the command should not silently choose one target. Ambiguous
validation targets would make failure reports harder to trust, especially for
automation.

## Decision

Make `--bundle` and `--registry` mutually exclusive in
`run_chain_evidence_bundle_cli`.

The command will continue to default to the checked-in neighbor-delivery chain
bundle when neither flag is supplied. Supplying both target flags will fail at
argument parsing with exit code `2`.

## Success Criteria

- Red tests fail before implementation because both target flags are accepted.
- In-process CLI invocation raises `SystemExit(2)` when both flags are supplied.
- Module execution returns exit code `2` and argparse reports the mutually
  exclusive argument error.
- Existing single-bundle default, explicit `--bundle`, explicit `--registry`,
  and full repository tests remain green.

## Consequences

The chain evidence CLI now fails closed on ambiguous target selection while
preserving both supported validation modes.

## Test Plan

- Red: `python -m unittest tests.test_chain_evidence_cli_target_selection`
  fails before the parser target flags are mutually exclusive.
- Green: the same focused test passes after changing the parser.
- Regression: run the chain evidence bundle and registry tests, both CLI
  modes, `py_compile`, `git diff --check`, and the full default suite before
  commit.

## After Action Report

Implemented in `autarkic_systems/chain_evidence_bundle.py`, with focused
tests in `tests/test_chain_evidence_cli_target_selection.py`.

The focused red run failed because the parser accepted both target flags and
silently validated the registry. The green implementation puts `--bundle` and
`--registry` in an argparse mutually exclusive group while preserving the
default single-bundle validation path when neither flag is supplied.

Verification passed:

- focused red:
  `python -m unittest tests.test_chain_evidence_cli_target_selection` failed
  before target flags were mutually exclusive;
- focused green:
  `python -m unittest tests.test_chain_evidence_cli_target_selection` passed 2
  tests;
- adjacent chain CLI/registry/bundle tests passed 20 tests;
- `python -m autarkic_systems.chain_evidence_bundle --format json` still
  reported `accepted: true` and `result_count: 9`;
- `python -m autarkic_systems.chain_evidence_bundle --registry
  evidence/chains/manifest.json --format json` still reported `accepted: true`
  and `bundle_count: 1`;
- `py_compile` passed for the touched module and focused test;
- `git diff --check` passed; and
- `python -m unittest discover` passed 504 tests.
