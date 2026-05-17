# Recipient Command Consumption Source Status

Status: source-status decision, 2026-05-17.

ADR-0048 records the source boundary for recipient-side command-message inputs
after ADR-0044 through ADR-0047 made neighbor-target command-buffer delivery
executable, claimed, traced, and rendered.

The structured status lives in
`sources/recipient_command_consumption_source_status.json`.

## Decision

Implement recipient-side init-family command-message consumption next, but do
not implement full command-message consumption yet.

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
self-target init command-buffer dispatch. The next executable slice may reuse
that stable init-family subset for recipient-side command-message inputs.

## Remaining Blockers

`standard-signal` remains blocked because the formal command table includes it
as command offset 0, while the legacy special-message sets exclude it.

`write-buf-zero` and `write-buf-one` remain blocked because AS has not yet
selected a complete write-buffer boundary for fixed cells, stem cells, or
buffer-full behavior.

Full recipient-side command-message consumption also needs a conflict policy
for multiple simultaneous command-message inputs.

## Verification

Run:

```sh
python -m unittest tests.test_recipient_command_consumption_source_status
```

The tests check the source-status decision, the formal input-special-message
anchor, the legacy special-message sets, unresolved blockers, and the updated
stem command execution next-slice list.
