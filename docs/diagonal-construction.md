# Diagonal Construction Seed

Status: checked syntactic seed, not a diagonal lemma, 2026-05-18.

ADR-0242 adds `claims/diagonal_construction_targets.json` and
`autarkic_systems/diagonal_construction.py`. It is the first checked artifact
that uses the ADR-0241 `substitution_code(t,u)` term to build the diagonal
route. ADR-0243 makes this seed a structured dependency of the aggregate
formal-confidence target, so formal-confidence validation fails closed if this
surface drifts. ADR-0244 adds the first checked substitution graph witness for
this seed, while still leaving representability unproved.

## Purpose

The naive fixed-point candidate directly embedded a full quotation term and
was shown length-obstructed. The diagonal route instead needs an arithmetized
substitution-code operation. This surface checks only the syntax needed for
that route:

- start from the current `AS-FIXED-POINT-SELFCONS1-TARGET`;
- replace the target variable `n` with `substitution_code(n,n)`;
- encode the resulting seed;
- quote the seed code as a formal term; and
- substitute that quotation term back into the seed to produce a closed
  syntactic instance.

## Current Seed

`AS-FIXED-POINT-SELFCONS1-DIAGONAL-SEED` is
`diagonal-seed-not-proved`.

The checked seed code is:

```text
[41, 1, 22, 11, 1, 18, 11, 4, 11, 4]
```

The checked seed has free variable `n`. The quoted seed instance is closed,
has code length `296`, and begins:

```text
[41, 1, 22, 11, 1, 18, 17, 13, 13, 13, 13, 13]
```

## Run

```sh
python -m autarkic_systems.diagonal_construction
python -m autarkic_systems.diagonal_construction --format json
```

The validator checks that:

- the fixed-point target and formal codebook dependencies remain accepted;
- required Willard anchors are present and known;
- the construction uses `substitution_code`;
- the seed code and free variables match the manifest;
- the quoted seed instance length, prefix, and free variables match the
  manifest; and
- proved diagonal statuses are rejected.

## Boundary

This is not a substitution representability proof, diagonal lemma, fixed-point
equation proof, arithmetized proof predicate, or self-consistency theorem. It
is the checked syntactic seed needed before those later claims can be pursued
without returning to direct quotation self-embedding. Use
`python -m autarkic_systems.substitution_representability` for the next
checked graph witness on top of this seed.
