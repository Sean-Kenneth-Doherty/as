# ADR-0064: Official TLA Universal Cell Status

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0062 and ADR-0063 reviewed the Guile and Chez Scheme simulator witnesses
for the blocked `standard-signal` and write-buffer command-token frontier.
The PRC official theory directory also contains three TLA files:
`universal-cell.tla`, `universalcell.tla`, and `uc.tla`.

Because TLA would be an attractive formal authority for future agents, AS must
record whether these files are executable/specification-ready before anyone
uses them to justify runtime behavior.

## Decision

Add `sources/official_tla_universal_cell_status.json` and a human-facing note
recording that the official TLA files are not dependency-ready AS evidence.

This ADR will record:

- `universal-cell.tla` as a 45-line partial sketch with constants, variables,
  `Init`, `Activate`, and an incomplete `Wire` body;
- `universalcell.tla` as a one-line `MODULE U` stub;
- `uc.tla` as an empty file;
- absence of `Next`, command-buffer, `standard-signal`, and write-buffer
  semantics from the TLA witnesses;
- cross-links from standard-signal, write-buffer, and stem command
  source-status artifacts.

This ADR does not change Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because
  `sources/official_tla_universal_cell_status.json` is absent.
- The source-status artifact records each official TLA witness path and line
  count.
- Tests verify that `universal-cell.tla` contains only the partial
  activation/role skeleton and lacks command semantics.
- Tests verify that `universalcell.tla` is a stub and `uc.tla` is empty.
- Tests verify that existing command source-status files reference this
  ADR-0064 evidence.
- Runtime behavior remains unchanged.

## Consequences

The official TLA files remain useful project context, but not executable or
semantics-settling authority. AS should keep command-token execution blocked
until a later ADR either recovers a complete TLA specification or deliberately
constructs an AS-owned one from already checked transition artifacts.

## Test Plan

- Red: `python -m unittest tests.test_official_tla_universal_cell_status`
  fails because the source-status artifact is absent.
- Green: the same focused test passes after adding the artifact and
  cross-links.
- Regression: run adjacent command source-status tests and the full default
  suite before commit.

## After Action Report

Implemented in `sources/official_tla_universal_cell_status.json` and
`docs/official-tla-universal-cell-status.md`.

The focused red run failed because
`sources/official_tla_universal_cell_status.json` was absent. The green
implementation records the official PRC TLA files as incomplete evidence:
`universal-cell.tla` is a partial 45-line activation skeleton,
`universalcell.tla` is a one-line stub, and `uc.tla` is empty. None of them
define `Next`, process-buffer, command-buffer, `standard-signal`, or
write-buffer command-token semantics.

Existing standard-signal, write-buffer, and stem command source-status
artifacts now cross-link this evidence. Runtime behavior remains unchanged.
