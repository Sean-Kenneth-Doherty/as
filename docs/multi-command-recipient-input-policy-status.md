# Multi-Command Recipient Input Policy Status

Status: source-status decision, 2026-05-17.

The structured status lives in
`sources/multi_command_recipient_input_policy_status.json`.

## Decision

Reject multiple simultaneous recipient command-message inputs.

AS accepts exactly one init-family command-message token as executable
recipient input. If two or more command-message tokens appear in the same
recipient activation, AS does not infer a priority order, does not sequence
them, and does not execute any token from that activation. The existing runtime
rejects the activation with `rejected-input`, clears the active command input,
and preserves role, memory, output, automail, self-mailbox, control, and
buffer state.

This is a policy decision over existing behavior, not a runtime change.

## Covered Surfaces

- Fixed direct input with two command-message tokens.
- Fixed upstream input pulled from neighbor output with two command-message
  tokens.
- Stem direct input with multiple command-message tokens.

The ADR-0054 rejection claim already covers conflicting command-message input.
ADR-0059 adds an all-init conflict example to the claim manifest so the
selected policy is explicit in the proof-certificate surface.

## AS Boundary

The boundary is:

- one init-family command-message token: consume it under ADR-0049;
- two or more command-message tokens: reject and clear active command input;
- non-init command-token execution remains blocked under ADR-0057 and
  ADR-0058.

ADR-0060 adds that schematic-linked trace. The next visible slice is a
rendered SVG for multi-command rejection.

## Verification

Run:

```sh
python -m unittest tests.test_multi_command_recipient_input_policy_status
```

The tests check the selected policy, existing fixed/stem runtime behavior, the
claim-manifest example, and adjacent source-status frontier updates.
