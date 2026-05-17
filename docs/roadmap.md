# Initial Roadmap

This roadmap is intentionally ADR-shaped. It should change as source review and
experiments improve the project model.

## ADR-0001: Project Orientation Scaffold

Goal: make the newborn AS repository navigable and source-backed.

Deliverables:

- public README;
- chronological log;
- memory and lessons files;
- project charter;
- subordinate repository review;
- first roadmap.

Success criteria:

- every named subordinate program in `AGENTS.md` is represented;
- reviewed repository snapshots are recorded;
- near-term work can proceed without relying on unstated context.

## ADR-0002: AFS Requirement Definition

Goal: define "Autarkic Formal System" as a concrete project object.

Candidate outputs:

- glossary of core terms;
- AFS requirement matrix connecting formal confidence, substrate visibility,
  reconfiguration, and executable evidence;
- explicit non-goals for the first month.

Key questions:

- What must an AFS prove, simulate, or preserve to deserve the name?
- Which claims belong in AS vs. PRC vs. SJAS?
- What is the smallest formal object that can be implemented and tested?

Status: accepted in `docs/adr/0002-afs-requirements.md`. The first answer is
recorded in `docs/afs-requirements.md`; the recommended first executable probe
is a tiny substrate/formal bridge around one Universal Cell transition
invariant.

## ADR-0003: Subordinate Artifact Manifest

Goal: create a reproducible manifest of subordinate material and open gaps.

Candidate outputs:

- machine-readable source manifest for AFS/PRC/SJAS snapshots;
- literature/artifact coverage table;
- known-bad or incomplete artifact list;
- policy for vendoring, submodules, or external pointers.

Key questions:

- Should AS pin subordinate commits?
- Which artifacts are canonical enough to build against?
- Where does recent Proflog SJAS work live relative to `jpt4/sjas`?

Status: accepted in `docs/adr/0003-source-manifest.md`. The first manifest is
`sources/manifest.json`, with notes in `docs/source-manifest.md`.

## ADR-0004: First Executable Probe

Goal: pick one tiny artifact that tests the AS integration story.

Candidate directions:

- a Universal Cell transition verifier around PRC's `asmsim.scm`;
- a minimal Type NS grammar/checker extracted from SJAS's ISLA/theta work;
- a formal interface specification between a toy substrate transition system
  and a toy self-confidence predicate.

Gate:

- strict red-green tests must precede code;
- coverage limits must be documented;
- slow checks must be split from fast checks.

Status: accepted in `docs/adr/0004-universal-cell-transition-probe.md`.
Implemented the first substrate-side probe in `autarkic_systems/universal_cell.py`
with fast tests under `tests/test_universal_cell.py`.

## ADR-0005: Transition Predicate Bridge

Goal: name and check the first substrate invariants as predicate results.

Deliverables:

- predicate result object;
- output preservation predicate;
- consumed-input clearing predicate;
- fixed-role memory predicate;
- stem-init reset predicate;
- fast tests covering true and false cases.

Status: accepted in `docs/adr/0005-transition-predicates.md`. Implemented in
`autarkic_systems/transition_predicates.py` with tests under
`tests/test_transition_predicates.py`.

## ADR-0006: Literature Map And Open Problems

Goal: turn the first review into a usable research map.

Candidate outputs:

- annotated bibliography by role: formal logic, self-reference,
  self-interpretation, reconfigurable hardware, reversible/asynchronous
  computing, and agent architecture;
- dependency graph from sources to claims;
- ranked open questions that can generate executable probes.

Status: accepted in `docs/adr/0006-literature-map.md`. The first map is
`docs/literature-map.md`; ranked project questions are in
`docs/open-problems.md`.

## ADR-0007: Transition Claim Manifest

Goal: make the current transition predicates machine-readable AS claims.

Deliverables:

- JSON claim manifest;
- loader/evaluator for manifest examples;
- positive and negative executable examples for every claim;
- tests proving manifest examples match predicate outcomes.

Status: accepted in `docs/adr/0007-transition-claim-manifest.md`. Implemented
in `claims/transition_claims.json` and `autarkic_systems/claim_manifest.py`,
with tests in `tests/test_claim_manifest.py`.

## ADR-0008: Stem Automail Probe

Goal: add the first executable stem/reconfiguration slice.

Deliverables:

- stem-state fields for automail, control, and buffer;
- `step_stem_cell` automail transition subset;
- tests for `wr`, `wl`, `pr`, `pl`, idle no-mail behavior, output blocking,
  and invalid automail values;
