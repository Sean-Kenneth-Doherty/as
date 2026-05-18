# ADR-0097: Project Status Registry Failures

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0096 added a project status command that reports accepted transition
evidence, accepted chain evidence, and the blocked command-token frontier. It
already turns missing source-status files into structured rejected output.

The same operator-facing rule should apply to registry files. If an agent runs
the status command with a bad transition or chain registry path, the command
should return a rejected status report that names the missing registry instead
of raising a traceback.

## Decision

Extend `autarkic_systems.project_status` so registry loading and validation
return structured summaries for missing or invalid registry files.

The report will keep the existing accepted output unchanged on the checked-in
path. For a missing registry path, it will:

- mark the corresponding registry summary rejected;
- preserve the requested registry path;
- include a failed subject for the missing registry file;
- keep the other registry and frontier summaries available when possible; and
- exit nonzero through the CLI.

## Success Criteria

- Red tests fail before implementation because missing registry paths raise
  `FileNotFoundError`.
- A missing transition registry path reports
  `transition_evidence.accepted: false`, `bundle_count: 0`, and
  `failed_subjects: ["registry-file"]`.
- A missing chain registry path reports `chain_evidence.accepted: false`,
  `bundle_count: 0`, and `failed_subjects: ["registry-file"]`.
- JSON CLI output for a missing registry exits `1` and names the missing path.
- Text output names missing registry files.
- The checked-in status command remains accepted.

## Consequences

The project status command becomes safer as a first diagnostic command. It can
now tell an operator which top-level registry is missing without hiding all
other status information behind an exception.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before
  missing registry handling exists.
- Green: focused project-status tests pass after implementation.
- Regression: run project-status CLI text/JSON, adjacent registry tests,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` failed in
four missing-registry cases with `FileNotFoundError`, confirming that status
report construction still crashed before emitting JSON or text.

`autarkic_systems.project_status` now wraps transition and chain registry
loading separately. A missing registry produces a rejected registry summary
with `failed_subjects: ["registry-file"]`, `bundle_count: 0`, the requested
path, and one failed result, while the other registry and frontier summaries
remain available when they can be read.

Verification:

- `python -m unittest tests.test_project_status_report` passed 9 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` passed 34 tests.
- `python -m autarkic_systems.project_status --transition-registry /tmp/missing-transition-registry.json --format json` exited `1` and reported `transition_evidence.failed_subjects: ["registry-file"]`.
- `python -m autarkic_systems.project_status --chain-registry /tmp/missing-chain-registry.json` exited `1` and printed `Missing registry files: /tmp/missing-chain-registry.json`.
- `python -m autarkic_systems.project_status --format json` remained accepted with transition `bundle_count: 8`, chain `bundle_count: 2`, and no missing source-status files.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 545 tests.
