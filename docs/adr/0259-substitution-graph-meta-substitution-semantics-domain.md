# ADR-0259: Substitution Graph Meta-Substitution Semantics Domain

Date: 2026-05-19

## Status

Accepted.

## Context

ADR-0254 decomposed substitution graph correctness into five open proof cases.
ADR-0257 and ADR-0258 gave the first two cases finite executable evidence:
codebook roundtrip over the graph-domain codes and quotation-term closure over
those same codes.

The third case, `meta-substitution-semantics`, still depends only on the
general checked formal-substitution example surface. That surface is useful,
but it does not explicitly name the substitution operations actually performed
by the current substitution graph formula candidate and finite evaluator.

## Decision

Add `claims/substitution_graph_meta_substitution_semantics.json` and
`autarkic_systems.substitution_graph_meta_substitution_semantics`.

The verifier will derive the concrete meta-level substitutions currently used
by the substitution graph stack:

- the three graph-variable substitutions that close the formula candidate
  witness instance; and
- the three finite-evaluation substitutions over current example formulae.

For each subject, it checks that the replacement quotation term is closed, the
output free-variable set follows the expected closed-replacement rule, the
observed output agrees with the existing expected surface when such a surface
exists, and substitutions for variables not free in the input behave as
no-ops.

Make the `meta-substitution-semantics` correctness case depend on this
verifier via a new `meta_substitution_semantics_path` field in
`claims/substitution_graph_correctness_cases.json`.

This is finite semantic evidence only. It does not prove general
capture-avoiding substitution correctness, formula correctness, substitution
representability, the diagonal lemma, a fixed-point equation, or
self-consistency.

## Success Criteria

- Red tests fail before implementation because the meta-substitution semantics
  verifier and manifest do not exist, the correctness-case manifest has no
  `meta_substitution_semantics_path`, and the third case does not depend on
  `meta_substitution_semantics`.
- The new verifier accepts the checked finite substitution subject set.
- The verifier derives 6 substitution subjects: three formula-candidate
  graph-variable substitutions and three finite-evaluation substitutions.
- Text and JSON output expose accepted semantic status, subject counts,
  source-kind counts, and no semantic failures.
- Stale subject counts reject the verifier.
- The correctness-case validator fails closed over the new verifier and
  reports `meta_substitution_semantics` as an accepted dependency on the
  healthy path.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_substitution_graph_meta_substitution_semantics
  tests.test_substitution_graph_correctness_cases`.
- Green: the same focused suite passes after implementation.
- Regression: run live meta-substitution-semantics text/JSON, live
  correctness-cases text/JSON, live formal-confidence text, live
  project-status summary, compileall, `git diff --check`, and the full default
  suite.

## After Action Report

Implemented in `claims/substitution_graph_meta_substitution_semantics.json`
and `autarkic_systems/substitution_graph_meta_substitution_semantics.py`.

The red run failed for the intended reasons: the verifier module and manifest
were absent, `SubstitutionGraphCorrectnessCaseManifest` had no
`meta_substitution_semantics_path`, and the `meta-substitution-semantics` case
still listed only `correctness_target` and `formal_substitution`.

The finished verifier derives 6 subjects: three graph-variable substitutions
from the formula candidate witness instance and three substitutions from the
finite evaluation examples. It checks closed replacement quotation terms,
free-variable preservation under closed replacement, no-op behavior for the
not-free example, and agreement with existing expected formula/evaluation
surfaces. The correctness-case validator now reports
`meta_substitution_semantics` as an accepted dependency for the third open
case.

Validation passed:

```sh
python -m unittest tests.test_substitution_graph_meta_substitution_semantics tests.test_substitution_graph_correctness_cases
python -m unittest tests.test_substitution_graph_meta_substitution_semantics tests.test_substitution_graph_correctness_cases tests.test_substitution_graph_codebook_roundtrip tests.test_substitution_graph_quotation_term_closure
python -m autarkic_systems.substitution_graph_meta_substitution_semantics
python -m autarkic_systems.substitution_graph_meta_substitution_semantics --format json
python -m autarkic_systems.substitution_graph_correctness_cases --format json
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.project_status --format summary
python -m compileall autarkic_systems tests
git diff --check
python -m unittest discover
```

The full default suite passed 1,212 tests in 370.497s. This adds finite
semantic evidence for the third correctness case. It still does not prove
general capture-avoiding substitution correctness, formula correctness,
substitution representability, the diagonal lemma, a fixed-point equation, or
self-consistency.
