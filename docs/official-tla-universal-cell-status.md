# Official TLA Universal Cell Status

Status: source-status decision, 2026-05-17.

The structured status lives in
`sources/official_tla_universal_cell_status.json`.

## Decision

Do not use the official PRC TLA files as executable Universal Cell authority.

The official theory directory contains three TLA witnesses:

- `universal-cell.tla`: a 45-line partial skeleton with constants,
  variables, `Init`, `Activate`, and an unfinished `Wire` body;
- `universalcell.tla`: a one-line `MODULE U` stub;
- `uc.tla`: an empty file.

The files do not define `Next`, `process-buffer`, `command-buffer`,
`standard-signal`, `write-buf-zero`, or `write-buf-one`. They therefore do
not resolve the command-token semantics blocked by ADR-0057, ADR-0058,
ADR-0062, and ADR-0063.

## AS Boundary

The TLA files remain useful project context, but not executable or
semantics-settling authority. AS should keep command-token execution blocked
until a complete TLA specification is recovered or AS builds its own from
already checked transition artifacts.

## Verification

Run:

```sh
python -m unittest tests.test_official_tla_universal_cell_status
```

The tests check the source-only decision, witness line counts, partial TLA
structure, absent command semantics, and cross-links from existing command
source-status artifacts.
