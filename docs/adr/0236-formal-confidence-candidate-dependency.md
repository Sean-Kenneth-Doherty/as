# ADR-0236: Formal Confidence Candidate Dependency

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0235 added a checked fixed-point equation candidate surface. The
formal-confidence target text now names that candidate, but
`autarkic_systems.formal_confidence` still only validates that the
configuration text is present. That leaves a drift risk: the aggregate
formal-confidence report could remain accepted even if the equation-candidate
manifest disappeared or began overclaiming.

## Decision

Add a structured `fixed_point_equation_candidate` configuration field to
`claims/formal_confidence_targets.json` and make the formal-confidence
validator load and validate that candidate surface.

This keeps the aggregate path fail-closed without changing the claim status.
The formal-confidence target remains blocked on fixed-point construction.

This does not implement a diagonal lemma, fixed-point equation proof,
arithmetized proof predicate, self-consistency theorem, runtime behavior,
command semantics, evidence bundles, or GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because
  `fixed_point_equation_candidate` is not a required configuration field and
  missing candidate files do not make formal-confidence validation fail.
- The formal-confidence manifest contains
  `fixed_point_equation_candidate:
  claims/fixed_point_equation_candidates.json`.
- `autarkic_systems.formal_confidence` validates that referenced candidate
  surface and exposes an accepted result when it is healthy.
- Missing or invalid candidate references make the formal-confidence report
  reject with a compact candidate dependency failure subject.
- Text and JSON CLI modes expose the new validation result.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_formal_confidence_target
  tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live formal-confidence text/JSON, live project-status
  summary, live handoff with `--refresh-remotes`, compileall, JSON checks,
  `git diff --check`, and the full default suite.

## After Action Report

Implemented on 2026-05-18.

The formal-confidence manifest now carries a structured
`fixed_point_equation_candidate` configuration field, and
`autarkic_systems.formal_confidence` loads and validates that referenced
candidate surface. Missing or invalid candidate references reject the aggregate
formal-confidence report with
`target-fixed-point-equation-candidate`, while the checked repository target
reports `fixed-point equation candidate accepted`.

The target remains truthfully blocked on `fixed-point-construction`; this ADR
only made the candidate dependency fail closed. Focused validation passed 99
tests, and live text/JSON formal-confidence reports exposed the new accepted
candidate result.
