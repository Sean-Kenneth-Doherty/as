# ADR-0038: Self Command Buffer Init Claim

Date: 2026-05-17

Status: Accepted

## Context

ADR-0037 added the first narrow command-buffer-to-behavior path: when a
standard-signal append completes a self-target init-family buffer,
`step_stem_cell` decodes the buffer and reuses the already tested
self-mailbox init semantics.

That behavior is now stable enough to join the named transition-claim surface.
Keeping it only as raw transition code would make the claim/proof layer lag
behind the new command-buffer behavior.

## Decision

Promote the narrow self-target init command-buffer dispatch into the claim
surface:

- add `stem_command_buffer_executes_self_init` in
  `autarkic_systems/transition_predicates.py`;
- add `UC-STEM-COMMAND-BUFFER-SELF-INIT` to
  `claims/transition_claims.json`;
- add manifest-example certificate coverage;
- add the predicate to the transition-claim object language;
- add tests for predicate behavior, manifest examples, certificate coverage,
  and object-language validation.

The claim covers only completed self-target init-family buffers. It does not
certify neighbor routing, self-target `standard-signal`, write-buffer
commands, or full command-buffer execution.

## Success Criteria

- Red tests fail before implementation because
  `stem_command_buffer_executes_self_init` is absent.
- The predicate accepts a valid self-target `proc-l-init` completed-buffer
  transition.
- The predicate rejects wrong target role/memory and uncleared control/buffer
  state.
- Manifest examples evaluate to their declared expectations.
- Proof certificates cover the new claim.
- The object-language predicate vocabulary names the new predicate.

## Consequences

- The first command-buffer execution slice now has the same claim/certificate
  discipline as prior stable transition subsets.
- Later trace/SVG work can depend on a named claim.
- Full command-buffer execution remains out of scope.

## After Action Report

Implemented.

The red run for `python -m unittest tests.test_self_command_buffer_init_claim`
failed because `stem_command_buffer_executes_self_init` was absent from
`autarkic_systems.transition_predicates`.

The green implementation added the predicate, the
`UC-STEM-COMMAND-BUFFER-SELF-INIT` manifest claim, manifest-example proof
certificate coverage, and the transition-language predicate symbol.

Final verification is recorded in `LOG.md`.
