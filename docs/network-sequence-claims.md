# Network Sequence Claims

ADR-0197 adds the first claim surface over the post-handoff signal witness.

## Purpose

The post-handoff witness shows that a delivered `proc-l-init` command can
change later recipient behavior. The claim surface names that behavior and
checks positive and negative examples through a small predicate-result proof
certificate.

## Run

```sh
python -m autarkic_systems.network_sequence_claims
python -m autarkic_systems.network_sequence_claims --format json
```

The checked claim is `UC-SEQUENCE-POST-HANDOFF-SIGNAL-ROUTED`.

It covers:

- a positive `proc-l-init` handoff followed by binary signal routing;
- a negative consumed write-buffer handoff, which is not an init-family
  reconfiguration sequence; and
- a negative malformed follow-up input, which preserves the delivery witness
  but does not route.

## Artifacts

- `claims/network_sequence_claims.json` names the claim and examples.
- `claims/network_sequence_proof_certificates.json` covers every example with
  `predicate-result` steps.
- `autarkic_systems/network_sequence_predicates.py` implements the checked
  predicate.
- `autarkic_systems/network_sequence_claims.py` loads, evaluates, verifies, and
  reports the claim surface.

## Boundary

This is not yet an evidence bundle or project-status input. It is the first
named claim/proof layer over the ADR-0196 witness, preserving the same boundary:
no scheduler, topology, timing, output clearing, or new command semantics.
