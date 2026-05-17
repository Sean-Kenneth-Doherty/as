# ADR-0050: Recipient Init Command-Message Claim

Date: 2026-05-17

Status: Accepted

## Context

ADR-0049 made recipient-side init-family command-message inputs executable in
the Universal Cell probe. The project pattern after new transition behavior is
to promote the stable subset into the named claim and proof-certificate
surface before using it as evidence for traces, renders, or wider command
execution.

The implemented behavior is still intentionally narrow. It covers a single
init-family command-message token on a recipient input channel, or a pulled
upstream init-family command-message token for fixed cells. It does not cover
`standard-signal`, write-buffer command messages, multiple simultaneous
command-message inputs, or occupied-output cases.

## Decision

Add a named predicate and claim for the ADR-0049 behavior:

- predicate: `recipient_init_command_message_processed`;
- claim ID: `UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED`;
- proof rule: existing `manifest-example`;
- object-language predicate-symbol entry.

The predicate covers both fixed and stem recipients, including the fixed-cell
upstream-pull case. It requires the expected role/memory target, cleared input
and output channels, cleared command state, and correct upstream preservation
or clearing depending on whether the command came from direct input or pulled
upstream.

## Success Criteria

- Red tests fail before implementation because the predicate, manifest claim,
  proof certificate, and language symbol are absent.
- The predicate accepts fixed direct-input consumption and fixed pulled-upstream
  consumption for init-family command messages.
- The predicate accepts stem recipient command consumption with control,
  buffer, and self-mailbox clearing.
- The predicate rejects wrong targets, uncleared command state, and wrong
  transition status.
- The predicate ignores non-init command-message inputs and multiple-command
  conflict inputs as inactive preconditions.
- Claim manifest examples include both accepted and rejected cases.
- Proof certificates cover the new claim.
- The transition-claim object language names the new predicate symbol.

## Consequences

- ADR-0049 becomes a durable transition claim rather than only a behavior test.
- Later recipient-side schematic traces can depend on a named claim.
- Full command-message consumption remains blocked at the source-status
  boundary.

## After Action Report

Implemented.

The red run for
`python -m unittest tests.test_recipient_init_command_message_claim` failed
because `recipient_init_command_message_processed` was absent from
`autarkic_systems.transition_predicates`.

The green implementation added the predicate, claim manifest examples, proof
certificate entry, object-language predicate symbol, and source-status updates
that move the next slice to a schematic-linked trace.

Final verification is recorded in `LOG.md`.
