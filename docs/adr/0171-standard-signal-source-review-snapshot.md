# ADR-0171: Standard-Signal Source Review Snapshot

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0165 made the `standard-signal` command-token execution boundary explicit:
AS preserves direct self-mailbox `standard-signal` commands as unsupported and
preserves completed self-target command-buffer `standard-signal` commands at
the append boundary. ADR-0166 then moved the safe-next guidance to a source
evidence gate: review new `standard-signal` command-token source evidence
before any execution change.

ADR-0170 closed the remaining write-buffer evidence-bundle gap. The active
source-status frontier now names only `standard-signal`. If the evidence gate
has been reviewed and no current source replaces the preserved-unsupported
boundary, leaving the same review string as the active next slice creates a
false open task.

## Decision

Add a dated source-review snapshot for the `standard-signal` command-token
gate. The snapshot records the checked upstream repository heads, the PRC
local witness commit, the source-status inputs that already carry
`standard-signal` evidence, and the conclusion that no reviewed source replaces
the existing unsupported execution boundary.

Update the standard-signal, recipient non-init, and multi-command
source-status records so their safe-next strings move from the active review
request to a `no-` prefixed guard:

`no-standard-signal-command-token-execution-change-without-new-source-evidence`

This ADR does not change Universal Cell runtime behavior, claims, proof
certificates, traces, SVGs, evidence bundles, project-status schema `15`, or
source-status frontier schema `2`.

## Success Criteria

- Red tests fail before implementation because the source-review snapshot does
  not exist and the source-status records still advertise the review as an
  active safe-next slice.
- The source-review snapshot records current remote heads for AS, AFS, PRC,
  SJAS, Proflog, and LeanTAP.
- The PRC remote head remains equal to the source manifest's PRC reviewed
  remote head, so the primary command-token source has not changed since the
  existing source review.
- The snapshot records the checked standard-signal source-status inputs and
  concludes that no execution change is allowed.
- Project-status and source-status frontier reports keep
  `standard-signal` blocked but render no active safe-next slice.
- Runtime behavior remains unchanged.

## Test Plan

- Red:
  `python -m unittest tests.test_standard_signal_source_review_status tests.test_standard_signal_command_semantics_status tests.test_recipient_non_init_command_source_status tests.test_multi_command_recipient_input_policy_status tests.test_project_status_report tests.test_source_status_frontier_cli`
  fails before implementation.
- Green: the same focused suite passes after adding the source-review snapshot
  and updating source-status expectations.
- Regression: run JSON parsing for touched JSON files, project/source status
  JSON, `compileall`, `git diff --check`, and the full default suite before
  commit.

## After Action Report

ADR-0171 added `sources/standard_signal_source_review_status.json`, linked it
from `sources/standard_signal_command_semantics_status.json`, and moved the
recipient non-init, multi-command, and standard-signal safe-next strings to
`no-standard-signal-command-token-execution-change-without-new-source-evidence`.
The aggregate project/source-status frontier still reports `standard-signal`
as blocked, but the active safe-next slice now renders as `none`.

The red focused run was observed before implementation:

```sh
python -m unittest tests.test_standard_signal_source_review_status tests.test_standard_signal_command_semantics_status tests.test_recipient_non_init_command_source_status tests.test_multi_command_recipient_input_policy_status tests.test_project_status_report tests.test_source_status_frontier_cli
```

Result: 112 tests ran with 13 failures and 6 errors because the source-review
snapshot was absent, `latest_source_review` was missing, and the source-status
records still advertised the active source-review safe-next slice.

The live source-head checks were non-mutating:

- AS `main`: `1a2fc06b75f5d33aee6655956c2a56df07a7bfb0`;
- AFS `main`: `a61592eab02a93d480149ce3465af5e3271ca213`;
- PRC `master`: `7e82c73fac8f108faac801a5c65e2c2b92653ba5`;
- SJAS `master`: `f1c11af5f310d39f487c3b91ee1ca70f4ade8871`;
- Proflog `main`: `77af8481d9f41a439eb42e1d8268a5b39f7c5c33`;
- LeanTAP `master`: `c17864a911c0c3cbd727b43743fdcb19b43714b8`;
- local PRC witness: `7e82c73fac8f108faac801a5c65e2c2b92653ba5`.

Focused verification passed after implementation:

```sh
python -m unittest tests.test_standard_signal_source_review_status tests.test_standard_signal_command_semantics_status tests.test_recipient_non_init_command_source_status tests.test_multi_command_recipient_input_policy_status tests.test_recipient_command_consumption_source_status tests.test_write_buffer_command_semantics_status tests.test_project_status_report tests.test_source_status_frontier_cli
```

Result: 132 tests passed.

Machine-readable status checks accepted the closed review gate:

- `python -m autarkic_systems.project_status --format json` accepted schema
  `15`, transition evidence `11`, chain evidence `2`, 16 transition claims,
  40 transition examples, blocked commands `["standard-signal"]`, and empty
  aggregate `safe_next_slice`;
- `python -m autarkic_systems.source_status --format json` accepted schema
  `2`, blocked commands `["standard-signal"]`, and empty aggregate
  `safe_next_slice`;
- `python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json --format json`
  accepted 11 transition evidence bundles;
- `python -m autarkic_systems.chain_evidence_bundle --registry evidence/chains/manifest.json --format json`
  accepted 2 chain evidence bundles.

Regression verification also passed:

- JSON parsing for all checked `*.json` files;
- `python -m compileall -q autarkic_systems tests`;
- `git diff --check`;
- `python -m unittest discover` ran 769 tests successfully.

This ADR did not change Universal Cell runtime behavior, transition claims,
proof certificates, traces, SVGs, evidence bundles, or schema versions.
