# Formal Quotation Sequence

Status: checked token-numeral sequence surface, not a quotation term,
2026-05-18.

ADR-0233 adds `language/formal_quotation_sequence_examples.json` and
`autarkic_systems/formal_quotation_sequence.py`. The surface wraps the
token-level unary numerals from ADR-0232 into explicit
`token-numeral-sequence` objects.

## Purpose

The fixed-point target needs to move from individual code-token numerals
toward a quoteable formula code. This slice names and validates the next
smallest object: a non-empty sequence of quoted token numerals.

The checked sequence is deliberately modest. It is useful because later
quotation-term work can depend on one validated sequence shape instead of raw
Python tuples, but it is still outside the arithmetic object language.

## Current Surface

`as-formal-quotation-sequence-v1` references:

- `language/formal_quotation_examples.json`;
- `claims/fixed_point_targets.json`; and
- the Willard generic-configuration and SelfCons(k) anchors.

It validates two examples, including the current fixed-point target expected
instance code `[41, 1, 22, 11, 1, 13, 12]`. Each example is checked for
non-empty tokens, token count, first-token numeral depth, last-token numeral
depth, accepted sequence kind, and accepted status.

## Run

```sh
python -m autarkic_systems.formal_quotation_sequence
python -m autarkic_systems.formal_quotation_sequence --format json
python -m autarkic_systems.fixed_point
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- the token quotation dependency remains accepted;
- required Willard anchors are present and known;
- the sequence manifest references the quotation and fixed-point manifests;
- every checked example quotes to `token-numeral-sequence`; and
- empty token sequences, endpoint mismatches, and unknown sequence kinds reject.

## Boundary

This is not pair/list coding in the arithmetic language, not a full quotation
term for formula codes, not a diagonal lemma, not a fixed-point equation proof,
and not a self-consistency theorem. The fixed-point target now points at this
sequence surface but remains blocked on quotation-term construction,
diagonal-lemma proof, and fixed-point equation proof.
