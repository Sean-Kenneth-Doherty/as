# Stem Command Buffer Map

Status: source-backed command decoder map, 2026-05-17.

This artifact records PRC's five-bit stem command-buffer encoding as a
structured AS map. It is the bridge between ADR-0022's buffer accumulation and
a later command-execution ADR.

The structured artifact lives in `sources/stem_command_buffer_map.json`; loader
and validation support live in `autarkic_systems/stem_command_map.py`.

## Encoding

The PRC formal model groups the 32 command values into four target ranges:

- `0` through `7`: `self`;
- `8` through `15`: `neighbor-a`;
- `16` through `23`: `neighbor-b`;
- `24` through `31`: `neighbor-c`.

Each range uses the same eight command offsets:

- `0`: `standard-signal`;
- `1`: `stem-init`;
- `2`: `wire-r-init`;
- `3`: `wire-l-init`;
- `4`: `proc-r-init`;
- `5`: `proc-l-init`;
- `6`: `write-buf-zero`;
- `7`: `write-buf-one`.

AS decodes the accumulated five-bit buffer in list order as a binary value with
the first accumulated bit as the most significant bit. Future command-execution
work must preserve or explicitly revise that convention.

## Boundary

This map only decodes target and command identity. It does not mutate a
`Cell`, deliver a message to a neighbor, interpret `standard-signal`, or execute
write-buffer commands.

## Verification

Run:

```sh
python -m unittest tests.test_stem_command_buffer_map
```

The tests verify source anchoring, target and command coverage, representative
decodes, and rejection of malformed buffers, incomplete maps, noncanonical
target grouping, or noncanonical command names.
