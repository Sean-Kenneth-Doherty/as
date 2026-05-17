# Self Command Buffer Init Dispatch

Status: narrow command-buffer execution slice, 2026-05-17.

ADR-0037 adds the first command-buffer-to-behavior path in
`step_stem_cell`. When a standard-signal append fills a five-bit buffer, AS
decodes the buffer with the ADR-0026 command map. If the decoded command is a
self-target init-family command, AS reuses the direct self-mailbox init
semantics and returns `stem-command-buffer-self-processed`.
ADR-0038 promotes this behavior into the named claim
`UC-STEM-COMMAND-BUFFER-SELF-INIT`.
ADR-0039 records the same bounded behavior as a schematic-linked trace.
ADR-0041 promotes the remaining completed-buffer append boundary into the
named claim `UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED`.

## Execution Boundary

The slice covers only completed buffers whose decoded target is `self` and
whose decoded command is one of:

- `stem-init`;
- `wire-r-init`;
- `wire-l-init`;
- `proc-r-init`;
- `proc-l-init`.

On that path, the transition:

- clears consumed input;
- clears output and automail;
- clears `self_mailbox`;
- clears control and buffer;
- applies the commanded role/memory target.

Completed neighbor-target buffers now deliver the decoded command token to the
corresponding output channel and return
`stem-command-buffer-neighbor-delivered`. Completed self-target
`standard-signal`, `write-buf-zero`, and
`write-buf-one` buffers also still stop at `stem-buffer-appended`.

## Source Boundary

This is not full command-buffer execution. It uses the source-backed target and
command map from `sources/stem_command_buffer_map.json`, but it does not execute
neighbor-side command tokens, implement write-buffer commands, or resolve
`standard-signal` command semantics.

## Verification

Run:

```sh
python -m unittest tests.test_self_command_buffer_init_dispatch
```

The tests cover self `proc-l-init`, self `stem-init`, neighbor delivery,
self non-init non-execution, and transition-language status coverage.
