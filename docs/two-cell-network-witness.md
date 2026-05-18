# Two-Cell Network Witness

ADR-0194 adds `autarkic_systems.network_witness`, a bounded operator witness
over the existing neighbor-delivery transition-chain behavior.

## Purpose

The transition-chain helper already proves one sender step can be composed with
one recipient step. The witness makes that composition inspectable as a
network-shaped execution record without introducing scheduler, timing, topology,
or output-clearing semantics.

## Run

```sh
python -m autarkic_systems.network_witness
python -m autarkic_systems.network_witness --case write-buffer-one-consumed
python -m autarkic_systems.network_witness --case standard-signal-rejected
python -m autarkic_systems.network_witness --case recipient-not-ready
python -m autarkic_systems.network_witness --case sender-not-delivered
python -m autarkic_systems.network_witness --format json
```

The checked fixture cases are:

- `init-consumed`: neighbor delivery of `proc-l-init` is installed as recipient
  upstream and consumed by recipient init-command logic.
- `write-buffer-one-consumed`: neighbor delivery of `write-buf-one` is installed
  as recipient upstream and consumed by recipient write-buffer append logic.
- `standard-signal-rejected`: neighbor delivery of `standard-signal` is
  installed as recipient upstream and rejected by the existing recipient non-init
  boundary.
- `recipient-not-ready`: neighbor delivery is produced by the sender, but the
  recipient already has pending upstream state, so no delivery is installed and
  no recipient step is run.
- `sender-not-delivered`: the sender executes a stem buffer append rather than a
  neighbor delivery, so no handoff or recipient step is run.

## Payload

JSON output contains:

- `schema_version: 1`;
- accepted state and witness status;
- sender before and sender after the sender step;
- recipient before, optional recipient before its step, and recipient after;
- the delivered tuple if installation occurred; and
- ordered events for sender step, handoff or blocked handoff, and recipient
  step when one ran.

## Boundary

This is not a general multi-cell simulator. It does not decide global
scheduling, timing, output-lifetime, or topology rules. It reuses the already
checked `execute_neighbor_delivery_recipient_chain` behavior and records the
result as an explicit two-cell witness.