- explicit non-goals for full stem buffer processing.

Status: accepted in `docs/adr/0008-stem-automail-probe.md`. Implemented in
`autarkic_systems/universal_cell.py` with tests in
`tests/test_stem_automail.py`.

## ADR-0009: Stem Automail Claim

Goal: promote stem automail reconfiguration into the named claim surface.

Deliverables:

- `automail_reconfigures_stem` predicate;
- transition claim manifest entry;
- positive and negative executable examples;
- manifest-loader support for stem fields.

Status: accepted in `docs/adr/0009-stem-automail-claim.md`. Implemented in
`autarkic_systems/transition_predicates.py`, `claims/transition_claims.json`,
and `autarkic_systems/claim_manifest.py`.

## ADR-0010: Proof Apparatus Options

Goal: choose the first proof-side apparatus direction before implementing proof
objects.

Deliverables:

- comparison of Proflog/Fitting, LeanTAP, and a minimal AS-local checker;
- source-manifest and literature-map updates for LeanTAP;
- explicit next ADR shape for proof-certificate syntax.

Status: accepted in `docs/adr/0010-proof-apparatus-options.md`. The decision is
to start with a minimal AS-local proof-certificate checker, use LeanTAP as a
transparent reference, and defer public Proflog as a dependency until the
active SJAS/Proflog frontier is recovered or replaced.

## ADR-0011: Proof Certificate Checker

Goal: add the first proof-object layer over the current transition claims.

Deliverables:

- proof-certificate manifest tied to claim IDs;
- checker for `manifest-example` certificate steps;
- tests for accepted certificates and rejected unknown/mismatched certificates.

Status: accepted in `docs/adr/0011-proof-certificate-checker.md`. Implemented
in `claims/proof_certificates.json` and
`autarkic_systems/proof_certificates.py`, with tests in
`tests/test_proof_certificates.py`.

## ADR-0012: Transition Claim Object Language

Goal: make the first AS claim language explicit instead of implicit in Python
loaders and JSON shapes.

Deliverables:

- transition-claim language manifest;
- object-language validator;
- tests for required syntax classes, current claim/certificate coverage, and
  rejected unknown syntax.

Status: accepted in `docs/adr/0012-transition-claim-language.md`. Implemented
in `language/transition_claim_language.json` and
`autarkic_systems/object_language.py`, with tests in
`tests/test_object_language.py`.

## ADR-0013: Willard Definition Map

Goal: anchor the formal-confidence side of AS to exact Willard definitions,
constructions, theorem statements, and boundary results.

Deliverables:

- structured Willard anchor map for the four core sources named by P5;
- loader and validator for local witness paths, uniqueness, and AS relevance;
- human-facing definition map;
- tests proving required source coverage.

Status: accepted in `docs/adr/0013-willard-definition-map.md`. Implemented in
`sources/willard_definition_map.json` and `autarkic_systems/willard_map.py`,
with tests in `tests/test_willard_definition_map.py`.

## ADR-0014: Proflog Source Status

Goal: decide whether public `jpt4/proflog` main can be treated as the active
SJAS/Proflog frontier or an AS dependency.

Deliverables:

- structured source-status artifact for public Proflog;
- human-readable source-status note and maintainer question;
- tests proving the decision, public head, missing frontier terms, and smoke
  failure are recorded.

Status: accepted in `docs/adr/0014-proflog-source-status.md`. Implemented in
`sources/proflog_frontier_status.json` and
`docs/proflog-frontier-status.md`, with tests in
`tests/test_proflog_frontier_status.py`.

## ADR-0015: PRC Hardware Witness Map

Goal: define the source-backed hardware/schematic evidence path before AS draws
or simulates PRC-derived hardware.

Deliverables:

- structured PRC hardware witness map;
- loader and validator for required witness coverage, PRC-local path pinning,
  AS relevance, and simulation constraints;
- human-facing hardware witness note;
- recommended next artifact for a single-node triangular RLEM schematic and UC
  transition trace.

Status: accepted in `docs/adr/0015-prc-hardware-witness-map.md`. Implemented
in `sources/prc_hardware_witness_map.json` and
`autarkic_systems/prc_hardware_map.py`, with tests in
`tests/test_prc_hardware_witness_map.py`.

## ADR-0016: Single-Node Schematic Trace

Goal: implement ADR-0015's recommended next artifact as a structured
schematic-linked Universal Cell transition trace.

