# Source-Status Frontier

ADR-0145 adds `autarkic_systems/source_status.py`, a focused report over the
command-token source-status records that currently bound AS runtime semantics.

## Purpose

The full project status report validates evidence registries, claim/proof
surfaces, object languages, and the source-status frontier. When the immediate
question is only "what command-token semantics are still blocked, and why?",
that broad report can obscure the answer.

The source-status frontier report narrows the first-run surface to the current
command-token blockers:

- `sources/recipient_non_init_command_source_status.json`;
- `sources/standard_signal_command_semantics_status.json`; and
- `sources/write_buffer_command_semantics_status.json`.

## Run

```sh
python -m autarkic_systems.source_status
python -m autarkic_systems.source_status --format json
```

Use repeated `--source-status <path>` arguments to validate a specific frontier
subset or a scratch fixture.

The report names:

- accepted or rejected state;
- failed subjects for missing, malformed, or schema-invalid source-status
  records;
- blocked command tokens;
- accepted source-status file paths and decisions;
- blocked runtime surfaces;
- AS boundaries;
- execution-readiness decisions, allowed-change flags, blockers, and summaries;
- unresolved resolution questions and summaries;
- source evidence explaining why unresolved questions remain open;
- resolved resolution questions and details;
- source-status cross-links behind the blocker trail;
- the safe next slice; and
- missing or invalid source-status paths.

JSON mode emits the same surface with top-level `schema_version: 2`.

ADR-0146 tightens the shared validation contract: source evidence question IDs
must match unresolved question IDs in the same source-status record. A typo or
stale evidence ID rejects the source-status record as `source-status-schema`.
ADR-0147 requires source evidence coverage for every unresolved question ID in
the same source-status record. Missing or partial evidence coverage rejects the
source-status record as `source-status-schema`.
ADR-0148 moves the standard-signal `recipient-surface` question from
unresolved to resolved, tying delivered recipient `standard-signal` command
messages to the existing non-init rejection boundary.
ADR-0149 rejects any source-status record that lists the same question ID as
both unresolved and resolved, so the focused frontier cannot present a blocker
as live and settled at the same time.
ADR-0150 moves the standard-signal `command-token-vs-binary-input` question
from unresolved to resolved, recording that command tokens do not replay
ordinary binary-input standard-signal behavior by default.
ADR-0151 moves the standard-signal `self-target-surface` question from
unresolved to resolved, so the standard-signal source-status record no longer
has live resolution questions.
ADR-0152 moves the write-buffer recipient command-message surface from
unresolved to resolved and narrows the remaining write-buffer surface question
to self-mailbox and self-target command-buffer behavior.
ADR-0153 moves that write-buffer `self-target-surface` question from
unresolved to resolved through the existing unsupported boundaries, so the
remaining write-buffer frontier is buffer-full behavior and post-append
clearing.
ADR-0154 adds an `execution_readiness` section to the focused report and
shared validation, so write-buffer append execution is explicitly blocked by
`buffer-full-boundary` and `post-append-clearing` until those questions are
resolved.
ADR-0155 tightens that shared validation: when readiness is `blocked`, its
blocker list must cover every live unresolved resolution question.
ADR-0156 adds the inverse guard: readiness cannot allow execution changes
while live unresolved resolution questions remain.
ADR-0157 adds a consistency guard: readiness cannot use decision `blocked`
while allowing execution changes.
ADR-0158 rejects duplicate unresolved and duplicate resolved question IDs
inside one source-status record, so the focused frontier cannot display the
same blocker or settled decision twice.
ADR-0159 moves write-buffer `buffer-full-boundary` from unresolved to resolved
and narrows write-buffer execution-readiness blockers to
`post-append-clearing`.
ADR-0160 moves write-buffer `post-append-clearing` from unresolved to resolved
as `preserve-appended-buffer-clear-command-source`, so the focused frontier
now reports no live write-buffer resolution questions and ready write-buffer
execution-readiness without changing schema version `2`.
ADR-0161 implements direct self-mailbox and completed self-target
command-buffer write-buffer append execution, changes write-buffer readiness
from source-ready to implemented, narrows the old unsupported self-target
boundaries to `standard-signal`, and leaves delivered recipient write-buffer
command-message inputs under the recipient non-init rejection boundary.
ADR-0162 registers both implemented write-buffer self-target surfaces as
evidence bundles and moves the write-buffer safe next slice to recipient
write-buffer command-message source resolution.
ADR-0163 adds explicit upstream `write-buf-zero` and `write-buf-one` rejection
examples to the recipient non-init claim/proof/evidence coverage without
changing the focused frontier schema or implementing recipient write-buffer
command-message execution.
ADR-0165 adds explicit standard-signal execution-readiness metadata, so the
focused frontier renders the settled `preserved-unsupported` boundary instead
of making "no live resolution questions" look like implementation readiness.
The focused frontier schema remains `2`.
ADR-0166 narrows the safe-next queue: recipient/write-buffer records point to
recipient write-buffer command-message semantics, while standard-signal points
to review of new command-token source evidence before any execution change.
The focused frontier schema remains `2`.
ADR-0167 makes that recipient write-buffer frontier a live source-status
question. The focused report now renders
`recipient-command-message-surface` and blocks write-buffer readiness on that
question while preserving source-status frontier schema `2`.
ADR-0168 resolves that live recipient write-buffer question as source-ready
append execution, clears the live write-buffer question/evidence lists, marks
write-buffer readiness as `recipient-command-message-source-ready`, and moves
the safe next slice to recipient write-buffer command-message implementation.
The focused frontier schema remains `2`.

## Boundary

This is not a separate source-status authority. It reuses the same frontier
validation used by `python -m autarkic_systems.project_status` so the focused
command and the aggregate command cannot accept different command-token
schemas.
