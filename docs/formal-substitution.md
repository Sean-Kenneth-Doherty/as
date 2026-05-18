# Formal Substitution

Status: first checked capture-avoiding substitution surface, 2026-05-18.

ADR-0228 adds `language/formal_substitution_examples.json` and
`autarkic_systems/formal_substitution.py`. This is the first substitution
artifact over the formal codebook nodes, including the ADR-0234 sequence term
constructors.

## Purpose

ADR-0227 made syntax and proof-line shells encodable. The next prerequisite
for self-reference is substitution over those encoded nodes. This slice
implements capture-avoiding free-variable substitution for the canonical node
vocabulary and validates checked examples against the formal codebook.

The substitution surface currently covers:

- free-variable calculation for terms, formulae, sentence wrappers, bounded
  quantifiers, and proof-line shells;
- free-variable calculation and substitution inside `sequence_cons` quotation
  terms;
- substitution of term nodes for free variable occurrences;
- binder-respecting behavior for quantifiers and `pi1`/`sigma1` wrappers;
- capture rejection when a replacement variable would become bound; and
- expected encoded outputs through `autarkic_systems.formal_code`.

## Run

```sh
python -m autarkic_systems.formal_substitution
python -m autarkic_systems.formal_substitution --format json
```

The validator checks that:

- the substitution manifest points at the checked formal codebook;
- required Willard anchors are present and known;
- checked substitutions produce expected nodes;
- expected nodes encode to expected code sequences; and
- expected code sequences decode back to expected nodes.

## Boundary

This is not a parser, evaluator, proof checker, deduction apparatus, fixed-point
self-reference construction, diagonal lemma, or self-consistency theorem. It is
the substitution layer needed before those later claims can be stated honestly.
