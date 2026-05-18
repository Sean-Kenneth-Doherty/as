# Stem Command Execution Source Status

Status: source-status decision, 2026-05-18.

ADR-0026 made the five-bit command-buffer decoder explicit. This note records
why AS still should not implement full command execution in `step_stem_cell`.

The structured status lives in
`sources/stem_command_execution_source_status.json`.

## Decision

Do not implement full stem command execution yet.

The PRC formal model gives the canonical target and command table now used by
AS, but the execution path requires behavior that AS only partially models:
ADR-0028 adds self mailbox representation, ADR-0029 adds command-message
channel-token representation, ADR-0030 processes the init-family
self-mailbox commands, and ADR-0037 dispatches just-completed self-target
init-family command buffers through that self-mailbox path. ADR-0034 records
the remaining self-mailbox `standard-signal` and write-buffer commands as an
explicit preserve-and-report unsupported boundary, ADR-0041 records the
self-target non-init command-buffer cases as an append-boundary claim, and
ADR-0044 delivers decoded neighbor-target command buffers onto output channels.
ADR-0045 promotes that delivery behavior into the named transition-claim
surface. ADR-0046 adds a schematic-linked trace for one
`neighbor-b/proc-l-init` delivery. ADR-0047 adds the corresponding rendered SVG
view. ADR-0048 records a recipient command-consumption source-status decision:
AS may execute recipient-side init-family command-message inputs, while
`standard-signal` and write-buffer command messages remain blocked. ADR-0049
implements that recipient init-family slice, and ADR-0050 promotes it into
the named claim/proof surface. ADR-0051 adds a schematic-linked trace for that
recipient slice, and ADR-0052 adds the rendered SVG view. ADR-0042/ADR-0043
now cover the self-target `write-buf-one` append boundary. ADR-0053 records
recipient non-init command-message inputs as a source-status blocking decision
and ADR-0054 promotes that rejection boundary into the named claim/proof
surface. ADR-0055 adds a schematic-linked trace for one fixed-recipient
upstream `standard-signal` rejection, and ADR-0056 adds the rendered SVG view.
ADR-0057 records write-buffer command semantics as a separate source-status
surface, and ADR-0161 implements its direct self-mailbox and completed
self-target command-buffer append behavior. ADR-0162 registers both
implemented write-buffer self-target surfaces as integrated evidence bundles.
ADR-0168 resolves recipient write-buffer command-message semantics as
source-ready append behavior while leaving runtime implementation for the next
slice.
ADR-0058 records `standard-signal` command-token semantics as still
source-blocked while preserving ordinary binary-input standard-signal
behavior. ADR-0059 selects reject-and-clear for multiple simultaneous
recipient command-message inputs, and ADR-0060 adds the matching
schematic-linked trace. ADR-0061 adds the matching rendered SVG view.
ADR-0062 records `guile-asmsim.scm` as another divergent command-semantics
witness rather than an execution-ready source. ADR-0063 records the newer
`practice/asmsim.scm` process-buffer branch as still needing documentation and
confirmed message-list codes. ADR-0064 records the official PRC TLA files as
partial, stub, or empty rather than executable command authority. ADR-0072
registers the direct self-mailbox init transition as an integrated evidence
bundle without widening the command-execution boundary. ADR-0073 registers the
direct unsupported self-mailbox preservation boundary the same way. ADR-0074
registers the completed self-target command-buffer init dispatch as an
integrated evidence bundle. ADR-0075 registers the completed self-target
non-init command-buffer append boundary as an integrated evidence bundle.
ADR-0076 registers the completed neighbor-target command-buffer delivery path
as an integrated evidence bundle. ADR-0077 composes that delivery output into
recipient init-family consumption without widening stem command execution.
Legacy simulator sketches still diverge from the formal table in ways that
should be resolved before AS treats them as executable authority for
standard-signal command tokens. AS still does not execute recipient
write-buffer command-message inputs at runtime, but that gap is now an
implementation frontier rather than a source-semantics blocker.

## Evidence

Formal command table:

- source: `/home/sean/Projects/_upstream/prc/theory/official/formal-model.txt`;
- locus: lines 437-454;
- target order: self, A neighbor, B neighbor, C neighbor;
- command order: standard-signal, stem-init, wire-r-init, wire-l-init,
  proc-r-init, proc-l-init, write-buf-zero, write-buf-one.

Formal process-buffer sketch:

- source: same formal model;
- locus: lines 660-681;
- records 32 target/message cases;
- dispatches self-target messages through a self mailbox and neighbor-target
  messages through output channels.

Legacy divergences:

- `practice/legacy/raa.scm` lines 206-222 maps target bits `00` to neighbor A
  output and `11` to self input, and places `standard-signal` at the final
  command case rather than offset 0.
- `practice/legacy/semsim.scm` lines 86-90 and
  `practice/legacy/fsmsim.scm` lines 10-14 define seven special messages and
  omit `standard-signal` from that list.
- ADR-0058 records that this divergence is not only a command-order question:
  AS must keep ordinary binary-input standard-signal behavior separate from
  command-token execution until a source resolves the bridge.

## AS Interpretation

ADR-0026 remains correct as a command-buffer decoder because it uses the formal
model's explicit command table. Execution is a different claim. To execute full
command behavior honestly, AS still needs to choose:

- how `standard-signal` behaves when selected as a self-mailbox or self-target
  command-buffer command;
- how to implement the ADR-0168 source-ready recipient write-buffer
  command-message append surface; and
- how standard-signal command-message inputs behave on recipient cells after
  the implemented init-family recipient slice.

## Verification

Run:

```sh
python -m unittest tests.test_stem_command_execution_source_status
```

The test validates the blocking decision, formal-table dependency, recorded
legacy divergences, and narrower allowed next slices.
