# ADR-0274: Substitution Graph Correctness Frontier Status

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0254 through ADR-0261 decomposed the substitution graph correctness target
into five open proof cases and added finite support surfaces for the current
graph-domain evidence. The case stack now names codebook roundtrip, quotation
term closure, meta-substitution semantics, formula schema relation, and
diagonal witness composition as checked support for future correctness proof
work.

Those surfaces are useful only if their boundary remains explicit. A later
worker needs a compact status view saying that the substitution graph
correctness frontier is still blocked, even though the current finite support
surfaces are present and parseable.

## Decision

Add `claims/substitution_graph_correctness_frontier_status.json` and
`autarkic_systems.substitution_graph_correctness_frontier_status`.

The status verifier will load the existing
`claims/substitution_graph_correctness_cases.json` manifest, observe its five
open proof cases, and summarize the current support subjects named there:

- correctness target;
- formal codebook;
- quotation term support;
- formal substitution support;
- formula candidate support;
- substitution representability support;
- codebook roundtrip;
- quotation term closure;
- meta-substitution semantics;
- formula schema relation; and
- diagonal witness composition.

This is a compact frontier/status surface only. It does not run expensive deep
derivations and does not promote the substitution graph correctness target,
formula schema, substitution witness, diagonal witness, fixed-point equation,
or self-consistency theorem.

## Success Criteria

- Red tests fail before implementation because the frontier-status verifier and
  manifest do not exist.
- The new verifier accepts the checked-in frontier-status manifest.
- The verifier observes exactly five substitution graph correctness cases and
  requires all five to remain `proof-case-open`.
- The aggregate frontier remains `blocked` by `substitution-graph-correctness`.
- Text and JSON output expose accepted status, blocked frontier status,
  blocker, case count, open-case count, support-surface count, per-case support
  summaries, and failed subjects.
- Overclaiming frontier statuses and proof-promotion case statuses reject.
- Missing support paths, missing non-claims, and empty non-claim entries reject.
- The layer stays compact and avoids deep proof/support derivations.

## Test Plan

- Red: `python -m unittest
  tests.test_substitution_graph_correctness_frontier_status`.
- Green: the same focused suite passes after implementation.
- Regression: run live substitution-graph-correctness-frontier-status
  text/JSON, compileall, changed JSON parsing, and `git diff --check`.

## After Action Report

The red focused suite failed before implementation as expected:

```sh
python -m unittest tests.test_substitution_graph_correctness_frontier_status
```

It reported the missing
`autarkic_systems.substitution_graph_correctness_frontier_status` module before
any manifest or implementation existed:

```text
ImportError: cannot import name 'substitution_graph_correctness_frontier_status' from 'autarkic_systems'
```

The implementation keeps the status surface compact. It loads the existing
correctness-case manifest, parses referenced support artifacts, and validates
IDs, open case statuses, per-case support mapping, and non-claims without
running the deeper support derivations owned by the existing modules.

The green and regression commands were:

```sh
python -m unittest tests.test_substitution_graph_correctness_frontier_status
python -m autarkic_systems.substitution_graph_correctness_frontier_status
python -m autarkic_systems.substitution_graph_correctness_frontier_status --format json | jq -e '.accepted == true and .frontier_status == "blocked" and .frontier_blocked_by == "substitution-graph-correctness" and .case_count == 5 and .open_case_count == 5 and .support_surface_count == 11 and (.failed_subjects | length == 0) and all(.case_supports[].status; . == "proof-case-open")'
jq -e . claims/substitution_graph_correctness_frontier_status.json
python -m compileall autarkic_systems tests
git diff --check
```

Observed results:

- focused frontier-status suite: 13 tests passed;
- live text CLI: accepted, blocked by `substitution-graph-correctness`, five of
  five cases open, eleven support surfaces present, no failed subjects;
- live JSON CLI acceptance check: passed;
- changed JSON parsing, compileall, and diff whitespace checks passed.

`python -m autarkic_systems.test_suite_selection --suite fast --list | rg
"test_substitution_graph_correctness_frontier_status|unclassified|extended-fixed-point"`
also confirmed that the new substitution-graph status test is covered by the
fast discovered suite boundary.

This slice adds a compact frontier handoff only. It does not prove formula
correctness, substitution representability, the diagonal lemma, a fixed-point
equation, an arithmetized proof predicate, or self-consistency.
