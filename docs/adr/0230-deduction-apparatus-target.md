# ADR-0230: Deduction Apparatus Target

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0226 added the syntax-only Type-NS arithmetic language. ADR-0227 added the
first formal proof-code surface. ADR-0228 added checked capture-avoiding
substitution examples. ADR-0229 selected Level-1 consistency as the first
consistency notion to target. The formal-confidence target remains blocked on
fixed-point self-reference and deduction-apparatus selection.

The repository already has an AS-local proof-certificate checker for
transition, transition-chain, and network-sequence claims. After ADR-0186
through ADR-0200, those checked substrate certificates use `predicate-result`
steps rather than permissive manifest examples. Willard anchors still require
care: Hilbert-style, tableau, Tab-1, and GenAC self-justification claims must
not be blurred together merely because AS has local executable certificates.

## Decision

Add a checked deduction-apparatus target manifest and validator selecting the
AS-local `predicate-result` proof-certificate checker as the current apparatus
target for the existing executable substrate surfaces.

The target will validate the transition, transition-chain, and
network-sequence certificate manifests; require their proof steps to use
`predicate-result`; reference the formal codebook; require the Willard anchors
that distinguish generic configurations, Hilbert-style deduction,
self-justifying pairs, GenAC, and tableau boundary cases; and mark the target
as selected but not self-justifying.

The formal-confidence target will be narrowed again: it will point to the
deduction-apparatus target and no longer list `deduction-apparatus-selection`
as a blocker. It will remain blocked on fixed-point self-reference.

This does not implement Hilbert deduction, semantic tableaux, Tab-1, proof
search, an arithmetized proof predicate, a theorem prover, a fixed-point
sentence, a consistency theorem, runtime behavior, command semantics, evidence
bundles, or GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because the deduction-apparatus module
  and manifest do not exist.
- The manifest selects `as-local-predicate-result-proof-certificate-checker`
  and the `predicate-result` rule for the current executable substrate.
- The validator checks transition, transition-chain, and network-sequence
  proof-certificate surfaces and reports the combined rule counts.
- The validator rejects unknown Willard anchors, missing certificate surfaces,
  non-`predicate-result` proof rules, Hilbert/tableau family overclaims, and
  statuses that claim self-justification.
- Text and JSON CLI modes expose the same validation surface.
- The formal-confidence target no longer lists
  `deduction-apparatus-selection` as a blocker but remains blocked.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_deduction_apparatus_target
  tests.test_formal_confidence_target tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live deduction-apparatus text/JSON, live formal-confidence,
  live project-status summary, live handoff with `--refresh-remotes`,
  compileall, JSON checks, `git diff --check`, and the full default suite.

## After Action Report

Implemented in `claims/deduction_apparatus_targets.json` and
`autarkic_systems/deduction_apparatus.py`.

The red run failed as intended because the deduction-apparatus module and
target manifest did not exist and the formal-confidence target still listed
`deduction-apparatus-selection` as a blocker. The green focused run passed 111
tests across `tests.test_deduction_apparatus_target`,
`tests.test_formal_confidence_target`, and
`tests.test_project_status_report`.

Live text and JSON deduction-apparatus reports accepted the selected
AS-local predicate-result checker, validated transition, transition-chain, and
network-sequence certificate surfaces, and reported combined proof-rule counts
of `predicate-result=52` and `manifest-example=0`. Live formal-confidence
output removed `deduction-apparatus-selection` from the blocker list, leaving
only `self-reference-fixed-point`, and live project-status summary remained
accepted. `compileall`, JSON validation, `git diff --check`, and
`python -m unittest discover` passed; the full default suite ran 990 tests.

The target now points at `claims/deduction_apparatus_targets.json` and remains
blocked on fixed-point self-reference. This ADR deliberately leaves Hilbert
deduction, semantic tableaux, Tab-1, proof search, arithmetized proof
predicates, fixed-point self-reference, and self-consistency claims for later
ADRs.
