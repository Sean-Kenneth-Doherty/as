# Recipient Non-Init Command Source Status

Status: source-status decision, 2026-05-17.

ADR-0053 records why recipient-side non-init command-message inputs remain
blocked after the init-family recipient ladder was implemented, claimed,
traced, and rendered.

The structured status lives in
`sources/recipient_non_init_command_source_status.json`.

## Decision

Do not implement recipient-side non-init command-message execution yet.

`standard-signal` remains blocked because the formal command table includes it
as a command, while the legacy special-message sets exclude it and classify
standard signal input separately.

`write-buf-zero` and `write-buf-one` remain blocked because the legacy sketches
do not yet give AS a single stable boundary for fixed cells, stem cells, input
clearing, buffer clearing, and buffer-full behavior.

Multiple simultaneous command-message inputs also remain blocked because AS has
not selected a conflict policy.

## Safe Next Slice

The current runtime already rejects `standard-signal`, write-buffer, and
multi-command recipient inputs. ADR-0053 identified claim promotion as the
safe next slice because the rejection boundary needed to become explicit
before trace/render work could depend on it.

ADR-0054 completes that promotion as
`UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED`. ADR-0055 adds the
schematic-linked rejection trace in
`schematics/recipient_non_init_command_rejection_trace.json`. ADR-0056 adds
the rendered SVG view in
`schematics/recipient_non_init_command_rejection_trace.svg`.

The rejection evidence ladder is now complete. ADR-0057 records the
write-buffer command semantics source-status decision in
`sources/write_buffer_command_semantics_status.json` and keeps write-buffer
execution blocked across recipient, self-mailbox, and self-target
command-buffer surfaces.

The next safe slice is source resolution for `standard-signal` command-message
divergence, with multi-command conflict policy still blocked.

## Verification

Run:

```sh
python -m unittest tests.test_recipient_non_init_command_source_status
```

The tests check the blocking decision, implemented claim/trace/SVG/source-status
surfaces, standard-signal divergence, write-buffer source divergences,
multi-command policy boundary, and the updated source-status frontier.
