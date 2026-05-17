# Autarkic Systems

Autarkic Systems is the umbrella project for turning the Autarkic Formal
Systems research program into an organized theory and, where the theory is
ready, executable or simulable artifacts.

The lower-bound objective is an artificial entity that demonstrates cognitive
sovereignty: it should be able to reason about itself, its knowledge, and its
computational substrate without depending on opaque external authority as the
final source of confidence.

## Current Repository State

This repository is at its first scaffolding stage. The initial upstream commit
contains only `AGENTS.md` and its backup, so the first durable work is to make
the project legible:

- `docs/project-charter.md` defines the umbrella project, key terms, and
  near-term research obligations.
- `docs/subordinate-review.md` records the first review of the referenced
  subordinate repositories.
- `docs/glossary.md` defines working project vocabulary.
- `docs/afs-requirements.md` defines the first requirement matrix for
  Autarkic Formal Systems.
- `docs/source-manifest.md` explains the pinned source manifest in
  `sources/manifest.json`.
- `docs/literature-map.md` and `docs/open-problems.md` connect reviewed
  sources to AS claims and next ADRs.
- `docs/proof-apparatus-options.md` records the first proof-apparatus
  direction decision.
- `docs/transition-claim-language.md` explains the first explicit object
  language for transition claims.
- `docs/willard-definition-map.md` records the first definition-granularity map
  of Willard anchors needed for formal-confidence claims.
- `docs/proflog-frontier-status.md` records why public Proflog main is not a
  dependency-ready AS proof apparatus.
- `docs/prc-hardware-witness-map.md` records the first source-backed
  hardware/schematic evidence path for PRC-derived work.
- `docs/single-node-schematic-trace.md` records the first schematic-linked
  Universal Cell transition trace.
- `docs/single-node-schematic-svg.md` records the first rendered view of that
  structured schematic trace.
- `docs/processor-memory-toggle-trace.md` records the second schematic-linked
  Universal Cell trace, covering processor memory toggle behavior.
- `docs/processor-memory-toggle-svg.md` records the rendered view of that
  processor memory-toggle trace.
- `docs/stem-automail-reconfiguration-trace.md` records the third
  schematic-linked Universal Cell trace, covering one stem automail
  reconfiguration.
- `docs/stem-automail-reconfiguration-svg.md` records the rendered view of that
  stem automail reconfiguration trace.
- `docs/stem-buffer-accumulation.md` records the first standard-signal stem
  buffer accumulation behavior.
- `docs/stem-buffer-claim.md` records the named claim and proof-certificate
  surface for that buffer behavior.
- `docs/stem-buffer-accumulation-trace.md` records the schematic-linked trace
  for one matching stem buffer append.
- `docs/stem-buffer-accumulation-svg.md` records the rendered view of that stem
  buffer append trace.
- `docs/stem-command-buffer-map.md` records the source-backed five-bit stem
  command-buffer decoding map.
- `claims/transition_claims.json` names the current executable transition
  claims and examples.
- `claims/proof_certificates.json` adds the first tiny proof certificates over
  those transition claims.
- `sources/willard_definition_map.json` makes the Willard anchor map
  machine-checkable.
- `sources/proflog_frontier_status.json` makes the Proflog source-status
  decision machine-checkable.
- `sources/prc_hardware_witness_map.json` makes the PRC hardware/schematic
  witness map machine-checkable.
- `sources/stem_command_buffer_map.json` makes the PRC stem command-buffer
  target/command map machine-checkable.
- `schematics/single_node_triangular_rlem_trace.json` makes the first
  schematic-linked transition trace machine-checkable.
- `schematics/single_node_triangular_rlem_trace.svg` is the generated rendered
  view checked against the JSON trace.
- `schematics/processor_memory_toggle_trace.json` makes the processor
  memory-toggle schematic trace machine-checkable.
- `schematics/processor_memory_toggle_trace.svg` is the generated rendered
  view checked against the processor JSON trace.
- `schematics/stem_automail_reconfiguration_trace.json` makes the stem
  automail reconfiguration schematic trace machine-checkable.
- `schematics/stem_automail_reconfiguration_trace.svg` is the generated
  rendered view checked against the stem JSON trace.
- `schematics/stem_buffer_accumulation_trace.json` makes the stem buffer
  accumulation schematic trace machine-checkable.
- `schematics/stem_buffer_accumulation_trace.svg` is the generated rendered
  view checked against the stem buffer JSON trace.
- `docs/roadmap.md` maps the first sequence of ADR-scoped work.
- `docs/adr/` holds Architecture Decision Records and their after-action
  follow-ups.
- `LOG.md` is the chronological development spine.
- `MEMORY.md` preserves the few facts that should remain present in future
  working context.
- `LESSONS.md` records durable lessons learned while working this project.

## Fast Verification

```sh
python -m unittest discover
```

The current executable probes live in `autarkic_systems/universal_cell.py` and
`autarkic_systems/transition_predicates.py`, with claim-manifest,
proof-certificate, and object-language support in
`autarkic_systems/claim_manifest.py`, `autarkic_systems/proof_certificates.py`,
`autarkic_systems/object_language.py`, and
`autarkic_systems/willard_map.py`. Source-backed structured maps also live in
`autarkic_systems/prc_hardware_map.py` and
`autarkic_systems/stem_command_map.py`, with schematic-linked trace support in
`autarkic_systems/schematic_trace.py` and generated SVG support in
`autarkic_systems/schematic_svg.py`. They are covered by `tests/`.

## Subordinate Programs

Autarkic Systems currently subsumes three named programs:

- Autarkic Formal Systems (`jpt4/afs`): the immediate formal-systems layer.
  At the reviewed snapshot it is only a placeholder README, so this repository
  must supply the first serious integration structure.
- Pervasively Reconfigurable Computing (`jpt4/prc`): the embodied computing
  substrate. It studies Universal Cells, geometrically explicit logic circuits,
  reversible logic elements with memory, explicit routing, and physically
  grounded reconfiguration.
- Self-Justifying Axiom Systems (`jpt4/sjas`): the formal-confidence substrate.
  It studies Willard-style self-justifying axiom systems, self-provability of
  consistency under tuned expressivity, and executable fragments in Racket,
  Clojure/core.logic, and Proflog-adjacent work.

## Development Discipline

Follow `AGENTS.md` before changing this repository. In brief:

- ADRs precede feature implementation.
- Tests precede code when code is added.
- Documentation belongs in the right layer: `LOG.md` for chronology,
  `MEMORY.md` for high-priority future context, `LESSONS.md` for durable
  lessons, and README files for current entrypoints.
- Branches should follow the ADR structure of the work.

The default branch is currently `main`, even though `AGENTS.md` refers to
`master` in its generic branch-discipline text. Until the repository owner
changes the remote default branch, use `main` as the integration branch while
preserving the ADR-shaped branch flow.
