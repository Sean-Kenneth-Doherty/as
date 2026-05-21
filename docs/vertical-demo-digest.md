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
ADR-0215 also carries this digest into `python -m autarkic_systems.handoff` so
the end-of-month submission report includes the reader-facing demonstration
summary alongside project-status and GitHub submission evidence.
ADR-0216 extends the digest with the concrete evidence trail from
`autarkic_systems.network_sequence_demo`: sequence claim/proof/language
artifacts, witness implementation, trace, SVG, underlying chain bundle, and
source-status records, each with an existence flag in JSON.
ADR-0217 adds `reproduction_commands`, the short command list for rerunning
the vertical demo, focused network-sequence demo JSON, compact project status,
and refreshed handoff.
ADR-0294 adds `formal_confidence_validation`, a compact read-through of the
derived formal-confidence validation summary already exposed by project
status. When project status supplies the top-level summary, the digest reuses
it; narrowed older status payloads may still derive the same counts and
accepted frontier labels from nested `formal_confidence.results`.

The accepted current text output reports:

- 11 transition evidence bundles;
- 2 transition-chain evidence bundles;
- 1 network-sequence evidence bundle;
- 16 transition claims with 40 matched examples;
- 2 chain claims and 1 sequence claim;
- 52 `predicate-result` proof steps and 0 `manifest-example` proof steps;
- 19 accepted and 0 failed formal-confidence validations, including
  `fixed_point_construction_frontier_status accepted`;
- the remaining `standard-signal` command-token frontier; and
- `evidence/sequences/post_handoff_signal_bundle.json` as the sequence bundle
  tying the currently checked end-to-end path together.

The evidence trail currently includes:

- `claims/network_sequence_claims.json`;
- `claims/network_sequence_proof_certificates.json`;
- `language/network_sequence_claim_language.json`;
- `autarkic_systems/network_sequence_claims.py`;
- `autarkic_systems/network_sequence.py`;
- `schematics/sequences/post_handoff_signal_sequence_trace.json`;
- `schematics/sequences/post_handoff_signal_sequence_trace.svg`;
- `evidence/chains/neighbor_delivery_chain_bundle.json`; and
- the source-status records that constrain command execution boundaries.

The reproduction command list currently includes:

- `python -m autarkic_systems.vertical_demo`;
- `python -m autarkic_systems.network_sequence_demo --format json`;
- `python -m autarkic_systems.project_status --format summary`; and
- `python -m autarkic_systems.handoff --refresh-remotes`.

## Boundary

This digest is an operator/readability layer. It does not change runtime
behavior, claims, proof rules, source-status decisions, evidence registries,
project-status schema, formal-confidence validation semantics, traces, SVG
renders, scheduler, topology, timing, or command semantics.
