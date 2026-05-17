# Self Command Buffer Init Claim

Status: named claim and proof-certificate surface, 2026-05-17.

ADR-0038 promotes the ADR-0037 self-target init command-buffer dispatch into
the transition-claim surface. The claim is
`UC-STEM-COMMAND-BUFFER-SELF-INIT` in `claims/transition_claims.json`, checked
by `stem_command_buffer_executes_self_init` in
`autarkic_systems/transition_predicates.py`.

## Claim Boundary

The claim covers only command-buffer transitions where a standard-signal append
completes a five-bit buffer that decodes to target `self` and one of:

- `stem-init`;
- `wire-r-init`;
- `wire-l-init`;
- `proc-r-init`;
- `proc-l-init`.

The predicate checks that the transition reaches
`stem-command-buffer-self-processed`, reconfigures to the decoded role/memory,
clears consumed input, clears output, clears automail and `self_mailbox`, and
clears control/buffer state.

The claim does not cover neighbor routing, self-target `standard-signal`,
write-buffer commands, or full command-buffer execution.

## Proof Surface

`claims/proof_certificates.json` covers the claim with `manifest-example`
steps for the positive and negative manifest examples.

## Verification

Run:

```sh
python -m unittest tests.test_self_command_buffer_init_claim
```

The tests cover the predicate, manifest examples, proof certificate coverage,
and object-language predicate vocabulary.
