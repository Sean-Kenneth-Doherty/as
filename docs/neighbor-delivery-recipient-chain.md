# Neighbor Delivery Recipient Chain

ADR-0077 adds `autarkic_systems/transition_chains.py`, a small executable
handoff from a stem neighbor-delivery transition into a recipient command
consumption transition.
ADR-0078 adds a named chain claim and proof-certificate surface for this
handoff.
ADR-0082 records the accepted handoff as a dedicated transition-chain trace.

The chain is intentionally narrower than a multi-cell simulator. It composes
one sender step and one recipient step:

1. run `step_stem_cell` on the sender;
2. require `stem-command-buffer-neighbor-delivered`;
3. copy the sender output tuple into an otherwise empty recipient upstream
   tuple;
4. run the recipient through its existing single-cell transition; and
5. accept only `recipient-init-command-message-processed`.

## Boundary

The chain proves that the already implemented delivery and recipient
init-family consumption slices compose. It does not add a graph topology,
timing model, multi-cell scheduler, non-init recipient command execution,
`standard-signal` command-token execution, or write-buffer command-token
execution.

If the sender does not deliver, the recipient is not empty, or the delivered
token is non-init, the helper reports an explicit rejected chain status rather
than silently executing or overwriting state.

## Verification

Run:

```sh
python -m unittest tests.test_neighbor_delivery_recipient_chain
python -m unittest tests.test_neighbor_delivery_chain_trace
```

The tests cover accepted `neighbor-b/proc-l-init` delivery into an empty fixed
recipient, sender precondition failure, recipient readiness failure, and
non-init delivered-token rejection.
