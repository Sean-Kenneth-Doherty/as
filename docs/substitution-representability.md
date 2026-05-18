# Substitution Representability Witness

Status: checked meta-level graph witness, not a proof, 2026-05-18.

ADR-0244 adds `claims/substitution_representability_targets.json` and
`autarkic_systems/substitution_representability.py`. It records the first
checked graph point for the `substitution_code` diagonal route introduced by
ADR-0242.

## Purpose

The checked diagonal seed says what syntactic self-application should look
like, but a diagonal lemma requires more than that syntax. A later proof must
show that meta-level substitution is represented by an arithmetic graph
formula.

This surface checks only the concrete graph point now needed by that later
proof:

- rebuild the checked diagonal seed for `AS-FIXED-POINT-SELFCONS1-TARGET`;
- encode the seed as the formula code;
- use that same seed code as the argument code;
- quote the argument code as a formal term;
- substitute that quotation term into the seed; and
- verify the resulting output code length, prefix, and free-variable boundary.

## Current Witness

`AS-SUBSTITUTION-REPRESENTABILITY-DIAGONAL-SEED-WITNESS` is
`representability-witness-not-proof`.

The checked formula and argument code are both:

```text
[41, 1, 22, 11, 1, 18, 11, 4, 11, 4]
```

The checked output is closed, has code length `296`, and begins:

```text
[41, 1, 22, 11, 1, 18, 17, 13, 13, 13, 13, 13]
```

## Run

```sh
python -m autarkic_systems.substitution_representability
python -m autarkic_systems.substitution_representability --format json
```

The validator checks that:

- the diagonal-construction, fixed-point target, and formal codebook
  dependencies remain accepted;
- required Willard anchors are present and known;
- witness IDs are unique;
- the witness preserves `representability-witness-not-proof`;
- required future work and non-claims are explicit;
- the formula and argument codes match the rebuilt seed; and
- the output code length, prefix, and free variables match the manifest.

## Boundary

This is not a delta0 substitution graph formula, not a substitution
representability proof, not a diagonal lemma, not a fixed-point equation proof,
and not a self-consistency theorem. The next AS step is to turn this concrete
meta-level witness into a formal graph target before claiming diagonal
representability.
