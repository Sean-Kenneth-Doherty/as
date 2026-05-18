# ADR-0166: Standard-Signal Safe-Next Boundary

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0165 made the standard-signal execution-readiness boundary explicit:
`standard-signal` command-token execution is preserved as unsupported, and
execution changes require new source evidence.

Some older source-status safe-next strings still say to revisit
`standard-signal` or write-buffer command semantics as though both remained
ordinary open blockers. That wording is now misleading. The remaining active
recipient command-message frontier is write-buffer-specific; standard-signal
work should be framed as review of new source evidence before changing the
settled unsupported boundary.

## Decision

Replace the stale combined safe-next language with two narrower directions:

- `standard-signal` source-status records should say to review new
  standard-signal command-token source evidence before any execution change;
- recipient non-init and multi-command status records should move their
  safe-next pointer to recipient write-buffer command-message semantics.

This ADR changes only source-status and documentation wording. It does not
change Universal Cell runtime behavior, claims, proof certificates, traces,
SVGs, evidence bundles, or schema versions.

## Success Criteria

- Red tests fail before implementation because the old combined
  `revisit-standard-signal-or-write-buffer-command-semantics` safe-next string
  is still present.
- Standard-signal source status exposes a new evidence-gated safe-next string.
- Recipient non-init and multi-command status records point to the recipient
  write-buffer command-message frontier.
- Project-status and source-status frontier reports render the narrowed
  safe-next queue.
- Runtime behavior remains unchanged.

## Test Plan

- Red:
  `python -m unittest tests.test_standard_signal_command_semantics_status tests.test_recipient_non_init_command_source_status tests.test_multi_command_recipient_input_policy_status tests.test_write_buffer_command_semantics_status tests.test_project_status_report tests.test_source_status_frontier_cli`
  fails before source-status updates.
- Green: the same focused suite passes after updating source-status records
  and expected text/JSON surfaces.
- Regression: run JSON parsing for touched files, project/source status JSON,
  `compileall`, `git diff --check`, and the full default suite before commit.

## After Action Report

ADR-0166 replaced the stale combined
`revisit-standard-signal-or-write-buffer-command-semantics` safe-next wording
with two narrower directions. Standard-signal now points to
`review-new-standard-signal-command-token-source-evidence-before-execution-change`;
recipient non-init and multi-command status records now point to
`revisit-recipient-write-buffer-command-message-semantics`.

The red focused run was observed before implementation:

```sh
python -m unittest tests.test_standard_signal_command_semantics_status tests.test_recipient_non_init_command_source_status tests.test_multi_command_recipient_input_policy_status tests.test_write_buffer_command_semantics_status tests.test_project_status_report tests.test_source_status_frontier_cli
```

Result: 120 tests ran with 12 failures because the old safe-next wording and
old standard-signal nested recipient status were still present.

Focused verification passed after implementation:

```sh
python -m unittest tests.test_standard_signal_command_semantics_status tests.test_recipient_non_init_command_source_status tests.test_multi_command_recipient_input_policy_status tests.test_write_buffer_command_semantics_status tests.test_project_status_report tests.test_source_status_frontier_cli
```

Result: 120 tests passed.

Machine-readable status checks accepted the narrowed safe-next queue:

- `python -m autarkic_systems.project_status --format json` accepted schema
  `15` and reported safe next
  `revisit-recipient-write-buffer-command-message-semantics,
  review-new-standard-signal-command-token-source-evidence-before-execution-change`;
- `python -m autarkic_systems.source_status --format json` accepted schema
  `2` and reported the same safe-next queue.

Regression verification also passed:

- `jq empty` over the four touched source-status JSON files;
- `python -m compileall -q autarkic_systems tests`;
- `git diff --check`;
- `python -m unittest discover` ran 732 tests successfully.

This ADR did not change Universal Cell runtime behavior, transition claims,
proof certificates, traces, SVGs, evidence bundles, or schema versions.
