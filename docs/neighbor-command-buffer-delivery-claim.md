# Neighbor Command Buffer Delivery Claim

Status: named claim and predicate-result proof-certificate surface, 2026-05-18.

ADR-0045 promotes ADR-0044 neighbor-target command-buffer delivery into the
transition-claim surface. The claim is
`UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED` in
`claims/transition_claims.json`, checked by
`stem_command_buffer_delivers_neighbor_command` in
`autarkic_systems/transition_predicates.py`.

## Claim Boundary

The claim covers command-buffer transitions where a standard-signal append
completes a neighbor-target five-bit buffer:

- `neighbor-a` delivers the decoded command token to output channel 0;
- `neighbor-b` delivers the decoded command token to output channel 1;
- `neighbor-c` delivers the decoded command token to output channel 2.

The predicate checks that the transition returns
`stem-command-buffer-neighbor-delivered`, clears consumed input, preserves
role/memory/upstream, places the decoded command token on exactly the expected
output channel, clears automail and `self_mailbox`, and clears control and
buffer state.

The claim does not define recipient-side command-message consumption or
execution. It is a delivery claim only.

## Proof Surface

`claims/proof_certificates.json` covers the claim with `predicate-result`
steps that name `stem_command_buffer_delivers_neighbor_command` directly for a
positive neighbor B delivery example plus a negative wrong-channel example. The
direct predicate tests also cover neighbor A and neighbor C.

## Verification

Run:

```sh
python -m unittest tests.test_neighbor_command_buffer_delivery_claim
```

The tests cover predicate behavior for all three neighbor targets, wrong output
channels, uncleared command state, self-target precondition exclusion, manifest
examples, proof certificate coverage, and object-language predicate vocabulary.
