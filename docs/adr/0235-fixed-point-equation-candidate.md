# ADR-0235: Fixed-Point Equation Candidate

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0234 added a checked quotation-term surface. The next temptation would be
to call substitution with that term a fixed point. That would be false: a
naive term substitution is only a candidate unless the encoded result is shown
to satisfy the intended fixed-point equation.

The useful next step is therefore not a theorem claim. It is a checked
candidate surface that constructs the naive quotation-term substitution,
computes its code, and records whether it is actually fixed.

## Decision

Add `claims/fixed_point_equation_candidates.json` and
`autarkic_systems.fixed_point_equation`. The module will load the current
fixed-point target and quotation-term example, substitute the checked
quotation term into the target template, encode the resulting candidate, and
verify the manifest's recorded outcome.

For this slice, the expected outcome is `candidate-not-fixed`: the constructed
candidate code is longer than and different from the originally quoted target
instance code. That is useful negative evidence. It shows that AS now has the
plumbing to test candidate equations while preserving the remaining need for a
real diagonal construction.

This does not implement a diagonal lemma, an equality proof between a sentence
and its quoted instance, arithmetic sequence axioms, an arithmetized proof
predicate, a self-consistency theorem, runtime behavior, command semantics,
evidence bundles, or GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because the fixed-point-equation module
  and manifest do not exist.
- The candidate manifest references the fixed-point target, quotation-term
  examples, and codebook manifests.
- The validator constructs the naive quotation substitution for
  `AS-FIXED-POINT-SELFCONS1-TARGET`, encodes it, and checks its length,
  prefix, and mismatch with the originally quoted target code.
- The validator rejects unknown target IDs, unknown quotation-term example
  IDs, proved-equation statuses, and stale expected candidate lengths.
- Text and JSON CLI modes expose the same candidate surface.
- The formal-confidence metadata names the checked candidate surface while
  preserving the `fixed-point-construction` blocker.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_fixed_point_equation_candidate
  tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live fixed-point-equation text/JSON, live fixed-point, live
  formal-confidence JSON, live project-status summary, live handoff with
  `--refresh-remotes`, compileall, JSON checks, `git diff --check`, and the
  full default suite.

## After Action Report

Implemented. The red focused run failed before implementation because
`autarkic_systems.fixed_point_equation` and
`claims/fixed_point_equation_candidates.json` did not exist.

The implementation added the fixed-point equation candidate manifest and
validator. The validator loads the current fixed-point target, quotation-term
examples, and formal codebook; substitutes the checked quotation term into the
target template; encodes the naive candidate; and verifies that the observed
candidate is not fixed. During implementation, this exposed a real integration
gap: the formal substitution layer did not yet treat `sequence_nil` and
`sequence_cons` as term nodes. ADR-0235 therefore also extends substitution to
handle those sequence terms.

Focused green evidence:

```sh
python -m unittest tests.test_fixed_point_equation_candidate tests.test_formal_substitution tests.test_project_status_report
# Ran 117 tests in 11.705s - OK
```

Live evidence:

```sh
python -m autarkic_systems.fixed_point_equation
# Fixed-point equation candidates: accepted; candidate-not-fixed; code length 121
python -m autarkic_systems.fixed_point_equation --format json
# accepted true; candidate_is_fixed false; observed_candidate_code_length 121
python -m autarkic_systems.formal_confidence --format json
# accepted true; failed_subjects []
python -m autarkic_systems.project_status --format summary
# Autarkic Systems summary: accepted; Formal confidence: 1 target; blocked=1
```

Regression evidence:

```sh
python -m compileall autarkic_systems tests
jq -e . claims/fixed_point_equation_candidates.json
jq -e . claims/fixed_point_targets.json
git diff --check
python -m unittest discover
# Ran 1055 tests in 19.899s - OK
```

The remaining boundary is unchanged in substance but sharper: AS can now build
and reject the naive candidate, but it still has no diagonal lemma proof,
fixed-point equation proof, arithmetized proof predicate, or self-consistency
theorem.
