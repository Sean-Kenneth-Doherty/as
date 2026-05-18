# Command-Buffer Unsupported Evidence Bundle

ADR-0075 adds `evidence/command_buffer_unsupported_bundle.json`, the seventh
AS transition evidence bundle.

The bundle's trace-aligned primary example is
`self standard signal command remains appended`, where a matching standard input
completes buffer `00000`, decodes it as `self/standard-signal`, and preserves
the completed command buffer at the append boundary.

ADR-0161 narrows the `covered_positive_examples` for the same claim after
moving self-target write-buffer commands into explicit append execution
claims:

- `self standard signal command remains appended`.

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

The evidence bundle validator checks that the trace-aligned append-boundary
claim example evaluates true, every covered positive example exists and
evaluates true with the expected status, the proof certificate is accepted,
the schematic trace executes and matches the exact primary claim example, the
committed SVG matches renderer output, and the source-status boundary files
remain present and parseable.

## Boundary

The bundle records self-target non-init command-buffer append preservation
only. It does not add write-buffer command-token execution,
`standard-signal` command-token execution, recipient non-init command
execution, priority, or sequencing.
ADR-0151 reuses this existing append boundary to resolve the standard-signal
self-target command-buffer surface as unsupported-preserved.
ADR-0161 removes self-target write-buffer commands from this unsupported
boundary and implements completed self-target write-buffer command-buffer
append behavior in
`UC-STEM-COMMAND-BUFFER-SELF-WRITE-BUFFER-APPENDED`.

## Verification

Run:

```sh
python -m unittest tests.test_command_buffer_unsupported_evidence_bundle
python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json
```

The tests cover the bundle fields, covered examples, path set, cross-layer
validation, registry entry, drifted covered-example rejection, and drifted
status rejection.
