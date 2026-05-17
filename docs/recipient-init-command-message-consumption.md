# Recipient Init Command-Message Consumption

Status: executable transition slice, 2026-05-17.

ADR-0049 implements the first recipient-side command-message behavior after
neighbor command-buffer delivery. It is intentionally narrower than full PRC
command execution.

ADR-0050 promotes this behavior into the named claim
`UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED`.

## Behavior

`step_fixed_cell` and `step_stem_cell` now consume a single input-channel
init-family command message:

- `stem-init`;
- `wire-r-init`;
- `wire-l-init`;
- `proc-r-init`;
- `proc-l-init`.

The transition status is `recipient-init-command-message-processed`.

The command selects the same role/memory targets used by the direct
self-mailbox init subset. The resulting cell clears input, output, automail,
self-mailbox, control, and buffer state. Fixed cells also process a pulled
upstream init-family command message when their direct input is empty.

The old fixed-cell `si` shorthand remains a separate `stem-init` transition
status. ADR-0049 is about command-message tokens such as `stem-init`, not the
older `si` special signal.

## Boundaries

This slice does not execute:

- `standard-signal` command-message inputs;
- `write-buf-zero` or `write-buf-one` command-message inputs;
- multiple simultaneous command-message inputs;
- any occupied-output case that the current AS transition probe already
  blocks.

Those inputs remain rejected or blocked at the previous boundary.

## Verification

Run:

```sh
python -m unittest tests.test_recipient_init_command_messages
```

The tests cover fixed-cell input consumption, pulled upstream command-message
consumption, stem command-state clearing, distinct `stem-init` command-token
versus `si` shorthand status, unresolved non-init rejection, multi-command
conflict rejection, and transition-language status coverage.