Deliverables:

- single-node triangular RLEM/Universal Cell schematic artifact;
- loader and validator for ports, interpretive layers, PRC witness references,
  Cell field coverage, and executable transition replay;
- human-facing note for the schematic key and trace;
- tests proving the recorded transition matches the existing AS Universal Cell
  probe.

Status: accepted in `docs/adr/0016-single-node-schematic-trace.md`.
Implemented in `schematics/single_node_triangular_rlem_trace.json` and
`autarkic_systems/schematic_trace.py`, with tests in
`tests/test_single_node_schematic_trace.py`.

## ADR-0017: Single-Node Schematic SVG

Goal: render the ADR-0016 structured schematic trace as a visible SVG while
keeping the JSON artifact authoritative.

Deliverables:

- SVG renderer for `SingleNodeSchematicTrace`;
- checked-in SVG view generated from the JSON trace;
- human-facing note for the render boundary;
- tests proving the committed SVG is parseable, nonblank, source-linked, and
  identical to renderer output.

Status: accepted in `docs/adr/0017-single-node-schematic-svg.md`. Implemented
in `schematics/single_node_triangular_rlem_trace.svg` and
`autarkic_systems/schematic_svg.py`, with tests in
`tests/test_single_node_schematic_svg.py`.

## ADR-0018: Processor Memory Toggle Trace

Goal: add a second schematic-linked Universal Cell trace covering processor
routing and memory toggle behavior.

Deliverables:

- processor memory-toggle schematic trace artifact;
- generic schematic-trace loader and validator path while preserving the
  ADR-0016 single-node wrapper;
- human-facing note for the processor trace;
- tests proving schema reuse, left-memory signal flow, executable replay, and
  rejection of a drifted expected memory.

Status: accepted in `docs/adr/0018-processor-memory-toggle-trace.md`.
Implemented in `schematics/processor_memory_toggle_trace.json` and
`autarkic_systems/schematic_trace.py`, with tests in
`tests/test_processor_memory_toggle_trace.py`.

## ADR-0019: Stem Automail Reconfiguration Trace

Goal: add a third schematic-linked Universal Cell trace covering the first stem
automail reconfiguration subset.

Deliverables:

- stem automail schematic trace artifact;
- validator support for stem automail target role, target memory, automail
  consumption, and recorded reconfiguration flow;
- human-facing note for the stem trace boundary;
- tests proving schema reuse, executable replay through `step_stem_cell`, and
  rejection of drifted target role or automail consumption.

Status: accepted in `docs/adr/0019-stem-automail-reconfiguration-trace.md`.
Implemented in `schematics/stem_automail_reconfiguration_trace.json` and
`autarkic_systems/schematic_trace.py`, with tests in
`tests/test_stem_automail_reconfiguration_trace.py`.

## ADR-0020: Processor Memory Toggle SVG

Goal: render the ADR-0018 processor memory-toggle trace as a checked SVG while
keeping the JSON artifact authoritative.

Deliverables:

- generic schematic SVG renderer/validator path for structured traces;
- checked-in processor memory-toggle SVG generated from the JSON trace;
- human-facing note for the processor render boundary;
- tests proving source metadata, ports, layers, processor role, memory
  before/after, routed flow, exact renderer match, and drift rejection.

Status: accepted in `docs/adr/0020-processor-memory-toggle-svg.md`.
Implemented in `schematics/processor_memory_toggle_trace.svg` and
`autarkic_systems/schematic_svg.py`, with tests in
`tests/test_processor_memory_toggle_svg.py`.

## ADR-0021: Stem Automail SVG

Goal: render the ADR-0019 stem automail reconfiguration trace as a checked SVG
while keeping the JSON artifact authoritative.

Deliverables:

- stem SVG artifact generated from the JSON trace;
- generic schematic SVG support for reconfiguration summary fields;
- human-facing note for the stem render boundary;
- tests proving source metadata, ports, layers, stem/proc role change,
  memory before/after, automail before/after, automail flow, exact renderer
  match, and drift rejection.

Status: accepted in `docs/adr/0021-stem-automail-svg.md`. Implemented in
`schematics/stem_automail_reconfiguration_trace.svg` and
`autarkic_systems/schematic_svg.py`, with tests in
`tests/test_stem_automail_svg.py`.

## ADR-0022: Stem Buffer Accumulation

Goal: add the first PRC source-backed standard-signal buffer behavior to
`step_stem_cell` without pretending to implement full command execution.

