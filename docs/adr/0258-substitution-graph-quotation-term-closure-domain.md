# ADR-0258: Substitution Graph Quotation Term Closure Domain

Date: 2026-05-19

## Status

Accepted.

## Context

ADR-0254 decomposed substitution graph correctness into open proof cases.
ADR-0257 made the first case depend on finite codebook roundtrip evidence for
the graph-domain codes currently exercised by the formula candidate and finite
evaluation examples.

The second case requires confidence that graph-domain code sequences quote into
the nested `sequence_cons` / `sequence_nil` term shape used by the substitution
graph evaluator. Existing quotation-term examples prove that the helper works
for two fixed examples, but they do not derive the graph-domain subject set.

## Decision

Add `claims/substitution_graph_quotation_term_closure.json` and
`autarkic_systems.substitution_graph_quotation_term_closure`.

The verifier derives the same finite graph-domain code subjects as ADR-0257,
quotes each subject with the checked quotation-term helper, and verifies that
the result is closed, has the expected token count, recovers the original
tokens, and round-trips through the formal codebook.

Make the `quotation-term-closure` correctness case depend on this verifier via
a new `quotation_term_closure_path` field in
`claims/substitution_graph_correctness_cases.json`.

This is finite closure evidence only. It does not prove formula correctness,
substitution representability, the diagonal lemma, a fixed-point equation, or
self-consistency.

## Success Criteria

- Red tests fail before implementation because the quotation-term closure
  verifier and manifest do not exist, the correctness-case manifest has no
  `quotation_term_closure_path`, and the second case does not depend on
  `quotation_term_closure`.
- The new verifier accepts the checked graph-domain subject set.
- The verifier derives 12 code subjects from the formula candidate and finite
  evaluation surfaces.
- Text and JSON output expose accepted closure status, subject counts, source
  kind counts, and no closure failures.
- Stale subject counts reject the verifier.
- The correctness-case validator fails closed over the new verifier and reports
  `quotation_term_closure` as an accepted dependency on the healthy path.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_substitution_graph_quotation_term_closure
  tests.test_substitution_graph_correctness_cases`.
- Green: the same focused suite passes after implementation.
- Regression: run live quotation-term-closure text/JSON, live
  correctness-cases text/JSON, live formal-confidence text, live
  project-status summary, compileall, `git diff --check`, and the full default
  suite.

## After Action Report

Implemented in `claims/substitution_graph_quotation_term_closure.json` and
`autarkic_systems/substitution_graph_quotation_term_closure.py`.

The red run failed for the intended reasons: the closure module and manifest
were absent, `SubstitutionGraphCorrectnessCaseManifest` had no
`quotation_term_closure_path`, and the `quotation-term-closure` case did not
list the new dependency.

The first green implementation exposed an additional useful fact: the checked
formula-candidate witness instance quotes a 4,815-token code sequence, deep
enough to exceed Python's default recursion limit in the existing recursive
formal encoder. The final verifier keeps the existing shared encoder intact,
raises recursion depth locally for this finite deep-term check, and recovers
quotation tokens iteratively.

Focused validation passed:

```sh
python -m unittest tests.test_substitution_graph_quotation_term_closure tests.test_substitution_graph_correctness_cases
python -m unittest tests.test_substitution_graph_codebook_roundtrip
```

This adds finite closure evidence for the second correctness case. It still
does not prove formula correctness, substitution representability, the
diagonal lemma, a fixed-point equation, or self-consistency.
