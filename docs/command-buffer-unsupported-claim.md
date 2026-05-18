# Command Buffer Unsupported Claim

Status: named claim and proof-certificate surface, 2026-05-17.

ADR-0041 promotes the unsupported self-target non-init command-buffer boundary
into the transition-claim surface. The claim is
`UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED` in
`claims/transition_claims.json`, checked by
`stem_command_buffer_preserves_unsupported_completion` in
`autarkic_systems/transition_predicates.py`.
ADR-0044 narrows this claim after neighbor-target command buffers become
delivered output tokens.

## Claim Boundary

The claim covers command-buffer transitions where a standard-signal append
completes a self-target five-bit buffer that is outside the ADR-0037 init-family
execution slice:

- self-target `standard-signal`;
- self-target `write-buf-zero`;
- self-target `write-buf-one`.

The predicate checks that the transition remains at `stem-buffer-appended`,
clears consumed input, preserves output, preserves role/memory/upstream,
preserves the control rail, keeps automail and `self_mailbox` empty, and leaves
the completed five-bit buffer intact.

The claim does not define self-target `standard-signal`, write-buffer command
execution, or full command-buffer execution. Neighbor-target completions are no
longer part of this boundary after ADR-0044.

## Proof Surface

`claims/transition_claims.json` now has positive manifest examples for all
three unsupported self-target command-buffer completions: self
`standard-signal`, self `write-buf-zero`, and self `write-buf-one`. It also
keeps a negative example proving that processing the completed buffer would
violate the append boundary.

`claims/proof_certificates.json` covers every manifest example with
`manifest-example` steps.

## Verification

Run:

```sh
python -m unittest tests.test_command_buffer_unsupported_claim
```

The tests cover the predicate, manifest examples, proof certificate coverage,
and object-language predicate vocabulary.
