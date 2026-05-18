# Self Mailbox Unsupported Claim

Status: named boundary claim and proof-certificate surface, 2026-05-17.

ADR-0034 promotes the ADR-0030 unsupported self-mailbox command boundary into
the transition-claim surface. The claim is
`UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED` in
`claims/transition_claims.json`, checked by
`self_mailbox_preserves_unsupported_command` in
`autarkic_systems/transition_predicates.py`.

## Claim Boundary

The claim covers the self-mailbox commands whose execution remains unresolved:

- `standard-signal`;
- `write-buf-zero`;
- `write-buf-one`.

The predicate checks that a stem cell with empty input, empty output, empty
automail, and one of those unsupported `self_mailbox` commands reaches
`self-mailbox-unsupported` and preserves the entire cell unchanged.

This claim does not define the future semantics of those commands. It records
that AS currently refuses to execute them until the source boundary is resolved.

## Proof Surface

`claims/transition_claims.json` now has positive manifest examples for all
three unsupported self-mailbox commands: `standard-signal`, `write-buf-zero`,
and `write-buf-one`. It also keeps a negative example proving that clearing an
unsupported mailbox command would violate the boundary.

`claims/proof_certificates.json` covers every manifest example with
`manifest-example` steps.

## Verification

Run:

```sh
python -m unittest tests.test_self_mailbox_unsupported_claim
```

The tests cover the predicate, manifest examples, proof certificate coverage,
and object-language predicate vocabulary.
