# Vertical Chain Demo Report

ADR-0089 adds `autarkic_systems/chain_demo.py`, a compact first-run report for
the checked neighbor delivery recipient-consumption chain.

## Purpose

The transition-chain work is intentionally split across claims, proof
certificates, object-language manifests, traces, SVG renders, evidence bundles,
and source-status records. That split is good for audit, but it is awkward as a
demo surface.

The vertical chain demo report keeps the existing validator as the authority
and presents the current chain as one claim-to-evidence path.

## Run

```sh
python -m autarkic_systems.chain_demo
python -m autarkic_systems.chain_demo --format json
python -m autarkic_systems.chain_demo --registry evidence/chains/manifest.json
python -m autarkic_systems.chain_demo --registry evidence/chains/manifest.json --format json
```

For one bundle, the text report names:

- the chain evidence bundle;
- the transition-chain claim;
- the predicate, positive example, chain helper, and expected status;
- validation status, result count, and failed subjects;
- missing evidence paths, if any;
- the chain claim, proof, language, trace, and SVG artifacts;
- the underlying transition evidence bundles;
- the source-status boundaries; and
- the explicit boundary terms.

JSON mode emits the same surface for automation.
ADR-0090 adds an `exists` flag to every JSON evidence layer and a
`missing_evidence_paths` summary to both text and JSON output.

ADR-0095 adds registry mode. A registry report validates
`evidence/chains/manifest.json`, builds a demo report for every existing
registered bundle, and summarizes:

- registry ID;
- bundle count;
- accepted and failed counts;
- missing registered bundle paths or missing evidence-layer paths; and
- the per-bundle demo reports.

The current checked-in registry reports the consumed init handoff bundle and
the rejected non-init handoff bundle. If a registry entry points at a missing
bundle, the registry demo report returns structured failure output instead of
crashing.

## Boundary

This is not a new simulator, proof checker, or validation path. It delegates
validation to `autarkic_systems.chain_evidence_bundle` and exists only to make
the current vertical artifact legible from one command.
