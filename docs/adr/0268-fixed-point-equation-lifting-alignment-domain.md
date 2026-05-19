# ADR-0268: Fixed-Point Equation Lifting Alignment Domain

Date: 2026-05-19

## Status

Accepted.

## Context

ADR-0263 decomposed the remaining fixed-point construction blocker into five
open proof cases. ADR-0264 through ADR-0267 made the first four cases depend
on finite evidence surfaces. The fifth construction case,
`fixed-point-equation-lifting`, still depends only on the fixed-point target,
fixed-point equation bridge, and codebook.

The bridge-equality alignment from ADR-0267 checks the finite equality surface
needed before a real proof can say that the direct target instance follows from
the diagonal construction. The last construction case should now fail closed
over a finite lifting-alignment surface that checks the selected `pi1`
fixed-point target context, direct target form, equation bridge, and codebook
remain aligned.

## Decision

Add `claims/fixed_point_equation_lifting_alignment.json` and
`autarkic_systems.fixed_point_equation_lifting_alignment`.

The verifier will derive one equation-lifting alignment point and check that:

- the fixed-point construction case remains `proof-case-open`;
- the construction case requires the fixed-point target, fixed-point equation
  bridge, codebook, and this alignment surface;
- the fixed-point target, equation bridge, bridge-equality alignment, and
  codebook remain accepted;
- the selected target is the current `pi1` fixed-point template over free code
  variable `n`;
- the equation bridge direct target remains closed, target-skeleton matched,
  and built by quoting the checked diagonal instance in the selected target
  context;
- the bridge-equality alignment remains route-aligned and schema-instance
  aligned; and
- the observed direct target code length stays at the checked 4528-token
  surface.

Make the `fixed-point-equation-lifting` construction case depend on this
verifier through a new `equation_lifting_alignment_path` field in
`claims/fixed_point_construction_cases.json`.

This is finite context-alignment evidence only. It does not prove the bridge
equality, fixed-point equation, arithmetized proof predicate, or
self-consistency.

## Success Criteria

- Red tests fail before implementation because the equation-lifting alignment
  verifier and manifest do not exist, the construction-case manifest has no
  `equation_lifting_alignment_path`, and the fifth construction case does not
  depend on `equation_lifting_alignment`.
- The new verifier accepts the checked equation-lifting alignment domain.
- The verifier derives one alignment point from the current fixed-point target,
  equation bridge, bridge-equality alignment, and codebook surfaces.
- Text and JSON output expose accepted status, alignment count, source-kind
  counts, direct-target length, target/context booleans, route/context
  alignment booleans, and no failed subjects.
- Stale alignment counts reject.
- Stale direct-target length facts reject.
- Missing non-claims reject.
- The construction-case validator fails closed over the new verifier and
  reports `equation_lifting_alignment` as an accepted dependency on the
  healthy path.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest
  tests.test_fixed_point_equation_lifting_alignment
  tests.test_fixed_point_construction_cases`.
- Green: the same focused suite passes after implementation.
- Regression: run live equation-lifting-alignment text/JSON, live
  construction-cases text/JSON, live formal-confidence text/JSON, live
  project-status summary, compileall, changed JSON parsing, `git diff --check`,
  adjacent fixed-point construction tests, and the full default suite.

## After Action Report

Implemented 2026-05-19.

The red focused run failed as intended:

```sh
python -m unittest tests.test_fixed_point_equation_lifting_alignment tests.test_fixed_point_construction_cases
```

It ran 12 tests in 354.635s and failed because
`autarkic_systems.fixed_point_equation_lifting_alignment` did not exist, the
construction-case manifest had no `equation_lifting_alignment_path`, and the
fifth construction case still exposed only three dependency subjects.

The green focused run passed 22 tests in 732.056s after adding the new
alignment manifest, validator, construction-case dependency, and tests.

Live validation passed:

- `python -m autarkic_systems.fixed_point_equation_lifting_alignment`;
- `python -m autarkic_systems.fixed_point_equation_lifting_alignment --format json`
  with accepted status, one alignment, direct target length 4528, matched
  target skeleton, and route alignment;
- `python -m autarkic_systems.fixed_point_construction_cases` and JSON output
  with `equation_lifting_alignment` accepted for the fifth case;
- `python -m autarkic_systems.formal_confidence` and JSON output with one
  blocked target and no failed subjects;
- `python -m autarkic_systems.project_status --format summary`, which remained
  accepted;
- `python -m compileall autarkic_systems tests`;
- `jq -e . claims/fixed_point_equation_lifting_alignment.json
  claims/fixed_point_construction_cases.json`; and
- `git diff --check`.

Adjacent fixed-point regression tests passed 111 tests in 2365.912s. The full
default suite passed 1311 tests in 8315.612s.

The resulting boundary is still finite context-alignment evidence only. The
formal-confidence target remains blocked on `fixed-point-construction`; no
bridge equality proof, fixed-point equation proof, arithmetized proof
predicate, or self-consistency theorem is claimed.
