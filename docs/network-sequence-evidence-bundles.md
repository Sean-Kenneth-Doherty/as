# Network Sequence Evidence Bundles

ADR-0198 adds a dedicated evidence-bundle surface for post-handoff network
sequence witnesses.

## Purpose

Transition evidence bundles cover one transition. Transition-chain evidence
bundles cover the existing two-step neighbor-delivery chain claim surface. The
post-handoff signal witness is a different object: it composes an accepted
delivery witness with one later recipient follow-up step.

The network-sequence evidence bundle makes that object auditable without
pretending it is a scheduler, topology model, or new command semantic.

## Run

```sh
python -m autarkic_systems.network_sequence_evidence_bundle
python -m autarkic_systems.network_sequence_evidence_bundle --format json
python -m autarkic_systems.network_sequence_evidence_bundle --registry evidence/sequences/manifest.json
python -m autarkic_systems.network_sequence_evidence_bundle --registry evidence/sequences/manifest.json --format json
```

The checked bundle is
`evidence/sequences/post_handoff_signal_bundle.json`, registered by
`evidence/sequences/manifest.json`.

## Validation

The validator checks:

- bundle schema and artifact paths;
- the named network-sequence claim example;
- network-sequence proof certificates;
- the network-sequence claim object language;
- the executable post-handoff witness status;
- the checked post-handoff sequence trace;
- the checked post-handoff sequence SVG;
- underlying transition-chain evidence bundles;
- referenced source-status JSON files; and
- explicit boundary text.

Registry JSON exposes both registry-level `failed_subjects` and
`bundle_failed_subjects`. The latter is an ordered list of loadable registered
bundle IDs with their rejected inner bundle subjects, so automation can see
whether a registered existing bundle failed at `sequence-witness`,
`sequence-trace`, `sequence-svg`, or another evidence layer without parsing
the `registry-bundle-validation` detail string.

## Boundary

ADR-0199 makes this registry part of aggregate project status through
`sequence_evidence`. It remains the first evidence bundle over the
ADR-0196/ADR-0197 post-handoff sequence surface, preserving the same boundary:
no scheduler, topology, timing, output clearing, queued delivery, or new
command semantics.