Deliverables:

- one-hot stem input control-rail selection;
- matching/non-matching one-hot input append behavior for a non-full buffer;
- explicit full-buffer boundary status;
- malformed stem-input rejection;
- human-facing note for the implemented subset and remaining boundary;
- tests proving the new behavior and automail priority.

Status: accepted in `docs/adr/0022-stem-buffer-accumulation.md`. Implemented in
`autarkic_systems/universal_cell.py`, with tests in
`tests/test_stem_buffer_accumulation.py`.

## ADR-0023: Stem Buffer Claim

Goal: promote ADR-0022 stem buffer accumulation into the named transition-claim
and proof-certificate surface.

Deliverables:

- `stem_buffer_accumulates` predicate;
- `UC-STEM-BUFFER-ACCUMULATES` claim manifest entry;
- proof-certificate manifest entry for the new claim examples;
- object-language predicate vocabulary update;
- human-facing note for the claim boundary;
- tests covering predicate, claim manifest, proof certificates, and language
  vocabulary.

Status: accepted in `docs/adr/0023-stem-buffer-claim.md`. Implemented in
`autarkic_systems/transition_predicates.py`,
`claims/transition_claims.json`, and `claims/proof_certificates.json`, with
tests in `tests/test_transition_predicates.py`.

## ADR-0024: Stem Buffer Accumulation Trace

Goal: add a schematic-linked trace for one ADR-0022 matching-input stem buffer
append while preserving existing automail trace validation.

Deliverables:

- structured stem buffer accumulation trace artifact;
- validator branch that distinguishes stem automail from stem buffer traces;
- human-facing trace boundary note;
- tests proving schema reuse, executable replay, buffer flow, and rejection of
  drifted expected buffer or flow.

Status: accepted in `docs/adr/0024-stem-buffer-accumulation-trace.md`.
Implemented in `schematics/stem_buffer_accumulation_trace.json` and
`autarkic_systems/schematic_trace.py`, with tests in
`tests/test_stem_buffer_accumulation_trace.py`.

## ADR-0025: Stem Buffer Accumulation SVG

Goal: render the ADR-0024 stem buffer accumulation trace as a checked SVG while
keeping the JSON artifact authoritative.

Deliverables:

- stem buffer SVG artifact generated from the JSON trace;
- generic schematic SVG support for buffer/control summary fields;
- human-facing note for the stem buffer render boundary;
- tests proving source metadata, ports, layers, control rail, buffer
  before/after, cleared input, exact renderer match, and drift rejection.

Status: accepted in `docs/adr/0025-stem-buffer-accumulation-svg.md`.
Implemented in `schematics/stem_buffer_accumulation_trace.svg` and
`autarkic_systems/schematic_svg.py`, with tests in
`tests/test_stem_buffer_svg.py`.

## ADR-0026: Stem Command Buffer Map

Goal: make PRC's five-bit stem command-buffer target/command encoding explicit
before implementing command execution.

Deliverables:

- structured command-buffer map artifact;
- loader, validator, and five-bit decoder;
- human-facing note for bit-order and execution boundary;
- tests proving source anchoring, 32-value coverage, representative decodes,
  and rejection of malformed buffers or incomplete maps.

Status: accepted in `docs/adr/0026-stem-command-buffer-map.md`. Implemented in
`sources/stem_command_buffer_map.json` and
`autarkic_systems/stem_command_map.py`, with tests in
`tests/test_stem_command_buffer_map.py`.

## ADR-0027: Stem Command Execution Source Status

Goal: block premature full command execution by recording the source-status
gaps between the formal command table, formal process-buffer sketch, and legacy
simulator divergences.

Deliverables:

- structured command-execution source-status artifact;
- human-facing source-status note;
- tests proving the blocking decision, ADR-0026 command-table dependency,
  legacy divergences, and narrower allowed next slices.

Status: accepted in `docs/adr/0027-stem-command-execution-source-status.md`.
Implemented in `sources/stem_command_execution_source_status.json` and
`docs/stem-command-execution-source-status.md`, with tests in
`tests/test_stem_command_execution_source_status.py`.

## ADR-0028: Self Mailbox Representation

Goal: add the explicit self mailbox state needed by PRC's process-buffer sketch
without implementing command-buffer execution.

Deliverables:

- `Cell.self_mailbox` field and validation;
- claim-manifest, object-language, and schematic-trace support for the field;
- updated checked schematic trace JSON artifacts that still map every Cell
  field;
