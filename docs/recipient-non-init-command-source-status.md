# Recipient Non-Init Command Source Status

Status: source-status decision, updated 2026-05-18.

ADR-0053 records why recipient-side non-init command-message inputs remain
blocked after the init-family recipient ladder was implemented, claimed,
traced, and rendered.

The structured status lives in
`sources/recipient_non_init_command_source_status.json`.
ADR-0117 adds a top-level `as_boundary` to that artifact so project status can
report the recipient non-init rejection boundary directly instead of exposing
only the nested standard-signal, write-buffer, and multi-command subdecision
boundaries.

## Decision

Do not implement recipient-side non-init command-message execution yet.

Delivered recipient `standard-signal` command messages remain rejected by the
ADR-0054 non-init rejection boundary. ADR-0148 resolves the recipient surface,
ADR-0150 resolves the command-token/binary-input distinction, ADR-0151
resolves self-target `standard-signal` as unsupported preservation, and
ADR-0165 makes execution changes require new source evidence.

Delivered recipient `write-buf-zero` and `write-buf-one` command messages
remain rejected by the current ADR-0054 non-init rejection boundary, but
ADR-0168 resolves their source semantics as append execution. ADR-0161 now
implements direct self-mailbox and completed self-target command-buffer
write-buffer append execution; the remaining work is to replace this current
recipient runtime boundary with the source-ready recipient append behavior.

Multiple simultaneous command-message inputs also remain blocked because AS has
selected reject-and-clear as the conflict policy, not priority or sequencing.

## Safe Next Slice

The current runtime already rejects `standard-signal`, write-buffer, and
multi-command recipient inputs. ADR-0053 identified claim promotion as the
safe next slice because the rejection boundary needed to become explicit
before trace/render work could depend on it.

ADR-0054 completes that promotion as
`UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED`. ADR-0055 adds the
schematic-linked rejection trace in
`schematics/recipient_non_init_command_rejection_trace.json`. ADR-0056 adds
the rendered SVG view in
`schematics/recipient_non_init_command_rejection_trace.svg`.

The rejection evidence ladder is now complete. ADR-0057 records the
write-buffer command semantics source-status decision in
`sources/write_buffer_command_semantics_status.json`. ADR-0161 implements the
direct self-mailbox and completed self-target command-buffer write-buffer
surfaces; this recipient non-init source status keeps only delivered recipient
write-buffer command-message inputs rejected.

ADR-0058 records the matching `standard-signal` command-token semantics
source-status decision in
`sources/standard_signal_command_semantics_status.json`. ADR-0165 and
ADR-0166 now make the settled boundary explicit: standard-signal command-token
execution is preserved as unsupported, and future changes require new source
evidence rather than another generic revisit of old blockers.

ADR-0059 records the multi-command recipient input policy in
`sources/multi_command_recipient_input_policy_status.json`: reject and clear
active command input. It also adds an all-init conflict example to the
recipient non-init rejection claim.

ADR-0060 adds the corresponding schematic-linked trace in
`schematics/multi_command_recipient_rejection_trace.json`.

ADR-0061 adds the corresponding rendered SVG view in
`schematics/multi_command_recipient_rejection_trace.svg`.

ADR-0068 records the single-token upstream `standard-signal` rejection as an
integrated evidence bundle in
`evidence/recipient_non_init_command_rejection_bundle.json`, tying the claim,
proof certificate, schematic trace, SVG render, hardware witness map, and
source-status boundaries together.

ADR-0163 keeps that same trace-aligned primary example but extends the
recipient non-init claim, proof certificate, and evidence-bundle coverage with
explicit upstream `write-buf-zero` and `write-buf-one` rejection examples.

ADR-0148 reuses this completed rejection evidence ladder to resolve the
standard-signal `recipient-surface` question: delivered recipient
`standard-signal` command messages are rejected as non-init command-message
inputs rather than executed.

ADR-0152 reuses the same rejection evidence ladder to resolve the write-buffer
`recipient-surface` question: delivered recipient `write-buf-zero` and
`write-buf-one` command messages are rejected as non-init command-message
inputs rather than executed.

The rejection evidence ladder is complete again. ADR-0168 resolves recipient
write-buffer command-message source semantics as append execution, so the
active safe next slice is recipient write-buffer command-message runtime
implementation. Standard-signal command-token execution should be changed only
if later source evidence replaces the ADR-0165 preserved unsupported boundary.

ADR-0117 keeps this boundary visible to project-status automation: accepted
source-status records must now carry non-empty top-level `as_boundary` text.

## Verification

Run:

```sh
python -m unittest tests.test_recipient_non_init_command_source_status
```

The tests check the blocking decision, implemented
claim/trace/SVG/evidence-bundle/source-status surfaces, standard-signal
preserved-unsupported gating, write-buffer source divergences, multi-command
policy boundary, and the updated source-status frontier.
