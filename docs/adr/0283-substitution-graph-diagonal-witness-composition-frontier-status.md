# ADR-0283: Substitution Graph Diagonal Witness Composition Frontier Status

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0254 decomposed substitution graph correctness into open proof cases.
ADR-0261 then added a finite support surface for the
`diagonal-witness-composition` case, and ADR-0274 summarized the aggregate
substitution graph correctness frontier.

The `diagonal-witness-composition` case now needs its own compact handoff. A
future worker should be able to see that the finite composition support
surface still validates, the matching correctness case remains open, and the
frontier is still a proof obligation rather than a proved diagonal,
representability, fixed-point, or self-consistency claim.

## Decision

Add
`claims/substitution_graph_diagonal_witness_composition_frontier_status.json`
and
`autarkic_systems.substitution_graph_diagonal_witness_composition_frontier_status`.

The status verifier will load the existing
`claims/substitution_graph_correctness_cases.json` manifest, locate the single
`diagonal-witness-composition` case, and require that case to remain
`proof-case-open`. It will also load
`claims/substitution_graph_diagonal_witness_composition.json`, run the
existing diagonal-witness-composition validator, require no failed subjects,
and report the finite support facts needed for handoff: one composition
subject, the `diagonal-witness` source kind, and the current dependency paths.

The manifest records the expected support paths for the correctness case map,
the diagonal-witness-composition support surface, the formal language,
codebook, correctness target, formula candidate, formula-schema relation,
substitution-representability target, diagonal-construction target, and
fixed-point target. The verifier checks those paths so stale handoff files
fail closed.

This is a compact frontier/status surface only. It does not promote the
`diagonal-witness-composition` case and does not claim formula correctness,
substitution representability, the diagonal lemma, a fixed-point equation
proof, an arithmetized proof predicate, or self-consistency.

## Success Criteria

- Red tests fail before implementation because the frontier-status verifier
  and manifest do not exist.
- The new verifier accepts the checked-in frontier-status manifest.
- The manifest points to the current substitution graph correctness case map
  and diagonal-witness-composition support manifest.
- The matching correctness case has case kind `diagonal-witness-composition`
  and remains `proof-case-open`.
- The frontier remains `blocked` by `diagonal-witness-composition`.
- The case support subjects are exactly correctness target, substitution
  representability, and diagonal witness composition.
- The diagonal-witness-composition support surface validates with no failed
  subjects and one composition subject.
- Text and JSON output expose accepted status, frontier status/blocker, the
  case id/kind/status, support surface count, support facts, non-claims, and
  failed subjects.
- Proof-promotion statuses reject.
- Missing or empty status non-claims reject.
- Stale dependency paths reject.
- A closed diagonal-witness-composition case rejects.
- Case dependency drift rejects.

## Test Plan

- Red: `python -m unittest
  tests.test_substitution_graph_diagonal_witness_composition_frontier_status`.
- Green: the same focused suite passes after implementation.
- Regression: run the focused suite together with
  `tests.test_suite_selection`, parse the new JSON manifest, run the live text
  and JSON CLIs, and run `git diff --check`.

## After Action Report

The red focused suite failed before implementation as expected:

```sh
python -m unittest tests.test_substitution_graph_diagonal_witness_composition_frontier_status
```

It reported the missing ADR-0283 module before any manifest or implementation
existed:

```text
ImportError: cannot import name 'substitution_graph_diagonal_witness_composition_frontier_status' from 'autarkic_systems'
```

The implementation added the compact diagonal-witness-composition frontier
manifest, verifier, CLI, documentation, and focused tests. The surface loads
the existing substitution graph correctness case map, requires
`AS-SUBST-GRAPH-CORRECTNESS-DIAGONAL-WITNESS-COMPOSITION` to remain
`proof-case-open`, runs the existing diagonal-witness-composition support
validator, and reports the finite composition support as accepted with one
composition subject and no failed subjects.

The green and regression commands were:

```sh
python -m unittest tests.test_substitution_graph_diagonal_witness_composition_frontier_status
python -m unittest tests.test_suite_selection tests.test_substitution_graph_diagonal_witness_composition_frontier_status
python -m json.tool claims/substitution_graph_diagonal_witness_composition_frontier_status.json >/dev/null
python -m autarkic_systems.substitution_graph_diagonal_witness_composition_frontier_status
python -m autarkic_systems.substitution_graph_diagonal_witness_composition_frontier_status --format json
python -m autarkic_systems.substitution_graph_diagonal_witness_composition_frontier_status --format json | python -c 'import json,sys; p=json.load(sys.stdin); assert p["accepted"] is True; assert p["frontier_status"] == "blocked"; assert p["frontier_blocked_by"] == "diagonal-witness-composition"; assert p["proof_case"]["case_kind"] == "diagonal-witness-composition"; assert p["proof_case"]["status"] == "proof-case-open"; assert p["support_surface_count"] == 2; assert p["composition_count"] == 1; assert p["failed_subjects"] == []'
python -m compileall autarkic_systems tests
git diff --check
```

Observed results:

- focused frontier-status suite: 15 tests passed;
- focused suite plus suite-selection check: 20 tests passed;
- manifest JSON parsing passed;
- live text CLI: accepted, blocked by `diagonal-witness-composition`,
  `AS-SUBST-GRAPH-CORRECTNESS-DIAGONAL-WITNESS-COMPOSITION` remained
  `proof-case-open`, two support surfaces accepted, one composition subject,
  and no failed subjects;
- live JSON CLI acceptance check passed;
- compileall and diff whitespace checks passed.

This slice adds a compact frontier handoff only. It does not prove formula
correctness, substitution representability, the diagonal lemma, a fixed-point
equation, an arithmetized proof predicate, or self-consistency.
