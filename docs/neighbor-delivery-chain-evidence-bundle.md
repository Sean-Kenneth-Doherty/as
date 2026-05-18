# Neighbor Delivery Chain Evidence Bundles

ADR-0081 adds the first transition-chain evidence bundle. It lives at
`evidence/chains/neighbor_delivery_chain_bundle.json` and is validated by
`autarkic_systems/chain_evidence_bundle.py`.
ADR-0094 adds the matching rejection-chain evidence bundle at
`evidence/chains/neighbor_delivery_rejection_chain_bundle.json`.

## Evidence Surface

The consumed-chain bundle ties the ADR-0077 through ADR-0080 chain stack into
one inspectable artifact:

- chain claim `UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED`;
- predicate `neighbor_delivery_consumed_by_recipient`;
- positive example `neighbor b proc left delivery consumed by empty recipient`;
- chain helper `execute_neighbor_delivery_recipient_chain`;
- chain proof certificate and chain object-language manifest;
- chain trace `schematics/chains/neighbor_delivery_recipient_chain_trace.json`;
- chain SVG `schematics/chains/neighbor_delivery_recipient_chain_trace.svg`;
- the neighbor command-buffer delivery transition bundle; and
- the recipient init command-message transition bundle.

The rejection-chain bundle ties the ADR-0091 through ADR-0093 rejection stack
into the same evidence surface:

- chain claim `UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-REJECTED`;
- predicate `neighbor_delivery_rejected_by_recipient`;
- positive example `neighbor c write buffer delivery rejected by recipient`;
- chain trace `schematics/chains/neighbor_delivery_rejection_chain_trace.json`;
- chain SVG `schematics/chains/neighbor_delivery_rejection_chain_trace.svg`;
- the neighbor command-buffer delivery transition bundle; and
- the recipient non-init command rejection transition bundle.

Both bundles also record the source-status files that keep full stem command
execution, recipient non-init command execution, `standard-signal` command
tokens, and write-buffer command tokens blocked.

## Boundary

This is composed-chain evidence, not a new single-transition evidence bundle.
It is deliberately stored under `evidence/chains/` instead of beside
`evidence/manifest.json`, whose closed index is for single-transition
`*_bundle.json` files.

The chain evidence bundles do not add a scheduler, topology model, multi-cell
timing semantics, non-init recipient command execution, `standard-signal`
command-token execution, or write-buffer command-token execution.

## Verification

Run:

```sh
python -m unittest tests.test_neighbor_delivery_chain_evidence_bundle
python -m unittest tests.test_neighbor_delivery_rejection_chain_evidence_bundle
python -m autarkic_systems.chain_evidence_bundle
python -m autarkic_systems.chain_evidence_bundle --format json
python -m autarkic_systems.chain_evidence_bundle --bundle evidence/chains/neighbor_delivery_rejection_chain_bundle.json --format json
python -m autarkic_systems.chain_evidence_bundle --registry evidence/chains/manifest.json
python -m autarkic_systems.chain_demo
```

The validator checks schema, executable chain example status, chain predicate
acceptance, chain proof certificate verification, chain language validation,
chain trace validation, chain SVG validation, both underlying transition evidence bundles,
source-status JSON, and boundary terms.

ADR-0088 adds `failed_subjects` to the single-bundle JSON payload so failed
bundle validation reports rejected validation subjects directly.

ADR-0089 adds `python -m autarkic_systems.chain_demo` as a first-run report
over the same validated bundle, claim, trace, SVG, transition-bundle, and
source-status surface.
ADR-0090 makes that report explicit about artifact presence with per-layer
`exists` flags and a `missing_evidence_paths` summary.

ADR-0084 adds the chain evidence registry so these bundles are discoverable and
batch-validatable without merging them into the single-transition evidence
registry.
ADR-0094 registers the rejection bundle in that registry.
