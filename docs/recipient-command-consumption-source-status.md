# Recipient Command Consumption Source Status

Status: source-status decision, 2026-05-17.

ADR-0048 records the source boundary for recipient-side command-message inputs
after ADR-0044 through ADR-0047 made neighbor-target command-buffer delivery
executable, claimed, traced, and rendered.

The structured status lives in
`sources/recipient_command_consumption_source_status.json`.

## Decision

ADR-0048 decided to implement recipient-side init-family command-message
consumption next, but not full command-message consumption.

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

`standard-signal` remains blocked because the formal command table includes it
as command offset 0, while the legacy special-message sets exclude it.

`write-buf-zero` and `write-buf-one` remain blocked because AS has not yet
selected a complete write-buffer boundary for fixed cells, stem cells, or
buffer-full behavior.

Full recipient-side command-message consumption also needs a conflict policy
for multiple simultaneous command-message inputs.

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

## Verification

Run:

```sh
python -m unittest tests.test_recipient_command_consumption_source_status
```

The tests check the source-status decision, the formal input-special-message
anchor, the legacy special-message sets, the implemented ADR-0049 slice,
the ADR-0050 claim, the ADR-0051 trace, the ADR-0052 SVG, unresolved blockers,
and the updated stem command execution next-slice list.
