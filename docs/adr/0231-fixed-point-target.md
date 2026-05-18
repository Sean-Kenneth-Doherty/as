# ADR-0231: Fixed-Point Target Surface

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0228 added capture-avoiding substitution examples over the formal
codebook. ADR-0229 selected Level-1 consistency as the first consistency
target. ADR-0230 selected the AS-local `predicate-result` proof-certificate
checker as the current deduction-apparatus target. The formal-confidence
target remains blocked on fixed-point self-reference.

The next useful step is still not a diagonal lemma or self-consistency theorem.
It is to make the fixed-point target itself explicit, check that its template
uses the existing formal codebook and substitution machinery, and prevent
agents from treating a target template as a constructed fixed point.

## Decision

Add a checked fixed-point target manifest and validator. The target will name
a `pi1` template with a free code variable, validate the substitution instance
against the existing codebook and capture-avoiding substitution engine, require
Willard SelfCons/Level(k)/GenAC anchors, and mark the target as
`target-selected-not-constructed`.

The formal-confidence target will be narrowed again: it will point to the new
fixed-point target and no longer use the broad `self-reference-fixed-point`
blocker. It will remain blocked on the more concrete
`fixed-point-construction` obligation.

This does not implement a diagonal lemma, quotation-term construction,
arithmetized proof predicate, fixed-point equation proof, consistency theorem,
runtime behavior, command semantics, evidence bundles, or GitHub submission
logic.

## Success Criteria

- Red tests fail before implementation because the fixed-point module and
  manifest do not exist.
- The manifest references the checked formal codebook, substitution examples,
  consistency-level target, and deduction-apparatus target.
- The validator checks a `pi1` template with a free code variable and validates
  an explicit substitution instance against expected node and code output.
- The validator rejects unknown Willard anchors, templates missing the target
  variable, expected-instance mismatches, and statuses that claim a fixed point
  has been proved.
- Text and JSON CLI modes expose the same validation surface.
- The formal-confidence target points at the fixed-point target and remains
  blocked on `fixed-point-construction`.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_fixed_point_target
  tests.test_formal_confidence_target tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live fixed-point text/JSON, live formal-confidence, live
  project-status summary, live handoff with `--refresh-remotes`, compileall,
  JSON checks, `git diff --check`, and the full default suite.

## After Action Report

Implemented in `claims/fixed_point_targets.json` and
`autarkic_systems/fixed_point.py`.

The red run failed as intended because the fixed-point module and target
manifest did not exist and the formal-confidence target still pointed at the
older broad `self-reference-fixed-point` blocker. The green focused run passed
110 tests across `tests.test_fixed_point_target`,
`tests.test_formal_confidence_target`, and
`tests.test_project_status_report`.

Live text and JSON fixed-point reports accepted the selected `pi1` template,
validated the free code variable `n`, checked the substitution instance
against expected node and code output, and reported no failed subjects. Live
formal-confidence output now points at `claims/fixed_point_targets.json` and
reports `fixed-point-construction` as the remaining blocker; live
project-status summary remained accepted. `compileall`, JSON validation,
`git diff --check`, and `python -m unittest discover` passed; the full default
suite ran 1002 tests.

The target now points at `claims/fixed_point_targets.json` and remains blocked
on fixed-point construction. This ADR deliberately leaves real quotation-term
construction, diagonal-lemma proof, fixed-point equation proof, arithmetized
proof predicates, and self-consistency claims for later ADRs.
