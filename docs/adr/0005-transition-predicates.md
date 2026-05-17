# ADR-0005: Transition Predicates

Date: 2026-05-16

Status: Accepted

## Context

ADR-0004 created the first executable substrate probe. ADR-0002 requires AS to
bridge substrate behavior to named formal claims. The next step should not be a
large theorem prover; it should be a small predicate layer that gives names and
truth values to the invariants already tested by the transition probe.

## Decision

Add `autarkic_systems/transition_predicates.py` with simple predicate checks
over `Cell` and `StepResult`:

- output is not overwritten when occupied;
- consumed input is cleared after terminal processing;
- fixed-role memory follows the wire/proc routing rule;
- stem-init resets a fixed cell to stem.

Add `tests/test_transition_predicates.py` before implementation.

## Success Criteria

- Predicate tests fail before implementation and pass after implementation.
- Predicate results carry a stable name, boolean result, and explanatory
  detail.
- The predicates remain descriptive checks over the probe, not claims of full
  PRC or SJAS correctness.

## Consequences

- AS gains the first formal-side vocabulary over its substrate probe.
- Future work can use these predicate names as the bridge toward proof objects
  or claim manifests.

## After Action Report

Red step:

- `python -m unittest tests.test_transition_predicates` failed with
  `ModuleNotFoundError: No module named
  'autarkic_systems.transition_predicates'` before the predicate module existed.

Green step:

- `python -m unittest tests.test_transition_predicates` passed 8 tests.
- `python -m unittest discover` passed 16 tests.
- `git diff --check` passed.

Coverage limits:

- Predicates are descriptive checks over ADR-0004's transition probe.
- They are not yet encoded proof objects, theorem-prover clauses, or SJAS
  consistency claims.
