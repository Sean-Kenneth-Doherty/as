# Recipient Write-Buffer Command Evidence Bundle

Status: transition evidence bundle with predicate-result proof surface, updated
2026-05-18.

ADR-0170 adds
`evidence/recipient_write_buffer_command_message_bundle.json`, registering the
recipient write-buffer command-message append surface in the transition
evidence registry.

The bundle ties together:

- `UC-RECIPIENT-WRITE-BUFFER-COMMAND-MESSAGE-APPENDED`;
- the `recipient_write_buffer_command_message_appends_literal` predicate;
- the predicate-result proof certificate for that claim;
- `schematics/recipient_write_buffer_command_message_trace.json`;
- `schematics/recipient_write_buffer_command_message_trace.svg`;
- `sources/prc_hardware_witness_map.json`; and
- the recipient/write-buffer/standard-signal source-status records.

The traced positive example is `fixed upstream write-buf-zero command
appended`. The covered positive examples include that upstream zero append and
`stem recipient write-buf-one command appended`.

## Boundary

This bundle promotes already implemented ADR-0169 behavior into the
cross-layer evidence registry. It does not add runtime behavior. Init-family
recipient consumption, standard-signal rejection, multi-command conflict
rejection, and self-target write-buffer execution remain covered by their own
bundles or tests.

## Verification

Run:

```sh
python -m unittest tests.test_recipient_write_buffer_command_evidence_bundle
python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json
```

The tests and CLI validate claim/proof, trace execution, SVG renderer parity,
source-status paths, boundary text, and registry completeness.
