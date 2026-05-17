# Self-Mailbox Init Evidence Bundle

ADR-0072 adds `evidence/self_mailbox_init_bundle.json`, the fourth AS
transition evidence bundle.

The bundle covers the positive `UC-STEM-SELF-MAILBOX-INIT-COMMAND` example
named `processor left mailbox init`, where a stem-right cell with
`self_mailbox` set to `proc-l-init` reconfigures into a processor with left
memory and clears the consumed self-mailbox, control, and buffer state.

## Evidence Path

The bundle points to:

- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/self_mailbox_init_trace.json`;
- `schematics/self_mailbox_init_trace.svg`;
- `sources/prc_hardware_witness_map.json`;
- `sources/stem_command_execution_source_status.json`;
- `sources/recipient_non_init_command_source_status.json`;
- `sources/standard_signal_command_semantics_status.json`; and
- `sources/write_buffer_command_semantics_status.json`.

The evidence bundle validator checks that the claim example evaluates true,
the proof certificate is accepted, the schematic trace executes and matches
the exact claim example, the committed SVG matches renderer output, and the
source-status boundary files remain present and parseable.

## Boundary

The bundle records direct self-mailbox init-family execution only. It does not
add non-init self-mailbox execution, recipient non-init command execution,
`standard-signal` command-token execution, or write-buffer command-token
execution.

## Verification

Run:

```sh
python -m unittest tests.test_self_mailbox_init_evidence_bundle
python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json
```

The tests cover the bundle fields, path set, cross-layer validation, registry
entry, and drifted trace-path rejection.
