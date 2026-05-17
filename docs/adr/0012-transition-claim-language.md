# ADR-0012: Transition Claim Object Language

Date: 2026-05-17

Status: Accepted

## Context

AFS-R2 requires an object language with explicit syntax classes for terms,
formulae, sentences, proof objects, and substrate claims. AS now has transition
claims and proof certificates, but their syntax is implicit in JSON manifests
and Python loaders.

P4 asks what syntax is sufficient for the first AS claims. The smallest useful
answer is not an IS(A)-style arithmetic language yet. The current executable
surface only needs a tiny transition-claim language that classifies Universal
Cell terms, predicate formulae, transition-claim sentences, proof-certificate
objects, and substrate-claim manifests.

## Decision

Add:

- `language/transition_claim_language.json`, naming the first AS object-language
  syntax classes and allowed symbols;
- `autarkic_systems/object_language.py`, loading and validating that language;
- `docs/transition-claim-language.md`, explaining the language boundary;
- tests proving the language covers the current transition claims and proof
  certificates while rejecting missing syntax classes, unknown predicates, and
  unknown proof-object rules.

## Success Criteria

- Red tests fail before implementation because the object-language module is
  absent.
- The language manifest explicitly names the required syntax classes:
  `terms`, `formulae`, `sentences`, `proof_objects`, and `substrate_claims`.
- The current transition-claim and proof-certificate manifests validate against
  the language.
- Altered languages or claim surfaces with missing classes, unknown predicate
  symbols, or unknown proof-object rules are rejected.

## Consequences

- AS gains its first explicit object-language boundary without overclaiming an
  SJAS arithmetic language.
- Future ADRs can add IS(A) terms, formulae, proof-code syntax, and
  substitution vocabulary as new language layers.

## After Action Report

Red step:

- `python -m unittest tests.test_object_language` failed with
  `ModuleNotFoundError: No module named 'autarkic_systems.object_language'`.

Green step:

- Added `language/transition_claim_language.json`.
- Added `autarkic_systems/object_language.py`.
- Added `docs/transition-claim-language.md`.
- `python -m unittest tests.test_object_language` passed 6 tests.
- `python -m unittest discover` passed 42 tests.
- `python -m py_compile autarkic_systems/object_language.py
  tests/test_object_language.py` passed.
- `jq -e . language/transition_claim_language.json`,
  `jq -e . claims/proof_certificates.json`, and
  `jq -e . claims/transition_claims.json` passed.
- `git diff --check` passed.

Coverage limits:

- The language covers the current Universal Cell transition-claim surface only.
- It does not define IS(A), Type NS, tableaux syntax, or arithmetized proof
  codes.
