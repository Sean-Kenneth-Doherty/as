# Transition Claim Language

Status: ADR-0012 object-language note, 2026-05-17.

## Purpose

`language/transition_claim_language.json` names the first explicit AS object
language. It is deliberately small: it covers the Universal Cell transition
claims that AS can currently execute, not the full IS(A) or SJAS arithmetic
language. ADR-0023 extends the current predicate vocabulary with
`stem_buffer_accumulates` for the stem buffer accumulation subset. ADR-0028
extends the term vocabulary with `command_messages` and the `self_mailbox` cell
field without adding command execution. ADR-0029 extends `signals` so channel
tuples can represent command-message tokens for neighbor delivery.
ADR-0030 extends `statuses` for the first self-mailbox init-command execution
slice. ADR-0031 extends `formulae.predicate_symbols` with
`self_mailbox_executes_init_command` so that execution subset can be checked as
a named transition claim. ADR-0034 adds
`self_mailbox_preserves_unsupported_command` for the unresolved self-mailbox
command boundary.
ADR-0037 adds `stem-command-buffer-self-processed` to the status vocabulary for
the first narrow self-target init command-buffer dispatch. ADR-0038 adds
`stem_command_buffer_executes_self_init` for the corresponding transition
claim. ADR-0041 adds
`stem_command_buffer_preserves_unsupported_completion` for completed command
buffers that remain at the append boundary. ADR-0044 adds
`stem-command-buffer-neighbor-delivered` for neighbor-target command buffers
that deliver decoded command tokens onto output channels. ADR-0045 adds
`stem_command_buffer_delivers_neighbor_command` for the corresponding named
transition claim.

The point is to stop relying on implicit Python/JSON shape as the only syntax
boundary. Current claims can now be checked against named syntax classes before
later proof or self-reference work builds on them.

## Syntax Classes

| Class | Current meaning |
| --- | --- |
| `terms` | Universal Cell term vocabulary: roles, memory values, channel tokens, automail commands, command-message mailbox values, statuses, and cell fields. |
| `formulae` | Predicate applications of the form `predicate(before_cell, step_result)`. |
| `sentences` | Transition-claim sentences named by claim IDs such as `UC-FIXED-OUTPUT-PRESERVED`. |
| `proof_objects` | Proof-certificate steps. The only current rule is `manifest-example`. |
| `substrate_claims` | Paths to the transition-claim and proof-certificate manifests. |

ADR-0078 deliberately keeps two-step transition-chain claims in
`claims/transition_chain_claims.json` instead of forcing them into this
single-transition language. Chain claims use their own checker until AS has
enough multi-step artifacts to justify a full chain object language.
ADR-0079 adds that first narrow chain object language in
`language/transition_chain_claim_language.json`.

## Verification

Fast validation is covered by:

```sh
python -m unittest tests.test_object_language
```

The validator checks:

- the language manifest names all required syntax classes;
- language term sets match the Universal Cell implementation vocabulary;
- formula predicate symbols correspond to implemented predicate functions;
- current transition claims fit the language;
- current proof certificates use known proof-object rules;
- deliberately missing classes, unknown predicates, unknown proof rules, and
  incomplete term vocabularies are rejected.

## Non-Goals

- This is not the full AS formal language.
- This does not encode Willard-style arithmetized syntax or proof codes.
- This does not define IS(A), Type NS, or a tableaux proof language.
- This does not make Universal Cell behavior complete; it only classifies the
  current transition-claim surface.
