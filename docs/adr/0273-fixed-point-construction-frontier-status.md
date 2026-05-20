# ADR-0273: Fixed-Point Construction Frontier Status

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0263 through ADR-0270 turned the fixed-point construction blocker into a
finite set of open proof cases and checked support surfaces. The current stack
now names the construction cases, the diagonal-instance candidate surface, the
substitution witness bridge, the substitution graph correctness bridge, the
bridge equality alignment and evaluation, and the equation lifting alignment.

Those surfaces are individually useful, but the project still lacks one compact
frontier/status view that says what is currently supported and, equally
importantly, what remains blocked. Without that view, a later worker can read a
support surface as a promotion of the fixed-point construction rather than as a
finite prerequisite for future proof work.

## Decision

Add `claims/fixed_point_construction_frontier_status.json` and
`autarkic_systems.fixed_point_construction_frontier_status`.

The status verifier will load the existing validated fixed-point construction
surfaces:

- fixed-point construction cases;
- diagonal-instance candidate surface;
- substitution witness bridge;
- substitution graph correctness bridge;
- bridge equality alignment;
- bridge equality evaluation; and
- equation lifting alignment.

It will summarize which finite support surfaces attach to each construction
case, require all five construction cases to remain `proof-case-open`, and
preserve the aggregate blocked boundary as `fixed-point-construction`.

This is a compact frontier/status surface only. It does not prove substitution
representability, substitution graph correctness, bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.

## Success Criteria

- Red tests fail before implementation because the frontier-status verifier and
  manifest do not exist.
- The new verifier accepts the checked-in frontier-status manifest.
- The manifest names all seven current construction/frontier dependencies.
- Text and JSON output expose accepted status, blocked frontier status,
  `fixed-point-construction` as the blocker, all five open cases, per-case
  finite support, support-surface acceptance, and no failed subjects.
- Overclaiming frontier statuses such as `fixed-point-equation-proved` reject.
- Stale or missing dependency paths reject.
- Missing status non-claims reject.
- Any construction case not marked `proof-case-open` rejects.
- The fixed-point construction frontier remains blocked and no case is promoted.

## Test Plan

- Red: `python -m unittest
  tests.test_fixed_point_construction_frontier_status`.
- Green: the same focused suite passes after implementation.
- Regression: run live fixed-point-construction-frontier-status text/JSON,
  compileall, changed JSON parsing, and `git diff --check`.

## After Action Report

The red focused suite failed before implementation as expected:

```sh
python -m unittest tests.test_fixed_point_construction_frontier_status
```

It reported the missing `autarkic_systems.fixed_point_construction_frontier_status`
module before any manifest or implementation existed:

```text
ImportError: cannot import name 'fixed_point_construction_frontier_status' from 'autarkic_systems'
```

The first implementation attempted to re-run all deep support validators from
the compact frontier layer. That was stopped as too slow for this focused
status surface: a single focused validation path was terminated after 31.472
seconds, and the existing construction-case CLI was also terminated after
24.522 seconds while still running. The final implementation keeps ADR-0273 at
manifest-level frontier/status validation and leaves expensive support
derivations with their owning modules.

The green and regression commands were:

```sh
python -m unittest tests.test_fixed_point_construction_frontier_status
python -m autarkic_systems.fixed_point_construction_frontier_status
python -m autarkic_systems.fixed_point_construction_frontier_status --format json | jq -e '.accepted == true and .frontier_status == "blocked" and .frontier_blocked_by == "fixed-point-construction" and .case_count == 5 and .open_case_count == 5 and .support_surface_count == 7 and (.failed_subjects | length == 0) and all(.case_supports[].status; . == "proof-case-open")'
python -m compileall autarkic_systems tests
jq -e . claims/fixed_point_construction_frontier_status.json
git diff --check
```

Observed results:

- focused frontier-status suite: 12 tests passed;
- live text CLI: accepted, blocked by `fixed-point-construction`, five of five
  cases open, seven support surfaces present, no failed subjects;
- live JSON CLI acceptance check: passed;
- compileall, JSON parsing, and diff whitespace checks passed.

This slice adds a compact frontier handoff only. It does not prove
substitution representability, substitution graph correctness, bridge equality,
a fixed-point equation, an arithmetized proof predicate, or self-consistency.
