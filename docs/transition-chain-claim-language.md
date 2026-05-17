# Transition Chain Claim Language

ADR-0079 adds `language/transition_chain_claim_language.json`, the first
explicit object language for AS transition-chain claims.

The language is deliberately narrow. It covers the current neighbor delivery
chain claim surface, not arbitrary temporal logic, graph topology, scheduling,
or future multi-cell simulation.

## Syntax Classes

| Class | Current Meaning |
| --- | --- |
| `terms` | Universal Cell term vocabulary reused by chain examples, transition statuses, chain statuses, and cell fields. |
| `chain_formulae` | Predicate applications of the form `predicate(chain_result)`, currently covering consumed and rejected neighbor-delivery handoffs. |
| `chain_sentences` | Transition-chain claim sentences named by IDs such as `UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED`. |
| `proof_objects` | Proof-certificate steps. The only current rule is `manifest-example`. |
| `substrate_chain_claims` | Paths to the chain-claim and chain-certificate manifests. |

## Boundary

This language is separate from
`language/transition_claim_language.json`. The transition language covers
single-step claims of the form `predicate(before_cell, step_result)`. The chain
language covers composed handoff claims where sender, recipient, and chain
status must all remain visible.

## Verification

Run:

```sh
python -m unittest tests.test_chain_object_language
python -m autarkic_systems.chain_claims
python -m autarkic_systems.chain_claims --format json
```

The validator checks required syntax classes, term vocabularies, implemented
chain predicates, current chain claims, proof-object rules, and rejection of
unknown predicates, unknown proof rules, and incomplete chain-status
vocabularies.

ADR-0080 exposes the same chain language, example, certificate, and surface
validation through the `python -m autarkic_systems.chain_claims` command.

ADR-0081 validates this language as part of the first composed-chain evidence
bundle:

```sh
python -m autarkic_systems.chain_evidence_bundle
```

ADR-0091 extends the language predicate-symbol set with
`neighbor_delivery_rejected_by_recipient` and validates two chain claims, two
proof certificates, and seven manifest examples.
