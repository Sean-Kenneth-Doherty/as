# Vertical Demo Digest

ADR-0214 adds `autarkic_systems/vertical_demo.py`, a top-level first-run digest
over the accepted AS evidence stack.

Run:

```sh
python -m autarkic_systems.vertical_demo
python -m autarkic_systems.vertical_demo --format json
```

The digest delegates acceptance to `autarkic_systems.project_status`; it does
not introduce independent validation authority. It summarizes the current
demonstration as post-handoff signal routing through checked evidence, then
names the evidence counts, claim counts, proof-rule mix, blocked command
frontier, canonical registries, and sequence evidence bundle behind that path.

The accepted current text output reports:

- 11 transition evidence bundles;
- 2 transition-chain evidence bundles;
- 1 network-sequence evidence bundle;
- 16 transition claims with 40 matched examples;
- 2 chain claims and 1 sequence claim;
- 52 `predicate-result` proof steps and 0 `manifest-example` proof steps;
- the remaining `standard-signal` command-token frontier; and
- `evidence/sequences/post_handoff_signal_bundle.json` as the sequence bundle
  tying the currently checked end-to-end path together.

## Boundary

This digest is an operator/readability layer. It does not change runtime
behavior, claims, proof rules, source-status decisions, evidence registries,
project-status schema, traces, SVG renders, scheduler, topology, timing, or
command semantics.
