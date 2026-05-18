# Post-Handoff Sequence SVG

ADR-0207 adds a checked SVG view for the accepted post-handoff sequence trace.

## Purpose

The JSON trace records the accepted sequence precisely, but it is not an easy
first inspection surface. The SVG renders the same trace as a visual artifact
while keeping the JSON trace and sequence helper as the source of truth.

## Artifact

The checked SVG is:

```text
schematics/sequences/post_handoff_signal_sequence_trace.svg
```

It is rendered from:

```text
schematics/sequences/post_handoff_signal_sequence_trace.json
```

## Validation

`autarkic_systems.network_sequence_svg` validates:

- SVG XML shape;
- trace artifact ID, sequence claim ID, and helper metadata;
- exact renderer output;
- visible delivery, follow-up, and recipient-state labels; and
- routed follow-up signal-flow text.

## Boundary

The SVG is not a scheduler, topology model, timing model, simulator, proof
rule, evidence-bundle field, or new command semantic. It is a deterministic
render of the checked sequence trace.
