# Write-Buffer Command Semantics Status

Status: source-status decision, updated 2026-05-18.

The structured status lives in
`sources/write_buffer_command_semantics_status.json`.

## Decision

Write-buffer command execution is source-resolved and implemented for direct
stem `self_mailbox` commands plus completed self-target command buffers.
Delivered recipient command-message append execution is source-ready after
ADR-0168, but current runtime still rejects those messages until the
implementation ADR replaces the checked recipient boundary.

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
`standard-signal-interaction` question.

ADR-0144 records the remaining source conflicts in
`resolution_question_evidence`, including the RAA buffer-full guard divergence
and the post-append clearing disagreement between RAA, SEMSIM, and FSMSIM.

ADR-0152 resolves the recipient-surface part of the older
`recipient-vs-stem-surface` question: delivered recipient `write-buf-zero` and
`write-buf-one` command messages are rejected as non-init command-message
inputs under the existing recipient rejection claim.

ADR-0153 originally resolved the self-target surface question through the
existing unsupported self-mailbox and self-target command-buffer boundaries.
ADR-0161 supersedes that preservation boundary for write-buffer commands:
direct self-mailbox write-buffer command tokens and completed self-target
command-buffer write-buffer tokens now append the command's literal bit and
clear the active command source.

ADR-0154 initially recorded that unresolved execution state as an explicit
`execution_readiness` gate. ADR-0159 and ADR-0160 later cleared the then-live
self-target blockers, and ADR-0161 updates the self-target readiness state
from source-ready to implemented for the self-target append surfaces.
ADR-0162 adds integrated evidence bundles for both implemented self-target
surfaces, so the remaining safe next write-buffer work is recipient
write-buffer command-message source resolution rather than another evidence
artifact for the self-target append behavior.
ADR-0163 makes the current recipient-side rejection boundary explicit for both
delivered write-buffer command tokens by adding upstream `write-buf-zero` and
`write-buf-one` positive examples to the recipient non-init claim/proof
surface and to the covered examples of the recipient non-init evidence bundle.
ADR-0167 makes that remaining recipient surface explicit again as a live
resolution question. Write-buffer readiness is now
`self-target-implemented-recipient-blocked`: self-target append behavior is
implemented, but delivered recipient write-buffer command-message execution
remains blocked until `recipient-command-message-surface` is resolved.
ADR-0168 resolves that surface as
`execute-recipient-write-buffer-command-message-append`. Write-buffer
readiness is now `recipient-command-message-source-ready`: the recipient
append rule is source-resolved, direct self-mailbox and completed self-target
surfaces remain implemented, and current recipient runtime still rejects
delivered write-buffer command messages until the implementation ADR changes
the checked transition behavior.

ADR-0159 resolves `buffer-full-boundary` as
`preserve-existing-full-buffer-boundary-before-write-buffer-append`. The formal
model gates writes to the stem buffer on less-than-full state and RAA guards
`write-buf` with `buffer-full?`; SEMSIM and FSMSIM omit a matching named
command-token full-buffer rule, but provide no contrary full-buffer policy.
ADR-0160 resolves `post-append-clearing` as
`preserve-appended-buffer-clear-command-source`. RAA and FSMSIM preserve the
appended literal bit while clearing command-source/input state; SEMSIM's stem
wrapper clears the buffer after append, so AS records SEMSIM as divergent
legacy behavior instead of selecting the buffer-erasing wrapper.

ADR-0161 implements the source-resolved self-target append behavior for:

- direct self-mailbox command execution;
- completed self-target command-buffer dispatch.

Recipient command-message input remains outside the implemented write-buffer
surface. AS currently rejects delivered recipient write-buffer command
messages through `UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED`, but that
runtime boundary is now an implementation backlog item rather than a source
semantics blocker.

The current recipient rejection claim remains the correct executable boundary
until a later implementation ADR moves recipient write-buffer command-message
input out of the non-init rejection surface. ADR-0168 records the resolved
source decision: the formal model plus RAA and FSMSIM support input-channel
write-buffer append behavior, while SEMSIM remains divergent on post-append
clearing as already recorded by ADR-0160. ADR-0061 completes the current
multi-command rejection
render frontier, so future write-buffer work should start from source
resolution rather than another rejection artifact. ADR-0062 reviews
`guile-asmsim.scm`, which has binary
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
`post-append-clearing` as the only live write-buffer blocker. ADR-0160 moves
`post-append-clearing` into resolved questions, clears the live write-buffer
question queue, and marks write-buffer append execution as source-ready for a
later implementation ADR. ADR-0161 implements that self-target append slice,
narrows the old unsupported boundaries to `standard-signal`, and ADR-0162
registers the direct self-mailbox plus completed self-target command-buffer
write-buffer execution paths as evidence bundles. ADR-0163 then widens the
existing recipient rejection coverage to name both delivered write-buffer
tokens explicitly. ADR-0167 restores a live write-buffer question for the
recipient command-message surface, with matching evidence and readiness
blocker metadata. ADR-0168 resolves that question, clears the live
write-buffer question queue, and moves the safe-next slice to recipient
write-buffer command-message execution.

## Verification

Run:

```sh
python -m unittest tests.test_write_buffer_command_semantics_status
```

The tests check the decision, formal-model gap, legacy witness divergence,
resolved recipient, self-target, buffer-full, and post-append surfaces, the
resolved recipient command-message surface, the source-ready recipient
execution-readiness gate, and source-status frontier updates.
