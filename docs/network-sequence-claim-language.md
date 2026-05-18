# Network Sequence Claim Language

ADR-0201 adds the first object language for post-handoff network-sequence
claims.

## Purpose

The network-sequence claim surface already checks one post-handoff witness and
its predicate-result proof certificate. The language manifest makes the syntax
explicit instead of leaving the allowed terms and proof objects implicit in
Python and JSON conventions.

## Run

```sh
python -m autarkic_systems.network_sequence_object_language
python -m autarkic_systems.network_sequence_object_language --format json
```

The checked language is `language/network_sequence_claim_language.json`.

## Validation

The validator checks:

- required syntax classes;
- roles, memory values, signal vocabulary, automail values, command messages,
  transition statuses, chain statuses, sequence statuses, and cell fields;
- implemented sequence predicate symbols;
- network-sequence claim sentence kind and claim ID prefixes;
- proof-object rules; and
- the checked-in sequence claim/proof surface.

## Boundary

This is not a new proof system, scheduler, topology model, timing model,
sequence behavior, evidence bundle, project-status field, or command semantic.
It is the explicit object-language layer for the current
`UC-SEQUENCE-POST-HANDOFF-SIGNAL-ROUTED` claim surface.
