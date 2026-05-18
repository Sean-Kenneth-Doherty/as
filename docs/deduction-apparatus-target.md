# Deduction Apparatus Target

Status: checked target selection, not self-justification, 2026-05-18.

ADR-0230 adds `claims/deduction_apparatus_targets.json` and
`autarkic_systems/deduction_apparatus.py`. The target selects the current
AS-local `predicate-result` proof-certificate checker as the deduction
apparatus for the executable substrate surfaces.

## Purpose

AS already has local proof certificates for transition, transition-chain, and
network-sequence claims. Those certificates are useful, but they are not a
Hilbert system, semantic-tableau proof search, Tab-1, an arithmetized proof
predicate, or a self-justifying theorem.

The deduction-apparatus target keeps that distinction explicit. It records
the apparatus AS can currently validate:

- transition proof certificates in `claims/proof_certificates.json`;
- transition-chain proof certificates in
  `claims/transition_chain_proof_certificates.json`;
- network-sequence proof certificates in
  `claims/network_sequence_proof_certificates.json`; and
- the shared `predicate-result` rule across those surfaces.

It also records what AS is not claiming: no theorem prover, no Hilbert-style
completeness result, no semantic-tableau or Tab-1 apparatus, no arithmetized
proof predicate, and no self-consistency theorem.

## Current Target

`AS-DEDUCTION-APPARATUS-PREDICATE-RESULT` is
`target-selected-not-self-justifying`.

It names these Willard anchors as constraints:

- `W2011-D3.4-GENERIC-CONFIGURATION`;
- `W2016-D3.2-HILBERT-STYLE`;
- `W2016-D3.4-SELF-JUSTIFYING-CONFIGURATION`;
- `W2020-D3.2-SELF-JUSTIFYING-GENAC`;
- `W2020-SEC4-TAB-XTAB-TAB1`; and
- `W2020-T4.4-T4.5-LEM-BOUNDARY`.

The checked-in target currently covers 52 certificate steps, all using
`predicate-result` and none using `manifest-example`.

## Run

```sh
python -m autarkic_systems.deduction_apparatus
python -m autarkic_systems.deduction_apparatus --format json
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- required Willard anchors are present and known;
- the formal codebook remains valid;
- the selected apparatus is the AS-local predicate-result checker;
- Hilbert/tableau apparatus families are not overclaimed;
- every required certificate surface is present; and
- every checked certificate step uses `predicate-result`.

## Boundary

This is a deduction-apparatus target selection, not a proof search engine or a
formal self-justification result. The remaining formal-confidence blocker is
fixed-point self-reference.
