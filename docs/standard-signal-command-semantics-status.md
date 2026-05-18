# Standard-Signal Command Semantics Status

Status: source-status decision, updated 2026-05-18.

The structured status lives in
`sources/standard_signal_command_semantics_status.json`.

## Decision

Do not implement `standard-signal` command-token execution yet.

AS already implements ordinary standard-signal behavior for binary input:
fixed wire/proc routing and stem high-rail / command-buffer accumulation. That
does not settle the separate command-token question. The formal model also
names `standard-signal` at command offset 0 for each target range, but it does
not define whether that token should execute from self-mailbox state or remain
unsupported.

ADR-0150 resolves the command-token/binary-input equivalence question:
`standard-signal` command tokens do not automatically replay ordinary
binary-input standard-signal behavior. The formal model separates ordinary
standard-signal processing from the command-table `standard-signal` entry, and
the reviewed legacy witnesses keep `standard-signal` outside special-message
dispatch.

ADR-0151 resolves the remaining self-target-surface question: direct
self-mailbox `standard-signal` command tokens are preserved as unsupported, and
completed self-target command-buffer `standard-signal` tokens remain preserved
at the append boundary.

The formal-model prose narrows one self-target case: it says wire, proc, and
stem cells all perform productive behavior on standard signals "unless sent to
the self-mailbox of a stem cell." AS therefore must not treat a stem
self-mailbox `standard-signal` command as ordinary binary-input
standard-signal behavior. ADR-0143 records that narrower equivalence decision
as resolved without selecting the exact preserve, clear/no-op, or execution
rule.

ADR-0128 resolves the command-table-offset question: AS preserves the formal
PRC command-buffer map from ADR-0026, where `standard-signal` is offset `0` in
each target range. RAA's offset-7 command-buffer divergence remains recorded
as legacy evidence, but it is no longer an open AS ordering question.

ADR-0148 resolves the recipient-surface question: delivered recipient
`standard-signal` command messages remain in the already-claimed recipient
non-init rejection boundary. The formal model gives no recipient execution
rule for that command token, and the reviewed legacy witnesses exclude
`standard-signal` from their special-message sets.

The restored legacy sketches do not supply a stable execution rule:

- RAA excludes `standard-signal` from `special-messages`, treats ordinary
  standard input as numeric `1`, and maps the final command-buffer case to
  `standard-signal`.
- SEMSIM excludes `standard-signal` from `special-messages` and classifies
  binary standard input separately from special-message dispatch.
- FSMSIM excludes `standard-signal` from `special-messages`, classifies
  nonzero binary input as ordinary standard input, and indexes command-buffer
  messages through the seven special messages only.

ADR-0144 recorded source conflict behind then-unresolved standard-signal
questions in `resolution_question_evidence`, so the project status report
could name both blockers and why they remained blocked while the queue was
live.

ADR-0165 records the settled execution-readiness boundary explicitly:
`standard-signal` command-token execution is preserved as unsupported at the
self-target boundaries, execution changes are not allowed, and any future
change requires new source evidence that replaces the existing unsupported
boundary.

ADR-0166 narrows the safe-next wording to that same evidence gate. The
standard-signal source-status record no longer advertises a generic
`standard-signal` / write-buffer revisit as its next slice; it points only to
new standard-signal command-token source evidence before any execution change.

ADR-0171 performs that source review and records the dated snapshot in
`sources/standard_signal_source_review_status.json`. The reviewed upstream
heads did not change from the pinned manifest, and the PRC local witness stayed
at `7e82c73fac8f108faac801a5c65e2c2b92653ba5`. No reviewed source replaces the
preserved-unsupported boundary, so the source-status safe-next field is now the
guard `no-standard-signal-command-token-execution-change-without-new-source-evidence`.

## AS Boundary

AS keeps `standard-signal` command-token execution blocked across these runtime
surfaces:

- self-mailbox command;
- self-target command-buffer dispatch.

Recipient command-message input is no longer an unresolved
`standard-signal` execution surface. AS rejects delivered recipient
`standard-signal` command messages through
`UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED`.

Command-token execution also no longer inherits ordinary binary-input
standard-signal behavior by default. Future work that wants executable
standard-signal command-token behavior must intentionally replace these
unsupported preservation boundaries with new source evidence.

The current ordinary standard-signal behavior remains valid because it is
binary-input behavior, not command-token execution. ADR-0059 selects
reject-and-clear for multi-command recipient input conflicts, and ADR-0060
adds the corresponding trace. ADR-0061 adds the rendered SVG view for that
trace, so the next useful command-execution work is source resolution rather
than more rejection rendering. ADR-0062 reviews `guile-asmsim.scm`, which keeps
standard signals as ordinary binary input while appending numeric standard
signals to a process-buffer command list; this strengthens the blocker rather
than resolving command-token semantics. ADR-0063 reviews `practice/asmsim.scm`,
which uses `tar+sic?` and code-shape predicates rather than a named
`standard-signal` command token. ADR-0064 records the official PRC TLA files
as incomplete and missing `standard-signal` command-token semantics. ADR-0127
records the formal-model self-mailbox exception as a narrowed
self-target-surface source anchor without changing runtime behavior. ADR-0128
removes `command-table-offset` from the unresolved queue after resolving it in
favor of the formal PRC command-buffer map. ADR-0143 exposes the self-mailbox
exception as a resolved sub-decision while leaving `self-target-surface`
unresolved. ADR-0148 moves `recipient-surface` into resolved questions through
the existing recipient non-init rejection boundary. ADR-0150 moves
`command-token-vs-binary-input` into resolved questions. ADR-0151 moves
`self-target-surface` into resolved questions, leaving the standard-signal
source-status record with no unresolved questions. ADR-0165 adds explicit
execution-readiness metadata so "no unresolved questions" cannot be mistaken
for permission to implement `standard-signal` command-token execution.
ADR-0166 updates the safe-next wording to match that settled boundary.
ADR-0171 closes that review gate for the current source snapshot and leaves no
active standard-signal execution slice.

## Verification

Run:

```sh
python -m unittest tests.test_standard_signal_command_semantics_status
```

The tests check the decision, formal-model command/binary distinction, legacy
witness divergence, resolved recipient-surface, command-token/binary-input,
self-target boundaries, execution-readiness metadata, ADR-0171 source-review
backlink, and source-status frontier updates.
