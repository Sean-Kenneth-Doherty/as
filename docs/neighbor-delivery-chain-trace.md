# Neighbor Delivery Chain Trace

ADR-0082 adds the first recorded transition-chain trace:
`schematics/chains/neighbor_delivery_recipient_chain_trace.json`.

The trace records the two-step handoff behind
`UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED`:

1. a stem sender completes `neighbor-b/proc-l-init` command-buffer delivery;
2. the sender output tuple `["_", "proc-l-init", "_"]` is installed as an
   empty recipient's upstream tuple; and
3. the recipient consumes `proc-l-init` through the existing init-family
   command-message transition.

## Validation

`autarkic_systems/chain_trace.py` loads and validates the trace. It checks the
sender step, handoff tuple, recipient step, whole-chain helper replay, and
boundary terms.

Run:

```sh
python -m unittest tests.test_neighbor_delivery_chain_trace
```

The trace is also validated by the composed-chain evidence bundle:

```sh
python -m autarkic_systems.chain_evidence_bundle
```

ADR-0083 adds the renderer-locked SVG view of this trace at
`schematics/chains/neighbor_delivery_recipient_chain_trace.svg`.

## Boundary

This is a trace artifact, not a renderer. It does not add SVG output,
scheduler semantics, graph topology, multi-cell timing, non-init command
execution, `standard-signal` command-token execution, or write-buffer
command-token execution.
