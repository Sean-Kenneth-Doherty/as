# Recipient Non-Init Rejection Evidence Bundle

ADR-0068 adds `evidence/recipient_non_init_command_rejection_bundle.json`, the
second AS transition evidence bundle.

The bundle's trace-aligned primary example is the positive
`UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED` example named
`fixed upstream standard-signal command rejected`, where a processor-left
recipient pulls an upstream `standard-signal` command-message token, rejects
it, preserves role and memory, and clears the active command source.

ADR-0163 temporarily extended the bundle's covered positive examples to
include upstream `write-buf-zero` and `write-buf-one` recipient rejections.
ADR-0169 removes those write-buffer examples from this rejection bundle because
single recipient write-buffer command messages now append instead of reject.

## Evidence Path

The bundle points to:

- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/recipient_non_init_command_rejection_trace.json`;
- `schematics/recipient_non_init_command_rejection_trace.svg`;
- `sources/prc_hardware_witness_map.json`;
- `sources/recipient_non_init_command_source_status.json`;
- `sources/standard_signal_command_semantics_status.json`;
- `sources/write_buffer_command_semantics_status.json`; and
- `sources/multi_command_recipient_input_policy_status.json`.

The evidence bundle validator checks that the rejection claim example
evaluates true, every covered positive example evaluates true, the proof
certificate is accepted through predicate-result steps, the schematic trace
executes and validates against the PRC hardware witness map, the committed SVG
matches renderer output, and the source-status boundary files remain present and
parseable.

## Boundary

The bundle records a rejection boundary, not new recipient command execution.
`standard-signal` and multi-command recipient inputs remain governed by
source-status blockers and rejection policy. Direct self-mailbox, completed
self-target command-buffer, and single delivered recipient write-buffer
command tokens are separate implemented surfaces.

## Verification

Run:

```sh
python -m unittest tests.test_recipient_non_init_evidence_bundle
python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json
```

The tests cover the bundle fields, path set, cross-layer validation, registry
entry, and drifted status rejection.
