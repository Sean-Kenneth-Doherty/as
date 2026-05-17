# ADR-0004: Universal Cell Transition Probe

Date: 2026-05-16

Status: Accepted

## Context

ADR-0002 recommended the first executable AS artifact be a tiny
substrate/formal bridge around one Universal Cell transition invariant. PRC's
full Universal Cell simulator is research-grade Scheme with known rough edges,
and the TLA+ sketch is incomplete. AS needs a small, testable foothold before
depending on the whole simulator.

The PRC formal model gives enough structure for a narrow fixed-role probe:

- wire and processor cells consume standard three-channel binary signals;
- the current memory selects right or left rotation;
- processor cells toggle memory after routing;
- occupied output blocks processing rather than being overwritten;
- a stem-init special signal reconfigures a fixed cell back to stem;
- malformed input is rejected and cleared.

## Decision

Add a minimal Python reference probe for fixed Universal Cell transitions:

- `autarkic_systems/universal_cell.py`;
- `tests/test_universal_cell.py`.

This is not a full PRC simulator. It is a deliberately small executable
contract for the first AS substrate requirement.

## Success Criteria

- Tests are written before implementation and fail while code is absent.
- The fast suite runs with the Python standard-library `unittest` runner.
- Tests cover standard wire routing, processor memory toggling, blocked output,
  upstream pull, stem-init reconfiguration, malformed input clearing, and input
  validation.
- The code is documented enough for a competent reader unfamiliar with PRC to
  understand why each transition exists.

## Consequences

- AS gains its first executable artifact.
- The implementation remains intentionally smaller than PRC's real simulator,
  so it must not be described as proving PRC correctness.
- Future work can add a formal-side predicate layer over these checked
  transition results.

## After Action Report

Red step:

- `python -m unittest tests.test_universal_cell` failed with
  `ModuleNotFoundError: No module named 'autarkic_systems'` before the package
  existed.

Green step:

- `python -m unittest tests.test_universal_cell` passed 8 tests after
  implementation.
- `python -m unittest discover` passed 8 tests after adding `tests/__init__.py`
  for default discovery.
- `python -m py_compile autarkic_systems/universal_cell.py
  autarkic_systems/__init__.py tests/__init__.py tests/test_universal_cell.py`
  passed.
- `git diff --check` passed.

Coverage limits:

- This probe covers only fixed wire/proc activation at a high level.
- It does not model stem buffer processing, automail, lattice scheduling, power
  routing, or the full PRC Scheme simulator.
- It does not yet expose a formal-side predicate layer; that remains the next
  AS bridge task.
