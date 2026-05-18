# Formal Confidence Target

Status: checked target boundary with arithmetic syntax, codebook, substitution,
consistency-level target, deduction-apparatus target, fixed-point target, and
quotation sequence/term dependencies, plus a validated fixed-point equation
candidate dependency, 2026-05-18.

ADR-0224 adds `claims/formal_confidence_targets.json` and
`autarkic_systems/formal_confidence.py`. The target records what AS would need
before claiming Willard-style formal self-confidence, while preserving the
current truth: AS does not yet make that claim.

## Purpose

Current AS evidence is real but scoped. It validates Universal Cell transition
claims, transition-chain claims, network-sequence claims, object-language
surfaces, and local `predicate-result` proof certificates.

That surface is not yet an SJAS-level self-consistency result. A Willard-style
claim needs at least:

- an arithmetic or bounded-formula object language;
- an axiom basis;
- a deduction apparatus;
- proof-code encoding;
- substitution and self-reference machinery;
- an exact consistency notion; and
- a bridge back to the substrate claims AS can execute.

The formal-confidence target keeps those obligations explicit. ADR-0226 adds
`language/formal_arithmetic_language.json`, so the target now has a checked
syntax-only Type-NS arithmetic language and `delta0` bounded formula class.
ADR-0227 adds `language/formal_codebook.json`, so the target also has a first
round-trippable proof-code shell for terms, formulae, sentences, and
placeholder proof lines. ADR-0228 adds
`language/formal_substitution_examples.json`, so capture-avoiding substitution
examples now validate against those codes. ADR-0229 adds
`claims/consistency_level_targets.json`, so Level-1 consistency is selected as
the first target notion. ADR-0230 adds
`claims/deduction_apparatus_targets.json`, so the AS-local predicate-result
proof-certificate checker is selected as the current deduction-apparatus
target. ADR-0231 adds `claims/fixed_point_targets.json`, so a first `pi1`
fixed-point target template and checked substitution instance are selected.
ADR-0233 adds `language/formal_quotation_sequence_examples.json`, so the
fixed-point target now depends on a checked token-numeral sequence object
instead of raw token tuples. ADR-0234 adds
`language/formal_quotation_term_examples.json`, so the fixed-point target now
depends on a checked nested sequence term surface. The target remains blocked
on constructing the actual fixed point. ADR-0235 adds
`claims/fixed_point_equation_candidates.json`, recording that the naive
quotation-term substitution candidate is not fixed. ADR-0236 makes that
candidate surface a structured, fail-closed dependency of the aggregate
formal-confidence validator.

## Current Target

`AS-FORMAL-CONFIDENCE-TARGET-001` is deliberately `blocked`.

It names these Willard anchors as constraints:

- `W2011-D3.4-GENERIC-CONFIGURATION`;
- `W2011-D5.6-LEVEL-K-CONSISTENCY`;
- `W2011-D5.7-SELFCONSK`;
- `W2020-D3.2-SELF-JUSTIFYING-GENAC`;
- `W2020-D3.4-TYPE-NS-A-S-M`; and
- `W2020-T4.4-T4.5-LEM-BOUNDARY`.

It records the current configuration as local AS transition/chain/sequence
object languages, `language/formal_arithmetic_language.json`,
`language/formal_codebook.json`,
`language/formal_substitution_examples.json`,
`claims/consistency_level_targets.json`, and local predicate-result proof
certificates through `claims/deduction_apparatus_targets.json`, plus the
fixed-point target in `claims/fixed_point_targets.json`, which now references
`language/formal_quotation_sequence_examples.json` and
`language/formal_quotation_term_examples.json`; the naive equation candidate
is recorded and validated through `claims/fixed_point_equation_candidates.json`.
It also records the remaining blocker: `fixed-point-construction`.

## Run

```sh
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.formal_confidence --format json
python -m autarkic_systems.formal_arithmetic
python -m autarkic_systems.formal_arithmetic --format json
python -m autarkic_systems.formal_code
python -m autarkic_systems.formal_code --format json
python -m autarkic_systems.formal_substitution
python -m autarkic_systems.formal_substitution --format json
python -m autarkic_systems.consistency_level
python -m autarkic_systems.consistency_level --format json
python -m autarkic_systems.deduction_apparatus
python -m autarkic_systems.deduction_apparatus --format json
python -m autarkic_systems.formal_quotation_sequence
python -m autarkic_systems.formal_quotation_sequence --format json
python -m autarkic_systems.formal_quotation_term
python -m autarkic_systems.formal_quotation_term --format json
python -m autarkic_systems.fixed_point_equation
python -m autarkic_systems.fixed_point_equation --format json
python -m autarkic_systems.fixed_point
python -m autarkic_systems.fixed_point --format json
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- target IDs are unique;
- referenced Willard anchors exist;
- required Willard anchors are present;
- every required configuration field is present and non-blank;
- the referenced fixed-point equation candidate surface validates;
- blocked targets name blockers; and
- each target names a next AS action.

ADR-0225 folds this validator into aggregate project status, so missing or
drifted formal-confidence targets now make the main status and inherited
handoff path reject instead of remaining invisible.

## Boundary

This is not a proof checker, not an arithmetic parser, and not a
self-consistency theorem. It is a fail-closed target boundary so later work can
build toward a real formal-confidence claim without confusing current green
substrate evidence for that claim.
