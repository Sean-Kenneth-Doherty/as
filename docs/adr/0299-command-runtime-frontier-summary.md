# ADR-0299: Command Runtime Frontier Summary

Date: 2026-05-21

## Status

Accepted.

## Context

ADR-0295 made the command-token source-status frontier expose a compact closure
summary. That report now says the safe-next queue is closed, `standard-signal`
remains the only blocked command token, `write-buf-zero` and `write-buf-one`
are implemented, and execution changes are not allowed without new source
evidence.

That status surface is useful, but it is still one step removed from the
runtime witness. A month-end handoff can see the source frontier, transition
claims, evidence bundles, and suite-selection boundaries, but it does not yet
have one small command that confirms the source-status closure against live
Universal Cell runtime cases.

## Decision

Add `autarkic_systems.command_runtime_frontier`, a focused text/JSON command
that combines the accepted source-status closure with live runtime witness
cases for the command-token frontier.

The command will run actual `universal_cell` transitions for:

- recipient `write-buf-zero` command-message append;
- recipient/stem `write-buf-one` command-message append;
- direct self-mailbox `write-buf-one` append;
- completed self-target `write-buf-one` command-buffer append;
- recipient `standard-signal` command-message rejection;
- direct self-mailbox `standard-signal` unsupported preservation; and
- completed self-target `standard-signal` command-buffer append boundary.

The JSON payload will expose:

- schema version;
- overall acceptance;
- source-status acceptance and closure summary;
- one runtime case per checked surface, with observed status and evidence
  bundle path where a bundle already exists; and
- empty runtime/evidence claims when the source-status frontier rejects.

The text output will render a concise `Command runtime frontier:` section for
operators.

Do not change Universal Cell runtime behavior, source-status JSON records,
source-status report semantics, transition predicates, evidence bundles,
formal-confidence files, project-status, vertical-demo, handoff behavior,
suite selection, claim manifests, or mathematical semantics.

## Success Criteria

- Red tests fail before implementation because the command module and payload
  do not exist.
- Default JSON accepts only when the checked-in source-status frontier accepts
  and all runtime cases match their expected statuses.
- Runtime cases confirm `write-buf-zero` and `write-buf-one` implemented
  surfaces through live `step_fixed_cell` / `step_stem_cell` calls.
- Runtime cases confirm `standard-signal` command-token surfaces remain
  rejected or preserved unsupported, not executed.
- Existing write-buffer evidence bundle paths are linked in the runtime cases.
- Rejected source-status input makes the report fail closed without claiming
  runtime implemented state.
- Text output names source closure, implemented commands, preserved unsupported
  commands, and each runtime case.

## Failure Criteria

- Any `standard-signal` command-token case is promoted to execution.
- Runtime cases are accepted when source-status closure rejects.
- The slice mutates source-status JSON or Universal Cell runtime behavior to
  force agreement.
- Formal-confidence, project-status, vertical-demo, handoff, or suite-selection
  semantics change.

## Test Plan

- Red:
  `python -m unittest tests.test_command_runtime_frontier`.
- Green:
  `python -m unittest tests.test_command_runtime_frontier`.
- Focused seam:
  `python -m unittest tests.test_command_runtime_frontier tests.test_source_status_frontier_cli tests.test_recipient_write_buffer_command_execution tests.test_write_buffer_command_execution tests.test_recipient_write_buffer_command_evidence_bundle tests.test_write_buffer_execution_evidence_bundle tests.test_standard_signal_command_semantics_status tests.test_write_buffer_command_semantics_status`.
- Live JSON assertion:
  `python -m autarkic_systems.command_runtime_frontier --format json`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Implemented.

The red run was:

```sh
python -m unittest tests.test_command_runtime_frontier
```

It failed as intended with:

```text
ModuleNotFoundError: No module named 'autarkic_systems.command_runtime_frontier'
```

The implementation adds only `autarkic_systems.command_runtime_frontier`. The
module reuses `build_source_status_frontier_report`; if that source-status
frontier rejects, ADR-0299 reports rejected status with no runtime/evidence
claims. If source status accepts, it runs seven live Universal Cell transition
cases and accepts only when the observed status matches the expected command
frontier boundary.

Focused verification passed:

```sh
python -m unittest tests.test_command_runtime_frontier
```

Observed result:

```text
Ran 7 tests in 1.114s
OK
```

The focused command/source-status/evidence seam passed:

```sh
python -m unittest tests.test_command_runtime_frontier tests.test_source_status_frontier_cli tests.test_recipient_write_buffer_command_execution tests.test_write_buffer_command_execution tests.test_recipient_write_buffer_command_evidence_bundle tests.test_write_buffer_execution_evidence_bundle tests.test_standard_signal_command_semantics_status tests.test_write_buffer_command_semantics_status
```

Observed result:

```text
Ran 74 tests in 2.708s
OK
```

The live JSON assertion:

```sh
python -m autarkic_systems.command_runtime_frontier --format json
```

returned `accepted=true`, source-status schema version 4, implemented commands
`write-buf-zero` and `write-buf-one`, preserved unsupported command
`standard-signal`, `execution_change_allowed=false`, and seven accepted
runtime cases.

The live suite index reflected the added test module:

```sh
python -m autarkic_systems.test_suite_selection --list-suites --format json
```

reported 152 discovered modules, with `fast=130`,
`extended-fixed-point=22`, and `all=152`.

Additional verification passed:

```sh
python -m compileall autarkic_systems tests
git diff --check
```

The fast suite passed:

```sh
python -m autarkic_systems.test_suite_selection --suite fast
```

Observed result:

```text
Ran 1188 tests in 300.178s
OK
manifest: as-test-suite-selection-v1 suite: fast module_count: 130
```

This is an additive runtime witness/reporting command only. It does not change
Universal Cell runtime behavior, source-status JSON records, source-status
report semantics, transition predicates, evidence bundles, formal-confidence
files, project-status, vertical-demo, handoff behavior, suite selection, claim
manifests, or mathematical semantics.
