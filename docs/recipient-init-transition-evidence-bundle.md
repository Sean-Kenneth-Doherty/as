# Recipient Init Transition Evidence Bundle

ADR-0065 adds `evidence/recipient_init_command_message_bundle.json`, the first
AS transition evidence bundle.

The bundle is intentionally narrow. It covers the positive
`UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED` example named
`fixed upstream wire right init processed`, where a processor-left recipient
pulls an upstream `wire-r-init` command-message token and becomes wire-right
while clearing command state.

## Evidence Path

The bundle points to:

- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/recipient_init_command_message_trace.json`;
- `schematics/recipient_init_command_message_trace.svg`;
- `sources/prc_hardware_witness_map.json`;
- `sources/recipient_command_consumption_source_status.json`;
- `sources/recipient_non_init_command_source_status.json`;
- `sources/standard_signal_command_semantics_status.json`; and
- `sources/write_buffer_command_semantics_status.json`.

`autarkic_systems/evidence_bundle.py` validates those paths together. The
validator checks that the claim example evaluates true, the proof certificate
is accepted, the schematic trace executes and validates against the PRC
hardware witness map, the committed SVG matches renderer output, and the
source-status boundary files are present and parseable.

## Boundary

The bundle does not widen command-message semantics. It covers only
init-family recipient command-message consumption. Non-init recipient commands,
`standard-signal` command-token execution, and write-buffer command-token
execution remain governed by their source-status blockers.

## Verification

Run:

```sh
python -m unittest tests.test_recipient_init_transition_evidence_bundle
```

The tests cover the bundle fields, path set, cross-layer validation, drifted
claim IDs, and missing SVG paths.
