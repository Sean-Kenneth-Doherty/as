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
multi-command recipient inputs. The next safe slice is to promote that
rejection boundary into a named transition claim and proof-certificate entry,
without executing the blocked commands.

## Verification

Run:

```sh
python -m unittest tests.test_recipient_non_init_command_source_status
```

The tests check the blocking decision, standard-signal divergence,
write-buffer source divergences, multi-command policy boundary, and the updated
source-status frontier.