- tests proving defaults, accepted command IDs, invalid-value rejection,
  reset-clearing, non-execution preservation, and parser/language/trace
  exposure.

Status: accepted in `docs/adr/0028-self-mailbox-representation.md`.
Implemented in `autarkic_systems/universal_cell.py`,
`autarkic_systems/claim_manifest.py`, `autarkic_systems/object_language.py`,
`autarkic_systems/schematic_trace.py`, and checked trace artifacts, with tests
in `tests/test_self_mailbox_representation.py`.

## ADR-0029: Command Channel Token Representation

Goal: allow channel tuples to represent ADR-0026 command-message tokens without
executing or routing command buffers.

Deliverables:

- expanded Universal Cell channel-token vocabulary;
- transition-claim language `signals` update;
- tests proving command-message output representation, blocked-output
  preservation, command-message input rejection without execution, continued
  `si` stem-init behavior, and object-language validation.

Status: accepted in `docs/adr/0029-command-channel-token-representation.md`.
Implemented in `autarkic_systems/universal_cell.py` and
`language/transition_claim_language.json`, with tests in
`tests/test_command_channel_tokens.py`.

## ADR-0030: Self Mailbox Init Commands

Goal: process the source-stable self-mailbox init-family command subset without
implementing full command-buffer execution.

Deliverables:

- self-mailbox handling for `stem-init`, `wire-r-init`, `wire-l-init`,
  `proc-r-init`, and `proc-l-init`;
- explicit unsupported boundary for `standard-signal`, `write-buf-zero`, and
  `write-buf-one`;
- transition-language statuses for processed and unsupported self-mailbox
  outcomes;
- tests proving init reconfiguration, reset clearing, unsupported preservation,
  output blocking, automail priority, and language status coverage.

Status: accepted in `docs/adr/0030-self-mailbox-init-commands.md`.
Implemented in `autarkic_systems/universal_cell.py` and
`language/transition_claim_language.json`, with tests in
`tests/test_self_mailbox_init_commands.py`.

## ADR-0031: Self Mailbox Init Claim

Goal: promote the ADR-0030 self-mailbox init-command execution subset into the
named transition-claim and proof-certificate surface.

Deliverables:

- `self_mailbox_executes_init_command` predicate;
- `UC-STEM-SELF-MAILBOX-INIT-COMMAND` manifest claim with positive and
  negative executable examples;
- proof-certificate coverage for the new claim;
- transition-language predicate vocabulary update;
- tests proving predicate behavior, manifest evaluation, certificate coverage,
  object-language validation, and preservation of omitted mailbox defaults.

Status: accepted in `docs/adr/0031-self-mailbox-init-claim.md`. Implemented in
`autarkic_systems/transition_predicates.py`,
`claims/transition_claims.json`, `claims/proof_certificates.json`, and
`language/transition_claim_language.json`, with tests in
`tests/test_self_mailbox_init_claim.py` and the refined default-preservation
test in `tests/test_self_mailbox_representation.py`.

## ADR-0032: Self Mailbox Init Trace

Goal: add a schematic-linked trace for one self-mailbox init command.

Deliverables:

- `schematics/self_mailbox_init_trace.json`;
- self-mailbox init artifact identity in the schematic-trace validator;
- validation that separates self-mailbox init from automail and buffer stem
  traces;
- tests for artifact identity, schema vocabulary, recorded mailbox flow,
  execution replay, witness-map validation, and drift rejection.

Status: accepted in `docs/adr/0032-self-mailbox-init-trace.md`. Implemented in
`autarkic_systems/schematic_trace.py` and
`schematics/self_mailbox_init_trace.json`, with tests in
`tests/test_self_mailbox_init_trace.py`.

## ADR-0033: Self Mailbox Init SVG

Goal: add a rendered SVG view of the ADR-0032 self-mailbox init trace.

Deliverables:

- `schematics/self_mailbox_init_trace.svg`;
- exported self-mailbox SVG artifact path;
- renderer summary fields for self-mailbox before/after and control/buffer
  clearing;
- tests proving parseability, trace metadata, port/layer annotations, visible
  mailbox details, exact renderer-output matching, and drift rejection.

Status: accepted in `docs/adr/0033-self-mailbox-init-svg.md`. Implemented in
`autarkic_systems/schematic_svg.py` and
`schematics/self_mailbox_init_trace.svg`, with tests in
`tests/test_self_mailbox_init_svg.py`.
