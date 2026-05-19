# ADR-0264: Fixed-Point Diagonal Instance Closure Domain

Date: 2026-05-19

## Status

Accepted.

## Context

ADR-0263 decomposed the remaining `fixed-point-construction` blocker into five
open proof cases. The first case, `diagonal-instance-closure`, currently
depends on the broad fixed-point target, diagonal-construction target, and
fixed-point equation bridge target.

That is too coarse for the first case. The project needs a checked finite
artifact proving that the current diagonal instance is closed, codebook-stable,
and aligned with the fixed-point target and bridge surfaces before later work
tries to discharge representability, bridge equality, or equation lifting.

## Decision

Add `claims/fixed_point_diagonal_instance_closure.json` and
`autarkic_systems.fixed_point_diagonal_instance_closure`.

The verifier will derive the current diagonal instance from the checked
fixed-point target, diagonal-construction target, codebook, and bridge target.
It will check that the derived instance:

- is the expected closed diagonal instance for
  `AS-FIXED-POINT-SELFCONS1-TARGET`;
- round-trips through the checked formal codebook;
- preserves the selected fixed-point target skeleton;
- places `substitution_code(quote(seed), quote(seed))` in the target slot; and
- matches the diagonal instance recorded by the bridge target.

Make the `diagonal-instance-closure` construction case depend on this verifier
through a new `diagonal_instance_closure_path` field in
`claims/fixed_point_construction_cases.json`.

This is finite closure evidence only. It does not prove substitution
representability, substitution graph correctness, bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.

## Success Criteria

- Red tests fail before implementation because the closure verifier and
  manifest do not exist, the construction-case manifest has no
  `diagonal_instance_closure_path`, and the first construction case does not
  depend on `diagonal_instance_closure`.
- The new verifier accepts the checked diagonal-instance closure domain.
- The verifier derives one closure point from the current target,
  construction, and bridge surfaces.
- Text and JSON output expose accepted closure status, closure count,
  source-kind counts, closure booleans, and no failed subjects.
- Stale closure counts reject.
- Stale diagonal-instance length facts reject.
- Missing non-claims reject.
- The construction-case validator fails closed over the new verifier and
  reports `diagonal_instance_closure` as an accepted dependency on the healthy
  path.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest
  tests.test_fixed_point_diagonal_instance_closure
  tests.test_fixed_point_construction_cases`.
- Green: the same focused suite passes after implementation.
- Regression: run live diagonal-instance-closure text/JSON, live
  construction-cases text/JSON, live formal-confidence text/JSON, live
  project-status summary, compileall, changed JSON parsing, `git diff --check`,
  adjacent fixed-point construction tests, and the full default suite.

## After Action Report

Completed on 2026-05-19.

The red suite failed before implementation as expected:

```sh
python -m unittest tests.test_fixed_point_diagonal_instance_closure tests.test_fixed_point_construction_cases
```

It reported the missing diagonal-instance closure module and manifest, the
missing `diagonal_instance_closure_path` field in the construction-case
manifest, the missing accepted `diagonal_instance_closure` result, and the old
three-dependency count for the first construction case.

The implementation added the closure manifest and verifier, wired the verifier
into the `diagonal-instance-closure` construction case, and preserved that case
as `proof-case-open`. The green and regression commands were:

```sh
python -m unittest tests.test_fixed_point_diagonal_instance_closure tests.test_fixed_point_construction_cases
python -m autarkic_systems.fixed_point_diagonal_instance_closure
python -m autarkic_systems.fixed_point_diagonal_instance_closure --format json | jq -e '.accepted == true and .closure_count == 1 and (.failed_subjects | length == 0) and .closures[0].observed_diagonal_instance_closed == true and .closures[0].observed_codebook_roundtrip == true'
python -m autarkic_systems.fixed_point_construction_cases --format json | jq -e '.accepted == true and .case_count == 5 and (.failed_subjects | length == 0) and (.results[] | select(.subject == "diagonal_instance_closure") | .accepted) == true'
python -m autarkic_systems.formal_confidence --format json | jq -e '.accepted == true and .target_count == 1 and (.failed_subjects | length == 0) and ([.targets[].status] == ["blocked"])'
python -m autarkic_systems.project_status --format summary
python -m compileall autarkic_systems tests
jq -e . claims/fixed_point_diagonal_instance_closure.json claims/fixed_point_construction_cases.json >/dev/null
git diff --check
python -m unittest tests.test_fixed_point_diagonal_instance_closure tests.test_fixed_point_construction_cases tests.test_fixed_point_equation_bridge tests.test_diagonal_construction tests.test_fixed_point_target tests.test_formal_confidence_target
python -m unittest discover
```

Observed results:

- focused diagonal-instance-closure/construction-cases suite: 22 tests passed;
- live diagonal-instance-closure text/JSON: accepted, one closure point, no
  failed subjects;
- live construction-cases JSON: accepted, first case now requires accepted
  `diagonal_instance_closure`;
- live formal-confidence JSON: accepted, one blocked target;
- live project-status summary: accepted, one blocked formal-confidence target,
  safe next slice `none`;
- compileall, changed JSON parsing, and diff whitespace checks passed;
- adjacent fixed-point construction suite: 80 tests passed; and
- full default suite: 1,267 tests passed.

This slice proves only finite closure/alignment facts for the current diagonal
instance. It does not prove substitution representability, substitution graph
correctness, bridge equality, a fixed-point equation, an arithmetized proof
predicate, or self-consistency.
