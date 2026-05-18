# Write-Buffer Command Semantics Status

Status: source-status decision, updated 2026-05-18.

The structured status lives in
`sources/write_buffer_command_semantics_status.json`.

## Decision

Do not implement write-buffer command execution yet.

The formal model names `write-buf-zero` and `write-buf-one` in the command
table and routes special messages through generic special-message paths, but
it does not define the complete executable write-buffer primitive or
post-append clearing boundary.

The restored legacy sketches disagree:

- RAA appends 0 or 1 only when the buffer is not full, with input-processing
  flow clearing channels after special-message dispatch.
- SEMSIM defines append functions, but its stem special-message wrapper applies
  `zero-buf` after the selected operation, erasing the buffer after append.
- FSMSIM appends 0 or 1 and clears self-mailbox plus input channels, but does
  not expose the same buffer-full guard.

ADR-0129 records one narrower agreement across those witnesses: the named
`write-buf-zero` and `write-buf-one` commands carry literal `0` and `1` append
bits. The bit value is not derived from the ordinary standard-signal high-rail
comparison path. ADR-0142 records that as the resolved
`standard-signal-interaction` question. That does not resolve post-append
clearing or any high-rail state clearing that may be chosen as part of
post-append execution semantics.

ADR-0144 records the remaining source conflicts in
`resolution_question_evidence`, including the RAA buffer-full guard divergence
and the post-append clearing disagreement between RAA, SEMSIM, and FSMSIM.

ADR-0152 resolves the recipient-surface part of the older
`recipient-vs-stem-surface` question: delivered recipient `write-buf-zero` and
`write-buf-one` command messages are rejected as non-init command-message
inputs under the existing recipient rejection claim.

ADR-0153 resolves the self-target surface question through the existing
unsupported self-mailbox and self-target command-buffer boundaries. Direct
self-mailbox write-buffer command tokens are preserved as unsupported, and
completed self-target command-buffer write-buffer command tokens remain at the
append boundary. Executable write-buffer append semantics remain unresolved.

ADR-0154 records that unresolved execution state as an explicit
`execution_readiness` gate: write-buffer append execution is `blocked`,
execution changes are not allowed yet, and the live blockers are
`buffer-full-boundary` and `post-append-clearing`.

ADR-0159 resolves `buffer-full-boundary` as
`preserve-existing-full-buffer-boundary-before-write-buffer-append`. The formal
model gates writes to the stem buffer on less-than-full state and RAA guards
`write-buf` with `buffer-full?`; SEMSIM and FSMSIM omit a matching named
command-token full-buffer rule, but provide no contrary full-buffer policy.
Post-append clearing remains unresolved.

## AS Boundary

AS keeps write-buffer command execution blocked across these runtime surfaces:

- self-mailbox command;
- self-target command-buffer dispatch.

Recipient command-message input is no longer an unresolved write-buffer
execution surface. AS rejects delivered recipient write-buffer command messages
through `UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED`.

The current rejection and preservation claims remain the correct executable
boundary until a later ADR selects source-backed semantics for post-append
input/mail clearing, buffer clearing, and high-rail interaction. ADR-0061
completes the current multi-command rejection render frontier, so future
write-buffer work should start from source resolution rather than another
rejection artifact. ADR-0062 reviews `guile-asmsim.scm`, which has binary
`write-buf` and self-mailbox numeric append behavior but omits named
`write-buf-zero` and `write-buf-one` command tokens. ADR-0063 reviews
`practice/asmsim.scm`, whose process-buffer code uses code-shape predicates
and warning comments rather than named write-buffer command semantics.
ADR-0064 records the official PRC TLA files as incomplete and missing
write-buffer command-token semantics. ADR-0129 records the literal command
bit-source evidence without changing runtime behavior. ADR-0142 moves the
standard-signal interaction blocker out of the unresolved queue because the bit
source is literal rather than high-rail derived. ADR-0152 moves
`recipient-surface` into resolved questions. ADR-0153 moves
`self-target-surface` into resolved questions and leaves
`buffer-full-boundary` and `post-append-clearing` unresolved. ADR-0154 exposes
those two blockers as the machine-checked execution readiness gate. ADR-0159
moves `buffer-full-boundary` into resolved questions and leaves
`post-append-clearing` as the only live write-buffer blocker.

## Verification

Run:

```sh
python -m unittest tests.test_write_buffer_command_semantics_status
```

The tests check the decision, formal-model gap, legacy witness divergence,
resolved recipient, self-target, and buffer-full surfaces, remaining required
resolution questions, execution readiness, and source-status frontier updates.
