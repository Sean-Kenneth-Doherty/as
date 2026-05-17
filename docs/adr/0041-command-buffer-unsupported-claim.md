# ADR-0041: Command Buffer Unsupported Claim

Date: 2026-05-17

Status: Accepted

Revision note: ADR-0044 later narrows the live claim to self-target non-init
completed command buffers. Neighbor-target completed buffers now deliver onto
output channels instead of remaining at this append boundary.

## Context

ADR-0037 deliberately executes only completed self-target init-family command
buffers. Completed neighbor-target buffers and completed self-target non-init
buffers still stop at the `stem-buffer-appended` boundary.

That boundary is already covered by dispatch tests, but it is not yet part of
the named transition-claim and proof-certificate surface. Leaving it only as a
raw behavior test makes it too easy for later command-routing work to treat the
current non-execution rule as incidental.

## Decision

Promote the unsupported completed command-buffer boundary into the claim
surface:

- add `stem_command_buffer_preserves_unsupported_completion` in
  `autarkic_systems/transition_predicates.py`;
- add `UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED` to
  `claims/transition_claims.json`;
- add manifest-example certificate coverage;
- add the predicate to the transition-claim object language;
- add tests for self-target non-init completion, neighbor-target completion,
  rejected mutation, manifest examples, certificate coverage, and
  object-language validation.

The claim covers completed command buffers that are outside the ADR-0037
self-target init execution slice. It asserts append-boundary preservation only:
the current step consumes input, appends the final bit, preserves control, and
does not route, execute, or clear the completed buffer.

## Success Criteria

- Red tests fail before implementation because
  `stem_command_buffer_preserves_unsupported_completion` is absent.
- The predicate accepts a completed self-target non-init command buffer that
  remains at `stem-buffer-appended`.
- The predicate accepts a completed neighbor-target command buffer that remains
  at `stem-buffer-appended`.
- The predicate rejects processed status, wrong appended buffer, or mutated
  cell state for the unsupported boundary.
- Manifest examples evaluate to their declared expectations.
- Proof certificates cover the new claim.
- The object-language predicate vocabulary names the new predicate.

## Consequences

- The command-buffer frontier now has named claims for both the supported
  self-init execution slice and the unsupported append boundary.
- Later neighbor routing or self non-init semantics must intentionally replace
  this boundary instead of accidentally erasing it.
- Full command-buffer execution remains out of scope.

## After Action Report

Implemented.

The red run for `python -m unittest tests.test_command_buffer_unsupported_claim`
failed because `stem_command_buffer_preserves_unsupported_completion` was
absent from `autarkic_systems.transition_predicates`.

The green implementation added the predicate, the
`UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED` manifest claim,
manifest-example proof certificate coverage, and the transition-language
predicate symbol.

Final verification is recorded in `LOG.md`.

ADR-0044 revision: the predicate and manifest examples were updated so
neighbor-target delivery is treated as outside this preservation precondition.
The current positive boundary is self-target non-init command-buffer
completion.
