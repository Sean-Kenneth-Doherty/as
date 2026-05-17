# Command-Buffer Unsupported Evidence Bundle

ADR-0075 adds `evidence/command_buffer_unsupported_bundle.json`, the seventh
AS transition evidence bundle.

The bundle covers the positive
`UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED` example named
`self write buffer command remains appended`, where a matching standard input
completes buffer `00111`, decodes it as `self/write-buf-one`, and preserves
the completed command buffer at the append boundary.

## Evidence Path

The bundle points to:

- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/command_buffer_unsupported_trace.json`;
- `schematics/command_buffer_unsupported_trace.svg`;
- `sources/prc_hardware_witness_map.json`;
- `sources/stem_command_execution_source_status.json`;
- `sources/recipient_non_init_command_source_status.json`;
- `sources/standard_signal_command_semantics_status.json`; and
- `sources/write_buffer_command_semantics_status.json`.

The evidence bundle validator checks that the append-boundary claim example
evaluates true, the proof certificate is accepted, the schematic trace
executes and matches the exact claim example, the committed SVG matches
renderer output, and the source-status boundary files remain present and
parseable.

## Boundary

The bundle records self-target non-init command-buffer append preservation
only. It does not add write-buffer command-token execution,
`standard-signal` command-token execution, recipient non-init command
execution, priority, or sequencing.

## Verification

Run:

```sh
python -m unittest tests.test_command_buffer_unsupported_evidence_bundle
python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json
```

The tests cover the bundle fields, path set, cross-layer validation, registry
entry, and drifted status rejection.
