# Recipient Init Command-Message Claim

Status: named claim and proof-certificate surface, 2026-05-17.

ADR-0050 promotes the ADR-0049 recipient init command-message behavior into
the transition-claim surface. The claim is
`UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED` in
`claims/transition_claims.json`, checked by
`recipient_init_command_message_processed` in
`autarkic_systems/transition_predicates.py`.

## Claim Boundary

The claim covers one input-channel init-family command message on a recipient
cell:

- `stem-init`;
- `wire-r-init`;
- `wire-l-init`;
- `proc-r-init`;
- `proc-l-init`.

For fixed cells, the claim also covers the existing upstream-pull path when
direct input is empty and upstream holds one init-family command-message token.

The predicate checks that the transition reaches
`recipient-init-command-message-processed`, reconfigures to the commanded
role/memory target, clears input and output, clears automail, self-mailbox,
control, and buffer state, and either clears pulled upstream input or preserves
upstream for direct input.

The claim does not cover `standard-signal`, write-buffer command messages,
multiple simultaneous command-message inputs, or occupied-output blocking.

## Proof Surface

`claims/proof_certificates.json` covers the claim with `manifest-example`
steps for fixed upstream processing, stem direct-input processing, and a
negative wrong-target example.

## Verification

Run:

```sh
python -m unittest tests.test_recipient_init_command_message_claim
```

The tests cover predicate behavior, inactive preconditions, manifest examples,
proof certificate coverage, and object-language predicate vocabulary.
