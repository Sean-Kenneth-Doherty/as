# ADR-0282: Substitution Graph Formula Schema Relation Frontier Status

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0254 decomposed substitution graph correctness into open proof cases.
ADR-0260 then added finite formula-schema relation evidence for the
`formula-schema-relation` case, and ADR-0274 summarized the aggregate
substitution graph correctness frontier.

The formula-schema-relation case now needs its own compact handoff. A later
worker should be able to see that the finite support surface validates, that
the matching correctness case remains open, and that the next frontier is a
general formula-correctness proof rather than a proved case.

## Decision

Add
`claims/substitution_graph_formula_schema_relation_frontier_status.json` and
`autarkic_systems.substitution_graph_formula_schema_relation_frontier_status`.

The status verifier will load the existing
`claims/substitution_graph_correctness_cases.json` manifest, locate the single
`formula-schema-relation` case, and require that case to remain
`proof-case-open`. It will also load
`claims/substitution_graph_formula_schema_relation.json`, run the existing
formula-schema relation validator, require no failed subjects, and report the
finite support facts needed for handoff: four relation points, the
witness-instance / finite-evaluation source-kind split, and the current
formula candidate, graph target, evaluation, codebook, formal-language, and
substitution-witness support paths.

This is a compact frontier/status surface only. It does not promote the
formula-schema-relation case and does not claim formula correctness,
substitution representability, the diagonal lemma, a fixed-point equation, an
arithmetized proof predicate, or self-consistency.

## Success Criteria

- Red tests fail before implementation because the frontier-status verifier
  and manifest do not exist.
- The new verifier accepts the checked-in frontier-status manifest.
- The manifest points to the current substitution graph correctness case map
  and formula-schema-relation support manifest.
- The matching correctness case has case kind `formula-schema-relation` and
  remains `proof-case-open`.
- The frontier remains `blocked` by `formula-schema-relation`.
- The case support subjects are exactly correctness target, formula candidate,
  and formula schema relation.
- The formula-schema-relation support surface validates with no failed
  subjects and four relation points.
- Text and JSON output expose accepted status, frontier status/blocker, the
  case id/kind/status, support-surface count, support facts, and failed
  subjects.
- Proof-promotion statuses reject.
- Missing or empty status non-claims reject.
- Stale dependency paths reject.
- A closed formula-schema-relation case rejects.

## Test Plan

- Red: `python -m unittest
  tests.test_substitution_graph_formula_schema_relation_frontier_status`.
- Green: the same focused suite passes after implementation.
- Regression: run the focused suite together with
  `tests.test_suite_selection`, parse the new JSON manifest, run the live text
  and JSON CLIs, and run `git diff --check`.

## After Action Report

The red focused suite failed before implementation as expected:

```sh
python -m unittest tests.test_substitution_graph_formula_schema_relation_frontier_status
```

It reported the missing ADR-0282 module before any manifest or implementation
existed:

```text
ImportError: cannot import name 'substitution_graph_formula_schema_relation_frontier_status' from 'autarkic_systems'
```

The implementation added the compact formula-schema-relation frontier
manifest, verifier, CLI, documentation, and focused tests. The surface loads
the existing substitution graph correctness case map, requires
`AS-SUBST-GRAPH-CORRECTNESS-FORMULA-SCHEMA-RELATION` to remain
`proof-case-open`, runs the existing formula-schema-relation support
validator, and reports the finite relation support as accepted with four
relation points and no failed subjects.

The green and regression commands were:

```sh
python -m unittest tests.test_substitution_graph_formula_schema_relation_frontier_status
python -m unittest tests.test_suite_selection tests.test_substitution_graph_formula_schema_relation_frontier_status
python -c 'import json; from pathlib import Path; json.loads(Path("claims/substitution_graph_formula_schema_relation_frontier_status.json").read_text(encoding="utf-8"))'
python -m autarkic_systems.substitution_graph_formula_schema_relation_frontier_status
python -c 'import json, subprocess, sys; completed = subprocess.run([sys.executable, "-m", "autarkic_systems.substitution_graph_formula_schema_relation_frontier_status", "--format", "json"], check=False, capture_output=True, text=True); payload = json.loads(completed.stdout); assert completed.returncode == 0, completed.stderr; assert payload["accepted"] is True; assert payload["frontier_status"] == "blocked"; assert payload["frontier_blocked_by"] == "formula-schema-relation"; assert payload["case"]["case_kind"] == "formula-schema-relation"; assert payload["case"]["status"] == "proof-case-open"; assert payload["support_surface_count"] == 1; assert payload["support_facts"]["formula_schema_relation"]["relation_point_count"] == 4; assert payload["failed_subjects"] == []'
python -m compileall autarkic_systems tests
git diff --check
```

Observed results:

- focused frontier-status suite: 14 tests passed;
- focused suite plus suite-selection check: 19 tests passed;
- manifest JSON parsing passed;
- live text CLI: accepted, blocked by `formula-schema-relation`,
  `AS-SUBST-GRAPH-CORRECTNESS-FORMULA-SCHEMA-RELATION` remained
  `proof-case-open`, one support surface accepted, four relation points, and
  no failed subjects;
- live JSON CLI acceptance check passed with `accepted: true`,
  `frontier_status: blocked`, one support surface, four relation points, and
  an empty `failed_subjects` list;
- compileall and diff whitespace checks passed.

This slice adds a compact frontier handoff only. It does not prove formula
correctness, substitution representability, the diagonal lemma, a fixed-point
equation, an arithmetized proof predicate, or self-consistency.
