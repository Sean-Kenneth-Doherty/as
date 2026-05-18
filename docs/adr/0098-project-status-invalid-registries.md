# ADR-0098: Project Status Invalid Registries

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0097 made missing transition and chain registry paths structured
project-status failures instead of tracebacks. The implementation catches any
registry loading error, but it currently collapses missing files and invalid
JSON or malformed registry content into the same `registry-file` subject.

That is enough to prevent a crash, but not precise enough for an operator. A
missing registry and an invalid registry file have different next actions.

## Decision

Refine `autarkic_systems.project_status` registry failure summaries so missing
registry paths and invalid registry contents are distinguishable.

Missing registry files will continue to report `registry-file`. Registry files
that exist but cannot be parsed or loaded as valid registries will report
`registry-json`.

The text report will name both missing and invalid registry file groups.

## Success Criteria

- Red tests fail before implementation because invalid registry JSON still
  reports `registry-file`.
- An invalid transition registry JSON file reports
  `transition_evidence.failed_subjects: ["registry-json"]`.
- An invalid chain registry JSON file reports
  `chain_evidence.failed_subjects: ["registry-json"]`.
- Text output names invalid registry files.
- The existing missing-registry behavior remains unchanged.
- The checked-in status command remains accepted.

## Consequences

The project status command becomes a more useful first diagnostic: an operator
can distinguish absent registry artifacts from present-but-malformed registry
artifacts without inspecting a Python traceback.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before
  invalid registry classification exists.
- Green: focused project-status tests pass after implementation.
- Regression: run project-status CLI text/JSON, adjacent registry tests,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` failed
because invalid transition and chain registry fixtures still reported
`failed_subjects: ["registry-file"]`, and text output listed a malformed
registry under missing registry files.

`autarkic_systems.project_status` now classifies `FileNotFoundError` registry
loads as `registry-file` and existing registry files with parse/schema/load
errors as `registry-json`. Text output includes separate missing and invalid
registry file lines.

Verification:

- `python -m unittest tests.test_project_status_report` passed 12 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` passed 37 tests.
- `python -m autarkic_systems.project_status --format json` remained accepted with transition `bundle_count: 8`, chain `bundle_count: 2`, and no missing or invalid source-status files.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 548 tests.
