# Recipient Non-Init Command Rejection Claim

Status: named claim and predicate-result proof-certificate surface, updated
2026-05-18.

ADR-0054 promotes the current recipient non-init command-message rejection
boundary into the transition-claim surface. The claim is
`UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED` in
`claims/transition_claims.json`, checked by
`recipient_non_init_command_message_rejected` in
`autarkic_systems/transition_predicates.py`.

## Claim Boundary

The claim covers recipient input cases that ADR-0053 keeps blocked:

- single `standard-signal` command-message input;
- fixed-cell upstream `standard-signal` command-message input;
- multiple simultaneous command-message input conflicts.

The predicate checks that the transition returns `rejected-input`, clears the
consumed input, preserves role and memory, creates no output, preserves
automail, self-mailbox, control, and buffer state, and handles upstream
according to the source of the rejected command.

Single `write-buf-zero` and `write-buf-one` recipient command-message inputs
are excluded from this rejection boundary after ADR-0169. They now belong to
the `UC-RECIPIENT-WRITE-BUFFER-COMMAND-MESSAGE-APPENDED` execution claim.
This claim still names the remaining rejected non-init command boundary so
later traces or semantic revisions have a stable reference point.

## Proof Surface

`claims/proof_certificates.json` covers the claim with `predicate-result`
steps that name `recipient_non_init_command_message_rejected` directly for fixed
upstream `standard-signal` rejection, a stem multi-command conflict rejection,
an all-init conflict rejection, and a negative changed-role example.

ADR-0163 had added the explicit upstream write-buffer positive examples. At
that point, recipient write-buffer command-message behavior remained inside
the rejection boundary while the claim/proof coverage was made as explicit as
the already implemented self-target write-buffer surfaces.

ADR-0169 removes those write-buffer positive examples from this rejection
claim. The remaining rejection examples cover `standard-signal` and
multi-command conflict behavior, while single recipient write-buffer command
messages are verified by the new append-execution claim.

## Verification

Run:

```sh
python -m unittest tests.test_recipient_non_init_command_rejection_claim
```

The tests cover predicate behavior, inactive preconditions, manifest examples,
proof certificate coverage, and object-language predicate vocabulary.
