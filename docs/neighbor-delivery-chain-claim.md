# Neighbor Delivery Chain Claims

ADR-0078 adds the first claim and proof-certificate surface for a composed
transition chain.
ADR-0079 adds the explicit transition-chain claim language that validates this
surface.

The first claim lives in `claims/transition_chain_claims.json` as
`UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED`, checked by
`neighbor_delivery_consumed_by_recipient` in
`autarkic_systems/transition_chain_predicates.py`.
ADR-0091 adds `UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-REJECTED`, checked by
`neighbor_delivery_rejected_by_recipient`, for the delivered non-init
recipient rejection boundary.

## Claim Boundary

The claim covers the ADR-0077 handoff where a stem sender completes
`neighbor-b/proc-l-init`, installs the delivered output tuple as an empty
recipient's upstream tuple, and the recipient consumes the init-family command
through the existing recipient command-message logic.

The manifest also records negative examples for:

- a sender that completes a self-target non-init command instead of delivering;
- a recipient that already has pending upstream state; and
- a delivered non-init `write-buf-one` token.

Those negative examples keep the claim from becoming a hidden scheduler or
overwrite rule.

The rejection claim covers the delivered non-init `write-buf-one` token path:
the sender performs neighbor delivery, the delivered output is installed as
recipient upstream state, and the recipient rejects the command through the
existing non-init boundary. It deliberately does not execute write-buffer
semantics.

## Proof Surface

`claims/transition_chain_proof_certificates.json` covers both chain claims with
`manifest-example` steps for all seven examples. The verifier in
`autarkic_systems/chain_claims.py` evaluates each manifest example by running
the ADR-0077 chain helper and then checking the chain predicate.

## Verification

Run:

```sh
python -m unittest tests.test_neighbor_delivery_chain_claim
python -m autarkic_systems.chain_claims
```

The tests cover manifest loading, example evaluation, proof-certificate
coverage, positive predicate acceptance, non-init delivered-token rejection,
and rejection-predicate refusal of the init-consumption chain.

ADR-0080 adds the module command so the chain claim surface can be validated
outside the unit-test runner.

ADR-0081 adds a separate chain evidence bundle that ties this claim/proof
surface to the chain object language, the underlying neighbor-delivery and
recipient-init transition bundles, and the source-status boundary records.

ADR-0082 adds a dedicated chain trace for the same accepted handoff, giving the
claim a single recorded sender-step, handoff, and recipient-step artifact.
