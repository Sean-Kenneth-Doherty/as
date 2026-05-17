# Guile ASMSIM Command Semantics Status

Status: source-status decision, 2026-05-17.

The structured status lives in
`sources/guile_asmsim_command_semantics_status.json`.

## Decision

Do not implement `standard-signal` or write-buffer command-token execution
from `practice/legacy/guile-asmsim.scm`.

The witness is useful because it exposes another command-buffer and
self-mailbox sketch, but it does not settle the AS frontier:

- its `special-messages` list contains only the init-family commands;
- it excludes `standard-signal`, `write-buf-zero`, and `write-buf-one`;
- its `write-buf` helper appends binary `0`/`1` values rather than named
  write-buffer command tokens;
- its self-mailbox path appends numeric `0`/`1` messages to the buffer;
- its process-buffer command list appends `special-messages` and
  `standard-signals`, diverging from the formal named command table.

## AS Boundary

This witness strengthens the blocker recorded by ADR-0057 and ADR-0058. AS
should keep command-token execution blocked until a later ADR selects a stable
source-backed command representation, target mapping, and clearing boundary.

## Verification

Run:

```sh
python -m unittest tests.test_guile_asmsim_command_semantics_status
```

The tests check the source-only decision, the init-family-only special-message
set, the numeric write-buffer evidence, the command-buffer divergence, and the
cross-links from the existing command source-status artifacts.
