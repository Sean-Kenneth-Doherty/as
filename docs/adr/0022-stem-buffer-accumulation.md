# ADR-0022: Stem Buffer Accumulation

Date: 2026-05-17

Status: Accepted

## Context

P2 remains open because `step_stem_cell` only covers explicit automail
reconfiguration. PRC's formal model also describes a small standard-signal path
for stem cells: a one-hot standard signal selects a high rail, later one-hot
signals append `1` when they match that rail and `0` when they do not, and a
five-bit buffer is later interpreted as a command.

The full five-bit command execution and neighbor-target routing are still too
large for the current AS probe. A smaller slice is useful: implement the buffer
accumulation behavior while making the full-buffer boundary explicit and
tested.

## Decision

Add the first standard-signal stem buffer behavior to `step_stem_cell`:

- a one-hot standard input selects the control rail when no control rail is
  set, consumes input, and leaves the buffer unchanged;
- when a control rail is already set and the buffer has fewer than five bits,
  a matching one-hot input appends `1` and a non-matching one-hot input appends
  `0`;
- a full five-bit buffer returns an explicit boundary status without consuming
  input or pretending to execute the command;
- malformed stem input is rejected and cleared;
- automail reconfiguration keeps priority over standard-signal buffering.

Add tests in `tests/test_stem_buffer_accumulation.py` and a human-facing note
in `docs/stem-buffer-accumulation.md`.

## Success Criteria

- Red tests fail before implementation because the new stem buffer statuses and
  behavior are absent.
- One-hot standard input selects control when control is unset.
- Matching one-hot input appends `1` to a non-full buffer.
- Non-matching one-hot input appends `0` to a non-full buffer.
- A full buffer is reported explicitly without consuming input.
- Malformed stem input is rejected and cleared.
- Existing automail tests still pass, proving the new branch did not regress
  the prior reconfiguration subset.

## Consequences

- P2 advances from automail-only stem behavior to the first source-backed
  command-buffer behavior.
- Full buffer command decoding, neighbor-target delivery, and dynamic
  reconfiguration remain separate ADRs.

## After Action Report

Red step:

- `python -m unittest tests.test_stem_buffer_accumulation` failed with five
  assertion failures because current `step_stem_cell` returned `idle` for the
  standard-signal buffer cases.

Green step:

- Added `stem-control-selected`, `stem-buffer-appended`, and
  `stem-buffer-full` statuses.
- Extended `step_stem_cell` with one-hot control selection, 1/0 bit append,
  explicit full-buffer boundary, and malformed-input rejection.
- Updated `language/transition_claim_language.json` so the object-language
  status vocabulary matches the implementation.
- Added `docs/stem-buffer-accumulation.md`.
- `python -m unittest tests.test_stem_buffer_accumulation
  tests.test_stem_automail` passed 14 tests.

Full verification:

- `python -m unittest discover` passed 104 tests.
- `python -m py_compile autarkic_systems/universal_cell.py
  tests/test_stem_buffer_accumulation.py` passed.
- `jq -e . language/transition_claim_language.json` passed.
- `git diff --check` passed.

Coverage limits:

- This implements buffer accumulation only.
- It does not interpret five-bit commands.
- It does not route command output to neighbors.
- It does not add a manifest claim for the new behavior.
