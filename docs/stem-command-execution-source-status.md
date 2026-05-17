# Stem Command Execution Source Status

Status: source-status decision, 2026-05-17.

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
view.
ADR-0042/ADR-0043 now cover the self-target `write-buf-one` append boundary.
Legacy simulator sketches still diverge from the formal table in ways that
should be resolved before AS treats them as executable authority, and AS still
does not execute command-message inputs on recipient cells.

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

## AS Interpretation

ADR-0026 remains correct as a command-buffer decoder because it uses the formal
model's explicit command table. Execution is a different claim. To execute
commands honestly, AS first needs to choose:

- how decoded output-channel command tokens are consumed by neighbors;
- how `standard-signal`, `write-buf-zero`, and `write-buf-one` behave when
  selected as self-mailbox or self-target command-buffer commands.

## Verification

Run:

```sh
python -m unittest tests.test_stem_command_execution_source_status
```

The test validates the blocking decision, formal-table dependency, recorded
legacy divergences, and narrower allowed next slices.
