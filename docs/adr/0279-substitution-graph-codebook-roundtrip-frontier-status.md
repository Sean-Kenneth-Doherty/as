# ADR-0279: Substitution Graph Codebook Roundtrip Frontier Status

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0254 through ADR-0261 decomposed the substitution graph correctness target
into open proof cases and finite support surfaces. ADR-0274 then summarized
the whole substitution graph correctness frontier, but the first case,
`codebook-roundtrip`, now needs its own compact handoff.

The existing codebook-roundtrip surface checks the finite graph-domain codes
currently exercised by the substitution graph formula candidate and finite
evaluation examples. That evidence is useful only if later workers can see
that the matching correctness case is still open and that the finite support
surface has not been mistaken for a proof.

## Decision

Add
`claims/substitution_graph_codebook_roundtrip_frontier_status.json` and
`autarkic_systems.substitution_graph_codebook_roundtrip_frontier_status`.

The status verifier will load the existing
`claims/substitution_graph_correctness_cases.json` case map and the existing
`claims/substitution_graph_codebook_roundtrip.json` support surface. It will
require the case with kind `codebook-roundtrip` to remain `proof-case-open`,
require that the case still depends on the correctness target, codebook, and
codebook-roundtrip support subjects, and require the roundtrip support surface
to accept over its current 12 finite subjects.

The manifest records the expected support paths for the correctness case map,
codebook-roundtrip surface, formal codebook, formula candidates, and finite
evaluation examples. The verifier checks those paths against the current
manifests so stale handoff files fail closed.

This is a compact status/frontier handoff only. It does not prove formula
correctness, substitution representability, the diagonal lemma, the
fixed-point equation, an arithmetized proof predicate, or self-consistency.

## Success Criteria

- Red tests fail before implementation because the frontier-status verifier
  and manifest do not exist.
- The checked-in manifest validates as accepted.
- The manifest points to the current substitution graph correctness case map,
  codebook-roundtrip support surface, formal codebook, formula candidates, and
  finite evaluation examples.
- The correctness case with kind `codebook-roundtrip` remains
  `proof-case-open`.
- The frontier remains `blocked` by `codebook-roundtrip`.
- The compact support layer reports the correctness case map and roundtrip
  support surface as accepted, with 12 roundtrip subjects and no failed
  subjects.
- Text and JSON output expose accepted status, frontier status/blocker, proof
  case id/kind/status, support surface count, roundtrip subject count, support
  facts, non-claims, and failed subjects.
- Proof-promotion frontier statuses reject.
- Missing or empty status non-claims reject.
- Stale dependency paths reject.
- A closed codebook-roundtrip proof case rejects.
- Case dependency drift rejects.

## Test Plan

- Red: `python -m unittest
  tests.test_substitution_graph_codebook_roundtrip_frontier_status`.
- Green: the same focused suite passes after implementation.
- Regression: run live text and JSON CLIs, parse the new JSON manifest, run
  focused unittest including `tests.test_suite_selection`, and run
  `git diff --check`.

## After Action Report

The red focused suite failed before implementation as expected:

```sh
python -m unittest tests.test_substitution_graph_codebook_roundtrip_frontier_status
```

It reported the missing ADR-0279 module before any manifest or implementation
existed:

```text
ImportError: cannot import name 'substitution_graph_codebook_roundtrip_frontier_status' from 'autarkic_systems'
```

The implementation added the compact codebook-roundtrip frontier manifest,
verifier, CLI, documentation, and focused tests. The surface keeps the
`codebook-roundtrip` correctness case open, records the existing
codebook-roundtrip support surface as accepted, checks the required support
paths, preserves the 12-subject finite roundtrip boundary, and carries
explicit non-claims including no arithmetized proof predicate.

The green and regression commands were:

```sh
python -m unittest tests.test_substitution_graph_codebook_roundtrip_frontier_status
python -m unittest tests.test_suite_selection tests.test_substitution_graph_codebook_roundtrip_frontier_status
python -m autarkic_systems.substitution_graph_codebook_roundtrip_frontier_status
python -m autarkic_systems.substitution_graph_codebook_roundtrip_frontier_status --format json | python -c 'import json,sys; p=json.load(sys.stdin); assert p["accepted"] is True; assert p["frontier_status"] == "blocked"; assert p["frontier_blocked_by"] == "codebook-roundtrip"; assert p["proof_case"]["case_kind"] == "codebook-roundtrip"; assert p["proof_case"]["status"] == "proof-case-open"; assert p["support_surface_count"] == 2; assert p["roundtrip_subject_count"] == 12; assert p["failed_subjects"] == []'
python -m json.tool claims/substitution_graph_codebook_roundtrip_frontier_status.json >/dev/null
python -m compileall autarkic_systems tests
git diff --check
```

Observed results:

- focused frontier-status suite: 14 tests passed;
- focused suite-selector plus new test: 19 tests passed;
- live text CLI: accepted, blocked by `codebook-roundtrip`, proof case
  `AS-SUBST-GRAPH-CORRECTNESS-CODEBOOK-ROUNDTRIP` remains `proof-case-open`,
  two support surfaces accepted, 12 roundtrip subjects, no failed subjects;
- live JSON CLI acceptance check passed;
- manifest JSON parsing, compileall, and diff whitespace checks passed.

This slice is only a compact frontier handoff. It does not prove formula
correctness, substitution representability, the diagonal lemma, a fixed-point
equation, an arithmetized proof predicate, or self-consistency.
