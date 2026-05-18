# Fixed-Point Target

Status: checked target template, not a constructed fixed point, 2026-05-18.

ADR-0231 adds `claims/fixed_point_targets.json` and
`autarkic_systems/fixed_point.py`. The target selects a first `pi1`
self-reference template and validates one substitution instance over the
formal codebook.

## Purpose

AS now has a formal codebook, capture-avoiding substitution examples, token
numeral quotation examples, token-numeral sequence examples, quotation term
examples, a checked naive equation candidate, a Level-1 consistency target,
and a selected deduction-apparatus target. Those are prerequisites for a
SelfCons-style statement, but they still do not construct a diagonal fixed
point.

The fixed-point target records the next precise obligation:

- a `pi1` template with free code variable `n`;
- a placeholder term used only to validate substitution plumbing;
- an expected substituted instance;
- the expected encoded output for that instance; and
- explicit future work before any self-consistency claim.

## Current Target

`AS-FIXED-POINT-SELFCONS1-TARGET` is
`target-selected-not-constructed`.

It names these Willard anchors as constraints:

- `W2011-D3.4-GENERIC-CONFIGURATION`;
- `W2011-D5.6-LEVEL-K-CONSISTENCY`;
- `W2011-D5.7-SELFCONSK`; and
- `W2020-D3.2-SELF-JUSTIFYING-GENAC`.

The checked instance proves only that the current substitution, codebook,
token quotation, token-numeral sequence, and quotation-term surfaces can
preserve the selected template boundary and round-trip the expected encoded
instance. ADR-0235 additionally checks the naive quotation substitution and
records that it is not a fixed point.

## Run

```sh
python -m autarkic_systems.fixed_point
python -m autarkic_systems.fixed_point --format json
python -m autarkic_systems.formal_quotation_sequence
python -m autarkic_systems.formal_quotation_term
python -m autarkic_systems.fixed_point_equation
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- required Willard anchors are present and known;
- the codebook, substitution examples, token quotation examples,
  token-numeral sequence examples, quotation term examples,
  consistency-level target, and
  deduction-apparatus target remain accepted;
- the template is a `pi1` target with the target variable free;
- the substitution instance matches the expected node and code; and
- proved fixed-point statuses are rejected.

## Boundary

This is not a diagonal lemma, not arithmetic sequence axioms, not a
fixed-point equation proof, and not a self-consistency theorem. The
formal-confidence target remains blocked on `fixed-point-construction`.
