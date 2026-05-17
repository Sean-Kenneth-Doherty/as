# Transition Claim Language

Status: ADR-0012 object-language note, 2026-05-17.

## Purpose

`language/transition_claim_language.json` names the first explicit AS object
language. It is deliberately small: it covers the Universal Cell transition
claims that AS can currently execute, not the full IS(A) or SJAS arithmetic
language.

The point is to stop relying on implicit Python/JSON shape as the only syntax
boundary. Current claims can now be checked against named syntax classes before
later proof or self-reference work builds on them.

## Syntax Classes

| Class | Current meaning |
| --- | --- |
| `terms` | Universal Cell term vocabulary: roles, memory values, signals, automail commands, statuses, and cell fields. |
| `formulae` | Predicate applications of the form `predicate(before_cell, step_result)`. |
| `sentences` | Transition-claim sentences named by claim IDs such as `UC-FIXED-OUTPUT-PRESERVED`. |
| `proof_objects` | Proof-certificate steps. The only current rule is `manifest-example`. |
| `substrate_claims` | Paths to the transition-claim and proof-certificate manifests. |

## Verification

Fast validation is covered by:

```sh
python -m unittest tests.test_object_language
```

The validator checks:

- the language manifest names all required syntax classes;
- language term sets match the Universal Cell implementation vocabulary;
- formula predicate symbols correspond to implemented predicate functions;
- current transition claims fit the language;
- current proof certificates use known proof-object rules;
- deliberately missing classes, unknown predicates, unknown proof rules, and
  incomplete term vocabularies are rejected.

## Non-Goals

- This is not the full AS formal language.
- This does not encode Willard-style arithmetized syntax or proof codes.
- This does not define IS(A), Type NS, or a tableaux proof language.
- This does not make Universal Cell behavior complete; it only classifies the
  current transition-claim surface.
