# Recipient Command Consumption Source Status

Status: source-status decision, 2026-05-18.

ADR-0048 records the source boundary for recipient-side command-message inputs
after ADR-0044 through ADR-0047 made neighbor-target command-buffer delivery
executable, claimed, traced, and rendered. ADR-0076 later registers that
delivery path as an integrated evidence bundle while keeping recipient
consumption as a separate source-status decision. ADR-0077 then adds a
two-step helper that composes that delivery tuple into recipient upstream state
for the init-family case only.

The structured status lives in
`sources/recipient_command_consumption_source_status.json`.

## Decision

ADR-0048 decided to implement recipient-side init-family command-message
consumption first, but not full command-message consumption. ADR-0169 extends
the implemented recipient-consumption surface to single `write-buf-zero` and
`write-buf-one` command messages.

The formal model routes input-channel special messages for wire, proc, and
stem cells through `process-special-message`. The restored PRC legacy sources
agree on a seven-message special-message set:

- `stem-init`;
- `wire-r-init`;
- `wire-l-init`;
- `proc-r-init`;
- `proc-l-init`;
- `write-buf-zero`;
- `write-buf-one`.

AS already implements init-family behavior in the self-mailbox path and in
self-target init command-buffer dispatch. ADR-0049 reuses that stable
init-family subset for recipient-side command-message inputs and records the
runtime slice in `docs/recipient-init-command-message-consumption.md`.

## Remaining Blockers

Delivered recipient `standard-signal` command messages remain rejected by the
ADR-0054 non-init rejection boundary, and self-target `standard-signal`
command tokens remain preserved as unsupported. ADR-0165 gates any future
execution change on new source evidence.

Delivered recipient `write-buf-zero` and `write-buf-one` command messages are
implemented by ADR-0169 as append execution. ADR-0161 selects and implements
direct self-mailbox and completed self-target command-buffer write-buffer
append behavior; ADR-0169 completes the single recipient command-message
write-buffer surface.

Full recipient-side command-message consumption still excludes non-init
command-token execution. ADR-0059 selects reject-and-clear as the policy for
multiple simultaneous command-message inputs.

## Implemented Slice

ADR-0049 implements single input-channel consumption for:

- `stem-init`;
- `wire-r-init`;
- `wire-l-init`;
- `proc-r-init`;
- `proc-l-init`.

The transition status is `recipient-init-command-message-processed`. The
source-status artifact records this in its `implemented_slices` field while
keeping non-init command-message inputs blocked.

ADR-0050 promotes this slice into the named transition claim
`UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED`, checked by
`recipient_init_command_message_processed`.

ADR-0051 records the same slice as a schematic-linked trace in
`schematics/recipient_init_command_message_trace.json`.

ADR-0052 adds the rendered SVG view in
`schematics/recipient_init_command_message_trace.svg`.

ADR-0053 records the remaining non-init command-message blockers in
`sources/recipient_non_init_command_source_status.json` and selects a named
rejection-boundary claim as the next safe slice.

ADR-0054 promotes that rejection boundary into the named claim
`UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED`.

ADR-0055 records one fixed-recipient upstream `standard-signal` rejection as a
schematic-linked trace in
`schematics/recipient_non_init_command_rejection_trace.json`.

ADR-0056 adds the rendered SVG view in
`schematics/recipient_non_init_command_rejection_trace.svg`.

ADR-0057 records the write-buffer command semantics source-status decision in
`sources/write_buffer_command_semantics_status.json`. ADR-0161 implements the
direct self-mailbox and completed self-target command-buffer write-buffer
surfaces, ADR-0168 marks delivered recipient write-buffer command messages
source-ready for append execution, and ADR-0169 implements that recipient
append execution. ADR-0170 promotes that recipient write-buffer
command-message surface into the transition evidence registry.

ADR-0058 records the `standard-signal` command-token semantics source-status
decision in `sources/standard_signal_command_semantics_status.json` while
preserving ordinary binary-input standard-signal behavior. ADR-0165 and
ADR-0166 record that command-token execution is not the active safe next
implementation lane unless new source evidence replaces the unsupported
boundary. ADR-0171 reviews the current source heads, finds no replacing
standard-signal command-token evidence, and removes the previous active review
slice from this recipient consumption status.

ADR-0059 records the multi-command recipient input policy in
`sources/multi_command_recipient_input_policy_status.json`, selecting
reject-and-clear instead of priority or sequencing.

ADR-0060 records that selected policy as a schematic-linked trace in
`schematics/multi_command_recipient_rejection_trace.json`.

ADR-0061 records the rendered SVG view of that selected policy in
`schematics/multi_command_recipient_rejection_trace.svg`.

ADR-0065 records the positive recipient init command-message transition as an
integrated evidence bundle in
`evidence/recipient_init_command_message_bundle.json`, tying the executable
example to its claim, proof certificate, schematic trace, SVG render, hardware
witness map, and source-status boundaries.

## Verification

Run:

```sh
python -m unittest tests.test_recipient_command_consumption_source_status
```

The tests check the source-status decision, the formal input-special-message
anchor, the legacy special-message sets, the implemented ADR-0049 slice,
the ADR-0050 claim, the ADR-0051 trace, the ADR-0052 SVG, unresolved blockers,
the ADR-0053 non-init source status, the ADR-0055/ADR-0056 rejection evidence
frontier, the ADR-0057 write-buffer status, the ADR-0058 standard-signal
status, the ADR-0059 multi-command policy, the ADR-0060 trace, the ADR-0061
SVG, the ADR-0065 evidence bundle, and the updated stem command execution
next-slice list.
