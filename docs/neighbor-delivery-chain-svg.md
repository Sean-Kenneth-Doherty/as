# Neighbor Delivery Chain SVG

ADR-0083 adds the first rendered view of a composed transition-chain trace:
`schematics/chains/neighbor_delivery_recipient_chain_trace.svg`.

The SVG is generated from
`schematics/chains/neighbor_delivery_recipient_chain_trace.json` by
`autarkic_systems/chain_svg.py`. The checked-in SVG must exactly match the
renderer output, so the visual cannot drift away from the chain trace.

## View

The view exposes:

- sender step `sender-neighbor-delivery`;
- recipient step `recipient-init-consumption`;
- whole-chain status `neighbor-delivery-consumed`;
- handoff `sender output[1] -> recipient upstream[1]`;
- delivered tuple `[_, proc-l-init, _]`;
- sender routed signal flow; and
- recipient routed signal flow.

## Verification

Run:

```sh
python -m unittest tests.test_neighbor_delivery_chain_svg
python -m autarkic_systems.chain_evidence_bundle
```

The SVG validator parses XML metadata, checks exact renderer output, checks
visible sender/recipient/status/tuple labels, and checks that the handoff and
both step flows are visible.

## Boundary

This is a two-cell visual for the current recorded chain. It is not a general
graph renderer and does not add scheduler, topology, multi-cell timing,
non-init command execution, `standard-signal` command-token execution, or
write-buffer command-token execution.
