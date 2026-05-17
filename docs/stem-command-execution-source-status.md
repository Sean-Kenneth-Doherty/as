# Stem Command Execution Source Status

Status: source-status decision, 2026-05-17.

ADR-0026 made the five-bit command-buffer decoder explicit. This note records
why AS still should not implement full command execution in `step_stem_cell`.

The structured status lives in
`sources/stem_command_execution_source_status.json`.

## Decision

Do not implement full stem command execution yet.

The PRC formal model gives the canonical target and command table now used by
AS, but the execution path requires state that AS only partially models:
ADR-0028 adds self mailbox representation, while output channels still do not
carry arbitrary command messages. Legacy simulator sketches also diverge from
the formal table in ways that should be resolved before AS treats them as
executable authority.

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

- how future self-target execution consumes the explicit `self_mailbox` field;
- how output channels represent command messages for neighbors;
- how `standard-signal` behaves when selected as a command rather than received
  as ordinary input.

## Verification

Run:

```sh
python -m unittest tests.test_stem_command_execution_source_status
```

The test validates the blocking decision, formal-table dependency, recorded
legacy divergences, and narrower allowed next slices.
