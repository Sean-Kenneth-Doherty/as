# Neighbor Delivery Chain Claim

ADR-0078 adds the first claim and proof-certificate surface for a composed
transition chain.
ADR-0079 adds the explicit transition-chain claim language that validates this
surface.

The claim lives in `claims/transition_chain_claims.json` as
`UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED`, checked by
`neighbor_delivery_consumed_by_recipient` in
`autarkic_systems/transition_chain_predicates.py`.

## Claim Boundary

The claim covers the ADR-0077 handoff where a stem sender completes
`neighbor-b/proc-l-init`, installs the delivered output tuple as an empty
recipient's upstream tuple, and the recipient consumes the init-family command
through the existing recipient command-message logic.

The manifest also records negative examples for:

- a sender that completes a self-target non-init command instead of delivering;
- a recipient that already has pending upstream state; and
- a delivered non-init `write-buf-one` token.

Those negative examples keep the claim from becoming a hidden scheduler,
overwrite rule, or non-init command executor.

## Proof Surface

`claims/transition_chain_proof_certificates.json` covers the chain claim with
`manifest-example` steps for all four examples. The verifier in
`autarkic_systems/chain_claims.py` evaluates each manifest example by running
the ADR-0077 chain helper and then checking the chain predicate.

## Verification

Run:

```sh
python -m unittest tests.test_neighbor_delivery_chain_claim
```

The tests cover manifest loading, example evaluation, proof-certificate
coverage, positive predicate acceptance, and non-init delivered-token
rejection.
