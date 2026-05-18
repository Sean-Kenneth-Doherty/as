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

## ADR-0034: Self Mailbox Unsupported Claim

Goal: promote the unsupported self-mailbox command boundary into the named
transition-claim and proof-certificate surface.

Deliverables:

- `self_mailbox_preserves_unsupported_command` predicate;
- `UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED` manifest claim with positive
  and negative executable examples;
- proof-certificate coverage for the new claim;
- transition-language predicate vocabulary update;
- tests proving predicate behavior, manifest evaluation, certificate coverage,
  and object-language validation.

Status: accepted in `docs/adr/0034-self-mailbox-unsupported-claim.md`.
Implemented in `autarkic_systems/transition_predicates.py`,
`claims/transition_claims.json`, `claims/proof_certificates.json`, and
`language/transition_claim_language.json`, with tests in
`tests/test_self_mailbox_unsupported_claim.py`.

## ADR-0035: Self Mailbox Unsupported Trace

Goal: add a schematic-linked trace for one unsupported self-mailbox command.

Deliverables:

- `schematics/self_mailbox_unsupported_trace.json`;
- unsupported self-mailbox artifact identity in the schematic-trace validator;
- validation that separates unsupported mailbox preservation from init
  mailbox execution;
- tests for artifact identity, schema vocabulary, preservation flow,
  execution replay, witness-map validation, and drift rejection.

Status: accepted in `docs/adr/0035-self-mailbox-unsupported-trace.md`.
Implemented in `autarkic_systems/schematic_trace.py` and
`schematics/self_mailbox_unsupported_trace.json`, with tests in
`tests/test_self_mailbox_unsupported_trace.py`.

## ADR-0036: Self Mailbox Unsupported SVG

Goal: add a rendered SVG view of the ADR-0035 unsupported self-mailbox trace.

Deliverables:

- `schematics/self_mailbox_unsupported_trace.svg`;
- exported unsupported self-mailbox SVG artifact path;
- renderer summary fields for unsupported mailbox and control/buffer
  preservation;
- tests proving parseability, trace metadata, port/layer annotations, visible
  preservation details, exact renderer-output matching, and drift rejection.

Status: accepted in `docs/adr/0036-self-mailbox-unsupported-svg.md`.
Implemented in `autarkic_systems/schematic_svg.py` and
`schematics/self_mailbox_unsupported_trace.svg`, with tests in
`tests/test_self_mailbox_unsupported_svg.py`.

## ADR-0037: Self Command Buffer Init Dispatch

Goal: dispatch just-completed self-target init-family command buffers without
implementing full command-buffer execution.

Deliverables:

- narrow `step_stem_cell` dispatch for completed self-target init-family
  command buffers;
- `stem-command-buffer-self-processed` transition status;
- transition-language status vocabulary update;
- source-status update showing the remaining full-execution blockers;
- tests proving self `proc-l-init`, self `stem-init`, then-current neighbor
  no-delivery behavior, self non-init non-execution, and status vocabulary
  coverage.

Status: accepted in `docs/adr/0037-self-command-buffer-init-dispatch.md`.
Implemented in `autarkic_systems/universal_cell.py`,
`language/transition_claim_language.json`, and
`sources/stem_command_execution_source_status.json`, with tests in
`tests/test_self_command_buffer_init_dispatch.py` and the updated source-status
tests. ADR-0044 later replaces that neighbor no-delivery expectation with
neighbor-target output-channel delivery.

## ADR-0038: Self Command Buffer Init Claim

Goal: promote the ADR-0037 self-target init command-buffer dispatch into the
named transition-claim and proof-certificate surface.

Deliverables:

- `stem_command_buffer_executes_self_init` predicate;
- `UC-STEM-COMMAND-BUFFER-SELF-INIT` manifest claim with positive and negative
  executable examples;
- proof-certificate coverage for the new claim;
- transition-language predicate vocabulary update;
- tests proving predicate behavior, manifest evaluation, certificate coverage,
  and object-language validation.

Status: accepted in `docs/adr/0038-self-command-buffer-init-claim.md`.
Implemented in `autarkic_systems/transition_predicates.py`,
`claims/transition_claims.json`, `claims/proof_certificates.json`, and
`language/transition_claim_language.json`, with tests in
`tests/test_self_command_buffer_init_claim.py`.

## ADR-0039: Self Command Buffer Init Trace

Goal: add a schematic-linked trace for one completed self-target init command
buffer.

Deliverables:

- `schematics/self_command_buffer_init_trace.json`;
- command-buffer self-init artifact identity in the schematic-trace validator;
- validation that separates completed self-init buffer dispatch from ordinary
  buffer accumulation and direct self-mailbox execution;
- tests for artifact identity, schema vocabulary, decode flow, execution
  replay, witness-map validation, and drift rejection.

Status: accepted in `docs/adr/0039-self-command-buffer-init-trace.md`.
Implemented in `autarkic_systems/schematic_trace.py` and
`schematics/self_command_buffer_init_trace.json`, with tests in
`tests/test_self_command_buffer_init_trace.py`.

## ADR-0040: Self Command Buffer Init SVG

Goal: add a rendered SVG view of the ADR-0039 self command-buffer init trace.

Deliverables:

- `schematics/self_command_buffer_init_trace.svg`;
- exported command-buffer SVG artifact path;
- renderer summary fields for command-buffer before/after and cleared command
  state;
- tests proving parseability, trace metadata, port/layer annotations, visible
  command-buffer details, exact renderer-output matching, and drift rejection.

Status: accepted in `docs/adr/0040-self-command-buffer-init-svg.md`.
Implemented in `autarkic_systems/schematic_svg.py` and
`schematics/self_command_buffer_init_trace.svg`, with tests in
`tests/test_self_command_buffer_init_svg.py`.

## ADR-0041: Command Buffer Unsupported Claim

Goal: promote completed command buffers outside the self-target init slice into
the named append-boundary claim surface. ADR-0044 later narrows the live
boundary to self-target non-init command buffers.

Deliverables:

- `stem_command_buffer_preserves_unsupported_completion` predicate;
- `UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED` manifest claim with positive
  self non-init examples plus a negative processed example;
- proof-certificate coverage for the new claim;
- transition-language predicate vocabulary update;
- tests proving predicate behavior, manifest evaluation, certificate coverage,
  and object-language validation.

Status: accepted in `docs/adr/0041-command-buffer-unsupported-claim.md`.
Implemented in `autarkic_systems/transition_predicates.py`,
`claims/transition_claims.json`, `claims/proof_certificates.json`, and
`language/transition_claim_language.json`, with tests in
`tests/test_command_buffer_unsupported_claim.py`. Revised by ADR-0044 after
neighbor-target command-buffer delivery became implemented behavior.

## ADR-0042: Command Buffer Unsupported Trace

Goal: add a schematic-linked trace for one unsupported completed command
buffer. ADR-0044 revises the live trace to a self-target non-init example.

Deliverables:

- `schematics/command_buffer_unsupported_trace.json`;
- command-buffer unsupported artifact identity in the schematic-trace
  validator;
- validation that separates completed unsupported command-buffer flow from
  ordinary buffer accumulation and supported self-init dispatch;
- tests for artifact identity, schema vocabulary, decode flow, execution
  replay, witness-map validation, and drift rejection.

Status: accepted in `docs/adr/0042-command-buffer-unsupported-trace.md`.
Implemented in `autarkic_systems/schematic_trace.py` and
`schematics/command_buffer_unsupported_trace.json`, with tests in
`tests/test_command_buffer_unsupported_trace.py`. Revised by ADR-0044 from the
original neighbor-target example to a self-target `write-buf-one` append
boundary.

## ADR-0043: Command Buffer Unsupported SVG

Goal: add a rendered SVG view of the ADR-0042 unsupported command-buffer trace.

Deliverables:

- `schematics/command_buffer_unsupported_trace.svg`;
- exported unsupported command-buffer SVG artifact path;
- renderer summary fields for command-buffer before/after and preserved
  append-boundary state;
- tests proving parseability, trace metadata, port/layer annotations, visible
  command-buffer details, exact renderer-output matching, and drift rejection.

Status: accepted in `docs/adr/0043-command-buffer-unsupported-svg.md`.
Implemented in `autarkic_systems/schematic_svg.py` and
`schematics/command_buffer_unsupported_trace.svg`, with tests in
`tests/test_command_buffer_unsupported_svg.py`. Revised by ADR-0044 alongside
the updated unsupported command-buffer trace.

## ADR-0044: Neighbor Command Buffer Delivery

Goal: deliver completed neighbor-target command buffers onto output channels
without executing recipient-side command-message inputs.

Deliverables:

- `stem-command-buffer-neighbor-delivered` status vocabulary;
- neighbor A/B/C output-channel delivery for decoded command buffers;
- transient command-state clearing after delivery;
- tests proving neighbor delivery, blocked-output behavior, self non-init
  preservation, and command-message input rejection;
- source-status and documentation updates that move the blocker from delivery
  to recipient-side consumption.

Status: accepted in `docs/adr/0044-neighbor-command-buffer-delivery.md`.
Implemented in `autarkic_systems/universal_cell.py`,
`language/transition_claim_language.json`,
`sources/stem_command_execution_source_status.json`, and the adjacent
command-buffer tests.

## ADR-0045: Neighbor Command Buffer Delivery Claim

Goal: promote ADR-0044 neighbor-target command-buffer delivery into the named
transition-claim and proof-certificate surface.

Deliverables:

- `stem_command_buffer_delivers_neighbor_command` predicate;
- `UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED` manifest claim with positive
  delivery and negative wrong-channel examples;
- proof-certificate coverage for the new claim;
- transition-language predicate vocabulary update;
- tests proving predicate behavior for all three neighbor targets, manifest
  evaluation, certificate coverage, and object-language validation.

Status: accepted in
`docs/adr/0045-neighbor-command-buffer-delivery-claim.md`. Implemented in
`autarkic_systems/transition_predicates.py`, `claims/transition_claims.json`,
`claims/proof_certificates.json`, and
`language/transition_claim_language.json`, with tests in
`tests/test_neighbor_command_buffer_delivery_claim.py`.

## ADR-0046: Neighbor Command Buffer Delivery Trace

Goal: add a schematic-linked trace for one completed neighbor-target command
buffer delivered onto an output channel.

Deliverables:

- `schematics/neighbor_command_buffer_delivery_trace.json`;
- neighbor command-buffer delivery artifact identity in the schematic-trace
  validator;
- validation that separates neighbor delivery from self init dispatch,
  unsupported append-boundary traces, and ordinary stem buffer accumulation;
- tests for artifact identity, schema vocabulary, decode flow, execution
  replay, witness-map validation, and drift rejection.

Status: accepted in
`docs/adr/0046-neighbor-command-buffer-delivery-trace.md`. Implemented in
`autarkic_systems/schematic_trace.py` and
`schematics/neighbor_command_buffer_delivery_trace.json`, with tests in
`tests/test_neighbor_command_buffer_delivery_trace.py`.

## ADR-0047: Neighbor Command Buffer Delivery SVG

Goal: add a rendered SVG view of the ADR-0046 neighbor command-buffer delivery
trace.

Deliverables:

- `schematics/neighbor_command_buffer_delivery_trace.svg`;
- exported neighbor command-buffer delivery SVG artifact path;
- renderer summary fields for command-buffer before state, output-channel
  delivery, and cleared command state;
- tests proving parseability, trace metadata, port/layer annotations, visible
  delivery details, exact renderer-output matching, and drift rejection.

Status: accepted in
`docs/adr/0047-neighbor-command-buffer-delivery-svg.md`. Implemented in
`autarkic_systems/schematic_svg.py` and
`schematics/neighbor_command_buffer_delivery_trace.svg`, with tests in
`tests/test_neighbor_command_buffer_delivery_svg.py`.

## ADR-0048: Recipient Command Consumption Source Status

Goal: decide the next recipient-side command-message consumption slice from
PRC sources before executing delivered neighbor command tokens.

Deliverables:

- `sources/recipient_command_consumption_source_status.json`;
- human-facing source-status note;
- tests covering the formal input special-message anchor, legacy
  special-message sets, unresolved blockers, and the updated stem command
  execution next-slice list;
- documentation updates that move the next executable slice to recipient-side
  init-family command-message consumption.

Status: accepted in
`docs/adr/0048-recipient-command-consumption-source-status.md`. Implemented in
`sources/recipient_command_consumption_source_status.json` and
`docs/recipient-command-consumption-source-status.md`, with tests in
`tests/test_recipient_command_consumption_source_status.py`.

## ADR-0049: Recipient Init Command-Message Consumption

Goal: consume delivered init-family command-message tokens on recipient cells
without executing unresolved non-init command messages.

Deliverables:

- recipient input-channel handling for `stem-init`, `wire-r-init`,
  `wire-l-init`, `proc-r-init`, and `proc-l-init`;
- `recipient-init-command-message-processed` transition status;
- fixed-cell direct input and pulled-upstream command-message coverage;
- stem-cell command-state clearing coverage;
- preserved rejection for `standard-signal`, write-buffer, and multi-command
  inputs;
- transition-language status update and source-status next-slice update.

Status: accepted in
`docs/adr/0049-recipient-init-command-message-consumption.md`. Implemented in
`autarkic_systems/universal_cell.py`,
`language/transition_claim_language.json`, and
`docs/recipient-init-command-message-consumption.md`, with tests in
`tests/test_recipient_init_command_messages.py`.

## ADR-0050: Recipient Init Command-Message Claim

Goal: promote the ADR-0049 recipient init command-message consumption subset
into the named transition-claim and proof-certificate surface.

Deliverables:

- `recipient_init_command_message_processed` predicate;
- `UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED` claim manifest entry;
- proof-certificate manifest entry using `manifest-example`;
- transition-language predicate vocabulary update;
- human-facing claim note;
- tests covering predicate behavior, inactive preconditions, manifest
  examples, proof certificates, and object-language coverage.

Status: accepted in
`docs/adr/0050-recipient-init-command-message-claim.md`. Implemented in
`autarkic_systems/transition_predicates.py`,
`claims/transition_claims.json`, `claims/proof_certificates.json`,
`language/transition_claim_language.json`, and
`docs/recipient-init-command-message-claim.md`, with tests in
`tests/test_recipient_init_command_message_claim.py`.

## ADR-0051: Recipient Init Command-Message Trace

Goal: add a schematic-linked trace for one recipient init command-message
transition over the ADR-0050 named claim.

Deliverables:

- `schematics/recipient_init_command_message_trace.json`;
- `recipient-init-command-message-schematic-and-uc-transition-trace` artifact
  identity;
- schematic-trace validator support for recipient init command-message
  alignment;
- tests proving artifact identity, schema vocabulary, upstream command flow,
  execution replay, PRC witness validation, and drift rejection;
- human-facing trace note and source-status next-slice update.

Status: accepted in
`docs/adr/0051-recipient-init-command-message-trace.md`. Implemented in
`autarkic_systems/schematic_trace.py`,
`schematics/recipient_init_command_message_trace.json`, and
`docs/recipient-init-command-message-trace.md`, with tests in
`tests/test_recipient_init_command_message_trace.py`.

## ADR-0052: Recipient Init Command-Message SVG

Goal: add a rendered SVG view of the ADR-0051 recipient init command-message
trace.

Deliverables:

- `schematics/recipient_init_command_message_trace.svg`;
- exported recipient init command-message SVG artifact path;
- renderer summary fields for upstream command-message before/after state,
  role/memory reconfiguration, and cleared command state;
- tests proving parseability, trace metadata, port/layer annotations, visible
  recipient command details, exact renderer-output matching, and drift
  rejection.

Status: accepted in
`docs/adr/0052-recipient-init-command-message-svg.md`. Implemented in
`autarkic_systems/schematic_svg.py`,
`schematics/recipient_init_command_message_trace.svg`, and
`docs/recipient-init-command-message-svg.md`, with tests in
`tests/test_recipient_init_command_message_svg.py`.

## ADR-0053: Recipient Non-Init Command Source Status

Goal: decide the recipient-side non-init command-message frontier before
runtime execution.

Deliverables:

- `sources/recipient_non_init_command_source_status.json`;
- human-facing source-status note;
- tests covering standard-signal divergence, write-buffer source divergences,
  multi-command policy, and updated source-status frontier;
- documentation updates that move the next safe slice to a named
  non-init command-message rejection-boundary claim.

Status: accepted in
`docs/adr/0053-recipient-non-init-command-source-status.md`. Implemented in
`sources/recipient_non_init_command_source_status.json` and
`docs/recipient-non-init-command-source-status.md`, with tests in
`tests/test_recipient_non_init_command_source_status.py`.

## ADR-0054: Recipient Non-Init Command Rejection Claim

Goal: promote the ADR-0053 recipient non-init command-message rejection
boundary into the named transition-claim and proof-certificate surface.

Deliverables:

- `recipient_non_init_command_message_rejected` predicate;
- `UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED` claim manifest entry;
- proof-certificate manifest entry using `manifest-example`;
- transition-language predicate vocabulary update;
- human-facing claim note;
- tests covering fixed direct rejection, fixed upstream rejection, stem
  multi-command conflict rejection, inactive preconditions, manifest examples,
  proof certificates, and object-language coverage.

Status: accepted in
`docs/adr/0054-recipient-non-init-command-rejection-claim.md`. Implemented in
`autarkic_systems/transition_predicates.py`,
`claims/transition_claims.json`, `claims/proof_certificates.json`,
`language/transition_claim_language.json`, and
`docs/recipient-non-init-command-rejection-claim.md`, with tests in
`tests/test_recipient_non_init_command_rejection_claim.py`.

## ADR-0055: Recipient Non-Init Command Rejection Trace

Goal: add a schematic-linked trace for one recipient non-init command-message
rejection over the ADR-0054 named claim.

Deliverables:

- `schematics/recipient_non_init_command_rejection_trace.json`;
- `recipient-non-init-command-rejection-schematic-and-uc-transition-trace`
  artifact identity;
- schematic-trace validator support for recipient non-init command-message
  rejection alignment;
- tests proving artifact identity, schema vocabulary, upstream rejection flow,
  execution replay, ADR-0054 predicate coverage, PRC witness validation, and
  drift rejection;
- human-facing trace note and source-status next-slice update.

Status: accepted in
`docs/adr/0055-recipient-non-init-command-rejection-trace.md`. Implemented in
`autarkic_systems/schematic_trace.py`,
`schematics/recipient_non_init_command_rejection_trace.json`, and
`docs/recipient-non-init-command-rejection-trace.md`, with tests in
`tests/test_recipient_non_init_command_rejection_trace.py`.

## ADR-0056: Recipient Non-Init Command Rejection SVG

Goal: add a rendered SVG view of the ADR-0055 recipient non-init
command-message rejection trace.

Deliverables:

- `schematics/recipient_non_init_command_rejection_trace.svg`;
- exported recipient non-init command-message rejection SVG artifact path;
- renderer summary fields for rejected upstream command-message before/after
  state, preserved role/memory, cleared input/output, and preserved command
  side state;
- tests proving parseability, trace metadata, port/layer annotations, visible
  rejection details, exact renderer-output matching, and drift rejection.

Status: accepted in
`docs/adr/0056-recipient-non-init-command-rejection-svg.md`. Implemented in
`autarkic_systems/schematic_svg.py`,
`schematics/recipient_non_init_command_rejection_trace.svg`, and
`docs/recipient-non-init-command-rejection-svg.md`, with tests in
`tests/test_recipient_non_init_command_rejection_svg.py`.

## ADR-0057: Write-Buffer Command Semantics Status

Goal: decide whether write-buffer command execution is source-backed enough to
implement after the recipient non-init rejection evidence ladder.

Deliverables:

- `sources/write_buffer_command_semantics_status.json`;
- formal-model anchors for the named write-buffer commands and special-message
  paths;
- RAA, SEMSIM, and FSMSIM write-buffer witness records;
- explicit blocked runtime surfaces for recipient command-message,
  self-mailbox, and self-target command-buffer commands;
- tests proving the source-status decision, witness divergence, required
  resolution questions, and updated source-status frontiers;
- human-facing source-status note.

Status: accepted in
`docs/adr/0057-write-buffer-command-semantics-status.md`. Implemented in
`sources/write_buffer_command_semantics_status.json` and
`docs/write-buffer-command-semantics-status.md`, with tests in
`tests/test_write_buffer_command_semantics_status.py`.

## ADR-0058: Standard-Signal Command Semantics Status

Goal: decide whether `standard-signal` command-token execution is source-backed
enough to implement after the write-buffer source-status decision.

Deliverables:

- `sources/standard_signal_command_semantics_status.json`;
- formal-model anchors separating ordinary binary-input standard-signal
  behavior from command-table placement;
- RAA, SEMSIM, and FSMSIM standard-signal witness records;
- explicit blocked runtime surfaces for recipient command-message,
  self-mailbox, and self-target command-buffer commands;
- tests proving the source-status decision, witness divergence, required
  resolution questions, and updated source-status frontiers;
- human-facing source-status note.

Status: accepted in
`docs/adr/0058-standard-signal-command-semantics-status.md`. Implemented in
`sources/standard_signal_command_semantics_status.json` and
`docs/standard-signal-command-semantics-status.md`, with tests in
`tests/test_standard_signal_command_semantics_status.py`.

## ADR-0059: Multi-Command Recipient Input Policy

Goal: select the policy for multiple simultaneous recipient command-message
inputs before adding more rejection traces or widening command consumption.

Deliverables:

- `sources/multi_command_recipient_input_policy_status.json`;
- explicit reject-and-clear policy for two or more command-message tokens;
- tests proving fixed direct, fixed upstream, and stem direct runtime behavior
  already matches the policy;
- an all-init command conflict example in the recipient non-init rejection
  claim manifest, with proof-certificate coverage;
- human-facing policy note and source-status frontier updates.

Status: accepted in
`docs/adr/0059-multi-command-recipient-input-policy.md`. Implemented in
`sources/multi_command_recipient_input_policy_status.json` and
`docs/multi-command-recipient-input-policy-status.md`, with tests in
`tests/test_multi_command_recipient_input_policy_status.py`.

## ADR-0060: Multi-Command Recipient Rejection Trace

Goal: make the ADR-0059 reject-and-clear policy visible as a schematic-linked
trace.

Deliverables:

- `schematics/multi_command_recipient_rejection_trace.json`;
- exported `MULTI_COMMAND_RECIPIENT_REJECTION_TRACE_ARTIFACT_ID`;
- validator routing for the new artifact through the recipient non-init
  rejection alignment check;
- tests proving replay, claim satisfaction, flow wording, witness-map
  validation, and drift rejection;
- human-facing trace note and source-status frontier updates.

Status: accepted in
`docs/adr/0060-multi-command-recipient-rejection-trace.md`. Implemented in
`schematics/multi_command_recipient_rejection_trace.json`,
`autarkic_systems/schematic_trace.py`, and
`docs/multi-command-recipient-rejection-trace.md`, with tests in
`tests/test_multi_command_recipient_rejection_trace.py`.

## ADR-0061: Multi-Command Recipient Rejection SVG

Goal: add a rendered SVG view of the ADR-0060 multi-command recipient
rejection trace.

Deliverables:

- `schematics/multi_command_recipient_rejection_trace.svg`;
- exported `MULTI_COMMAND_RECIPIENT_REJECTION_SVG_ARTIFACT`;
- renderer routing through the recipient non-init rejection summary branch;
- tests proving parseability, trace metadata, port/layer annotations, visible
  multi-command rejection details, exact renderer-output matching, and drift
  rejection;
- human-facing SVG note and source-status frontier updates.

Status: accepted in
`docs/adr/0061-multi-command-recipient-rejection-svg.md`. Implemented in
`autarkic_systems/schematic_svg.py`,
`schematics/multi_command_recipient_rejection_trace.svg`, and
`docs/multi-command-recipient-rejection-svg.md`, with tests in
`tests/test_multi_command_recipient_rejection_svg.py`.

## ADR-0062: Guile ASMSIM Command Semantics Status

Goal: decide whether `practice/legacy/guile-asmsim.scm` resolves the blocked
`standard-signal` or write-buffer command-token semantics.

Deliverables:

- `sources/guile_asmsim_command_semantics_status.json`;
- source-status record for the init-family-only `special-messages` list;
- source-status record for binary `write-buf`, self-mailbox numeric append,
  and the command-buffer list expression;
- cross-links from standard-signal, write-buffer, and stem command
  source-status artifacts;
- tests proving the source-only blocking decision and local witness facts;
- human-facing source-status note.

Status: accepted in
`docs/adr/0062-guile-asmsim-command-semantics-status.md`. Implemented in
`sources/guile_asmsim_command_semantics_status.json` and
`docs/guile-asmsim-command-semantics-status.md`, with tests in
`tests/test_guile_asmsim_command_semantics_status.py`.

## ADR-0063: ASMSIM Process-Buffer Status

Goal: decide whether `practice/asmsim.scm` resolves the blocked
`standard-signal` or write-buffer command-token semantics.

Deliverables:

- `sources/asmsim_process_buffer_status.json`;
- source-status record for the `qs18` process-buffer branch set;
- source-status record for the "need documentation here" and
  "XXX CONFIRM MSGLIST CODES" source warnings;
- source-status record for process-buffer code-shape predicates and the
  `msg-list` placeholder;
- cross-links from standard-signal, write-buffer, and stem command
  source-status artifacts;
- tests proving the source-only blocking decision and local witness facts;
- human-facing source-status note.

Status: accepted in `docs/adr/0063-asmsim-process-buffer-status.md`.
Implemented in `sources/asmsim_process_buffer_status.json` and
`docs/asmsim-process-buffer-status.md`, with tests in
`tests/test_asmsim_process_buffer_status.py`.

## ADR-0064: Official TLA Universal Cell Status

Goal: decide whether PRC's official TLA files can serve as executable
Universal Cell or command-semantics authority.

Deliverables:

- `sources/official_tla_universal_cell_status.json`;
- source-status record for `universal-cell.tla`, `universalcell.tla`, and
  `uc.tla`;
- tests proving line counts, partial/stub/empty status, and absent command
  semantics;
- cross-links from standard-signal, write-buffer, and stem command
  source-status artifacts;
- human-facing source-status note.

Status: accepted in
`docs/adr/0064-official-tla-universal-cell-status.md`. Implemented in
`sources/official_tla_universal_cell_status.json` and
`docs/official-tla-universal-cell-status.md`, with tests in
`tests/test_official_tla_universal_cell_status.py`.

## ADR-0065: Recipient Init Transition Evidence Bundle

Goal: make one already implemented recipient init command-message transition
inspectable across runtime, claim, proof, schematic, render, and source-status
layers.

Deliverables:

- `evidence/recipient_init_command_message_bundle.json`;
- `autarkic_systems/evidence_bundle.py`;
- tests proving the bundle validates the claim example, proof certificate,
  schematic trace, SVG render, and source-status files together;
- drift tests for unknown claim IDs and missing SVG paths;
- human-facing evidence-bundle note.

Status: accepted in
`docs/adr/0065-recipient-init-transition-evidence-bundle.md`. Implemented in
`evidence/recipient_init_command_message_bundle.json` and
`autarkic_systems/evidence_bundle.py`, with tests in
`tests/test_recipient_init_transition_evidence_bundle.py`.

## ADR-0066: Evidence Bundle Registry

Goal: make transition evidence bundles discoverable and batch-verifiable.

Deliverables:

- `evidence/manifest.json`;
- registry dataclasses, loader, and validator in
  `autarkic_systems/evidence_bundle.py`;
- tests proving registry loading, bundle entry coverage, whole-registry
  validation, duplicate bundle-ID rejection, and missing path rejection;
- human-facing registry note.

Status: accepted in `docs/adr/0066-evidence-bundle-registry.md`. Implemented
in `evidence/manifest.json` and `autarkic_systems/evidence_bundle.py`, with
tests in `tests/test_evidence_bundle_registry.py`.

## ADR-0067: Evidence Registry CLI

Goal: expose evidence registry validation as a direct project command.

Deliverables:

- CLI entrypoint through `python -m autarkic_systems.evidence_bundle`;
- concise `OK`/`FAIL` report formatting for registry validation results;
- exit code `0` for accepted registries and non-zero for validation failures;
- tests covering report formatting, successful command execution, missing
  bundle failure, and module execution;
- human-facing command documentation.

Status: accepted in `docs/adr/0067-evidence-registry-cli.md`. Implemented in
`autarkic_systems/evidence_bundle.py`, with tests in
`tests/test_evidence_bundle_cli.py`.

## ADR-0068: Recipient Non-Init Rejection Evidence Bundle

Goal: add the recipient non-init command-message rejection boundary as the
second transition evidence bundle.

Deliverables:

- `evidence/recipient_non_init_command_rejection_bundle.json`;
- registry entry in `evidence/manifest.json`;
- tests proving bundle fields, artifact paths, cross-layer validation,
  registry coverage, and drifted status rejection;
- human-facing evidence-bundle note and source-status cross-link.

Status: accepted in `docs/adr/0068-recipient-non-init-evidence-bundle.md`.
Implemented in `evidence/recipient_non_init_command_rejection_bundle.json`,
with tests in `tests/test_recipient_non_init_evidence_bundle.py`.

## ADR-0069: Multi-Command Rejection Evidence Bundle

Goal: add the simultaneous command-message rejection boundary as the third
transition evidence bundle.

Deliverables:

- `evidence/multi_command_recipient_rejection_bundle.json`;
- registry entry in `evidence/manifest.json`;
- tests proving bundle fields, artifact paths, cross-layer validation,
  registry coverage, and drifted claim-ID rejection;
- human-facing evidence-bundle note and multi-command source-status cross-link.

Status: accepted in `docs/adr/0069-multi-command-rejection-evidence-bundle.md`.
Implemented in `evidence/multi_command_recipient_rejection_bundle.json`, with
tests in `tests/test_multi_command_evidence_bundle.py`.

## ADR-0070: Evidence Registry Completeness

Goal: make the evidence registry a closed index over sibling bundle files.

Deliverables:

- registry completeness validation for sibling `*_bundle.json` files;
- CLI/report coverage for the new `registry-completeness` result;
- tests proving the checked-in registry is complete and that unregistered
  sibling bundle files are rejected;
- human-facing registry documentation update.

Status: accepted in `docs/adr/0070-evidence-registry-completeness.md`.
Implemented in `autarkic_systems/evidence_bundle.py`, with tests in
`tests/test_evidence_bundle_registry.py` and
`tests/test_evidence_bundle_cli.py`.

## ADR-0071: Evidence CLI JSON Output

Goal: make evidence registry validation consumable by automation without text
scraping.

Deliverables:

- `--format text|json` option for
  `python -m autarkic_systems.evidence_bundle`;
- structured JSON report payload with registry ID, accepted status, bundle
  count, result count, and validation result records;
- tests covering successful JSON output, failing JSON output, and module
  execution in JSON mode;
- human-facing registry command documentation update.

Status: accepted in `docs/adr/0071-evidence-cli-json-output.md`. Implemented
in `autarkic_systems/evidence_bundle.py`, with tests in
`tests/test_evidence_bundle_cli.py`.

## ADR-0072: Self-Mailbox Init Evidence Bundle

Goal: add the direct self-mailbox init-family transition as the fourth
transition evidence bundle.

Deliverables:

- `evidence/self_mailbox_init_bundle.json`;
- registry entry in `evidence/manifest.json`;
- trace/SVG alignment with the existing positive claim example;
- tests proving bundle fields, artifact paths, cross-layer validation,
  registry coverage, and drifted trace-path rejection;
- human-facing evidence-bundle note and stem command source-status cross-link.

Status: accepted in `docs/adr/0072-self-mailbox-init-evidence-bundle.md`.
Implemented in `evidence/self_mailbox_init_bundle.json`, with tests in
`tests/test_self_mailbox_init_evidence_bundle.py`.

## ADR-0073: Self-Mailbox Unsupported Evidence Bundle

Goal: add the direct unsupported self-mailbox preservation boundary as the
fifth transition evidence bundle.

Deliverables:

- `evidence/self_mailbox_unsupported_bundle.json`;
- registry entry in `evidence/manifest.json`;
- trace/SVG alignment with the existing positive preservation claim example;
- tests proving bundle fields, artifact paths, cross-layer validation,
  registry coverage, and drifted status rejection;
- human-facing evidence-bundle note and stem command source-status cross-link.

Status: accepted in
`docs/adr/0073-self-mailbox-unsupported-evidence-bundle.md`. Implemented in
`evidence/self_mailbox_unsupported_bundle.json`, with tests in
`tests/test_self_mailbox_unsupported_evidence_bundle.py`.

## ADR-0074: Self Command-Buffer Init Evidence Bundle

Goal: add the completed self-target command-buffer init dispatch as the sixth
transition evidence bundle.

Deliverables:

- `evidence/self_command_buffer_init_bundle.json`;
- registry entry in `evidence/manifest.json`;
- tests proving bundle fields, artifact paths, cross-layer validation,
  registry coverage, and drifted claim-ID rejection;
- human-facing evidence-bundle note and stem command source-status cross-link.

Status: accepted in
`docs/adr/0074-self-command-buffer-init-evidence-bundle.md`. Implemented in
`evidence/self_command_buffer_init_bundle.json`, with tests in
`tests/test_self_command_buffer_init_evidence_bundle.py`.

## ADR-0075: Command-Buffer Unsupported Evidence Bundle

Goal: add the completed self-target non-init command-buffer append boundary as
the seventh transition evidence bundle.

Deliverables:

- `evidence/command_buffer_unsupported_bundle.json`;
- registry entry in `evidence/manifest.json`;
- tests proving bundle fields, artifact paths, cross-layer validation,
  registry coverage, and drifted status rejection;
- human-facing evidence-bundle note and stem command source-status cross-link.

Status: accepted in
`docs/adr/0075-command-buffer-unsupported-evidence-bundle.md`. Implemented in
`evidence/command_buffer_unsupported_bundle.json`, with tests in
`tests/test_command_buffer_unsupported_evidence_bundle.py`.

## ADR-0076: Neighbor Command-Buffer Delivery Evidence Bundle

Goal: add the completed neighbor-target command-buffer delivery path as the
eighth transition evidence bundle.

Deliverables:

- `evidence/neighbor_command_buffer_delivery_bundle.json`;
- registry entry in `evidence/manifest.json`;
- tests proving bundle fields, artifact paths, cross-layer validation,
  registry coverage, and drifted status rejection;
- human-facing evidence-bundle note and stem command source-status cross-link.

Status: accepted in
`docs/adr/0076-neighbor-command-buffer-delivery-evidence-bundle.md`.
Implemented in `evidence/neighbor_command_buffer_delivery_bundle.json`, with
tests in `tests/test_neighbor_command_buffer_delivery_evidence_bundle.py`.

## ADR-0077: Neighbor Delivery Recipient Chain

Goal: add the first executable two-step handoff from neighbor command-buffer
delivery into recipient init-family command consumption.

Deliverables:

- `autarkic_systems/transition_chains.py`;
- `tests/test_neighbor_delivery_recipient_chain.py`;
- tests proving accepted init delivery consumption, sender precondition
  failure, recipient readiness failure, and delivered non-init rejection;
- human-facing chain note and project navigation updates.

Status: accepted in `docs/adr/0077-neighbor-delivery-recipient-chain.md`.
Implemented in `autarkic_systems/transition_chains.py`, with tests in
`tests/test_neighbor_delivery_recipient_chain.py`.

## ADR-0078: Neighbor Delivery Chain Claim

Goal: promote the ADR-0077 two-step handoff into a named chain claim and proof
surface without forcing it into the single-transition claim language.

Deliverables:

- `claims/transition_chain_claims.json`;
- `claims/transition_chain_proof_certificates.json`;
- `autarkic_systems/transition_chain_predicates.py`;
- `autarkic_systems/chain_claims.py`;
- tests proving manifest loading, example evaluation, proof-certificate
  coverage, positive predicate acceptance, and non-init delivered-token
  rejection;
- human-facing claim note and project navigation updates.

Status: accepted in `docs/adr/0078-neighbor-delivery-chain-claim.md`.
Implemented in `claims/transition_chain_claims.json` and
`autarkic_systems/chain_claims.py`, with tests in
`tests/test_neighbor_delivery_chain_claim.py`.

## ADR-0079: Transition Chain Claim Language

Goal: make the transition-chain claim language explicit instead of relying on
implicit Python and JSON shape.

Deliverables:

- `language/transition_chain_claim_language.json`;
- `autarkic_systems/chain_object_language.py`;
- `tests/test_chain_object_language.py`;
- tests proving required syntax classes, current chain claim surface
  validation, unknown chain-predicate rejection, unknown proof-rule rejection,
  and incomplete chain-status vocabulary rejection;
- human-facing language note and project navigation updates.

Status: accepted in `docs/adr/0079-transition-chain-claim-language.md`.
Implemented in `language/transition_chain_claim_language.json` and
`autarkic_systems/chain_object_language.py`, with tests in
`tests/test_chain_object_language.py`.

## ADR-0080: Transition Chain Claim CLI

Goal: expose transition-chain claim validation as an operator-facing command.

Deliverables:

- text and JSON validation output in `autarkic_systems/chain_claims.py`;
- `python -m autarkic_systems.chain_claims` module execution;
- tests proving successful text/JSON output, incomplete-certificate failure,
  and subprocess module execution;
- human-facing command documentation update.

Status: accepted in `docs/adr/0080-transition-chain-claim-cli.md`.
Implemented in `autarkic_systems/chain_claims.py`, with tests in
`tests/test_transition_chain_claim_cli.py`.

## ADR-0081: Neighbor Delivery Chain Evidence Bundle

Goal: make the ADR-0077 through ADR-0080 neighbor delivery recipient chain
inspectable as one composed-chain evidence artifact.

Deliverables:

- `evidence/chains/neighbor_delivery_chain_bundle.json`;
- `autarkic_systems/chain_evidence_bundle.py`;
- `tests/test_neighbor_delivery_chain_evidence_bundle.py`;
- text and JSON validation through
  `python -m autarkic_systems.chain_evidence_bundle`;
- human-facing chain evidence-bundle note and project navigation updates.

Status: accepted in
`docs/adr/0081-neighbor-delivery-chain-evidence-bundle.md`. Implemented in
`evidence/chains/neighbor_delivery_chain_bundle.json`, with tests in
`tests/test_neighbor_delivery_chain_evidence_bundle.py`.

## ADR-0082: Neighbor Delivery Chain Trace

Goal: record the ADR-0077 neighbor delivery recipient chain as a dedicated
two-step trace artifact before rendering it.

Deliverables:

- `schematics/chains/neighbor_delivery_recipient_chain_trace.json`;
- `autarkic_systems/chain_trace.py`;
- `tests/test_neighbor_delivery_chain_trace.py`;
- ADR-0081 chain evidence bundle linkage to the trace;
- human-facing chain trace note and project navigation updates.

Status: accepted in `docs/adr/0082-neighbor-delivery-chain-trace.md`.
Implemented in `schematics/chains/neighbor_delivery_recipient_chain_trace.json`,
with tests in `tests/test_neighbor_delivery_chain_trace.py`.

## ADR-0083: Neighbor Delivery Chain SVG

Goal: render the ADR-0082 chain trace as a checked SVG artifact.

Deliverables:

- `schematics/chains/neighbor_delivery_recipient_chain_trace.svg`;
- `autarkic_systems/chain_svg.py`;
- `tests/test_neighbor_delivery_chain_svg.py`;
- ADR-0081 chain evidence bundle linkage to the SVG;
- human-facing chain SVG note and project navigation updates.

Status: accepted in `docs/adr/0083-neighbor-delivery-chain-svg.md`.
Implemented in `schematics/chains/neighbor_delivery_recipient_chain_trace.svg`,
with tests in `tests/test_neighbor_delivery_chain_svg.py`.

## ADR-0084: Chain Evidence Registry

Goal: make composed-chain evidence bundles discoverable and batch-validatable
without merging them into the single-transition evidence registry.

Deliverables:

- `evidence/chains/manifest.json`;
- registry loader, validator, text report, JSON payload, and `--registry` CLI
  support in `autarkic_systems/chain_evidence_bundle.py`;
- `tests/test_chain_evidence_bundle_registry.py`;
- human-facing chain registry note and project navigation updates.

Status: accepted in `docs/adr/0084-chain-evidence-registry.md`. Implemented in
`evidence/chains/manifest.json`, with tests in
`tests/test_chain_evidence_bundle_registry.py`.

## ADR-0085: Chain Evidence CLI Target Selection

Goal: make `--bundle` and `--registry` mutually exclusive for the chain
evidence CLI.

Deliverables:

- parser target exclusivity in `autarkic_systems/chain_evidence_bundle.py`;
- `tests/test_chain_evidence_cli_target_selection.py`;
- command documentation update.

Status: accepted in `docs/adr/0085-chain-evidence-cli-target-selection.md`.
Implemented in `autarkic_systems/chain_evidence_bundle.py`, with tests in
`tests/test_chain_evidence_cli_target_selection.py`.

## ADR-0086: Chain Registry JSON Entries

Goal: make chain evidence registry JSON output list the concrete bundle entries
validated in a run.

Deliverables:

- `bundles` array in `chain_registry_validation_report_payload`;
- focused tests in `tests/test_chain_evidence_bundle_registry.py`;
- documentation update for the chain evidence registry JSON contract.

Status: accepted in `docs/adr/0086-chain-registry-json-entries.md`.
Implemented in `autarkic_systems/chain_evidence_bundle.py`, with tests in
`tests/test_chain_evidence_bundle_registry.py`.

## ADR-0087: Chain Registry JSON Failure Summary

Goal: make failed chain evidence registry JSON output report the rejected
validation subjects directly.

Deliverables:

- `failed_subjects` array in `chain_registry_validation_report_payload`;
- focused success/failure payload tests in
  `tests/test_chain_evidence_bundle_registry.py`;
- documentation update for the chain registry JSON contract.

Status: accepted in `docs/adr/0087-chain-registry-json-failure-summary.md`.
Implemented in `autarkic_systems/chain_evidence_bundle.py`, with tests in
`tests/test_chain_evidence_bundle_registry.py`.

## ADR-0088: Chain Bundle JSON Failure Summary

Goal: make single-bundle chain evidence JSON output report rejected validation
subjects directly.

Deliverables:

- `failed_subjects` array in `chain_evidence_bundle_report_payload`;
- focused success/failure payload tests in
  `tests/test_neighbor_delivery_chain_evidence_bundle.py`;
- documentation update for the chain evidence bundle JSON contract.

Status: accepted in `docs/adr/0088-chain-bundle-json-failure-summary.md`.
Implemented in `autarkic_systems/chain_evidence_bundle.py`, with tests in
`tests/test_neighbor_delivery_chain_evidence_bundle.py`.

## ADR-0089: Vertical Chain Demo Report

Goal: expose the current transition-chain evidence path as one compact
operator-facing report.

Deliverables:

- `autarkic_systems/chain_demo.py`;
- `tests/test_chain_demo_report.py`;
- text and JSON CLI output through `python -m autarkic_systems.chain_demo`;
- human-facing demo report documentation and public navigation updates.

Status: accepted in `docs/adr/0089-vertical-chain-demo-report.md`.
Implemented in `autarkic_systems/chain_demo.py`, with tests in
`tests/test_chain_demo_report.py`.

## ADR-0090: Chain Demo Artifact Presence

Goal: make the vertical chain demo report explicit about whether listed
evidence artifacts exist.

Deliverables:

- per-layer `exists` flags in `autarkic_systems.chain_demo` JSON output;
- top-level `missing_evidence_paths` summary in text and JSON output;
- focused missing-path tests in `tests/test_chain_demo_report.py`;
- documentation update for the vertical chain demo contract.

Status: accepted in `docs/adr/0090-chain-demo-artifact-presence.md`.
Implemented in `autarkic_systems/chain_demo.py`, with tests in
`tests/test_chain_demo_report.py`.

## ADR-0091: Neighbor Delivery Rejection Chain Claim

Goal: name the delivered non-init recipient rejection boundary as its own
transition-chain claim.

Deliverables:

- `neighbor_delivery_rejected_by_recipient` in
  `autarkic_systems/transition_chain_predicates.py`;
- `UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-REJECTED` in
  `claims/transition_chain_claims.json`;
- matching manifest-example proof certificate coverage;
- transition-chain claim language update for the new predicate symbol;
- focused claim, CLI, and language test updates.

Status: accepted in
`docs/adr/0091-neighbor-delivery-rejection-chain-claim.md`. Implemented in
`autarkic_systems/transition_chain_predicates.py`, with tests in
`tests/test_neighbor_delivery_chain_claim.py`.

## ADR-0092: Neighbor Delivery Rejection Chain Trace

Goal: record the delivered non-init recipient rejection chain as a
machine-checked composed-chain trace.

Deliverables:

- `schematics/chains/neighbor_delivery_rejection_chain_trace.json`;
- trace validator support for expected rejected chain statuses;
- focused trace tests covering the rejection artifact, handoff, replay, and
  validation;
- chain trace documentation and project navigation updates.

Status: accepted in
`docs/adr/0092-neighbor-delivery-rejection-chain-trace.md`. Implemented in
`autarkic_systems/chain_trace.py`, with tests in
`tests/test_neighbor_delivery_chain_trace.py`.

## ADR-0093: Neighbor Delivery Rejection Chain SVG

Goal: render the delivered non-init recipient rejection chain trace as a
checked SVG artifact.

Deliverables:

- `schematics/chains/neighbor_delivery_rejection_chain_trace.svg`;
- renderer support for deriving the visible handoff channel from the delivered
  tuple;
- focused SVG tests covering the rejection render and committed artifact;
- chain SVG documentation and project navigation updates.

Status: accepted in
`docs/adr/0093-neighbor-delivery-rejection-chain-svg.md`. Implemented in
`autarkic_systems/chain_svg.py`, with tests in
`tests/test_neighbor_delivery_chain_svg.py`.

## ADR-0094: Neighbor Delivery Rejection Chain Evidence Bundle

Goal: give the delivered non-init recipient rejection chain integrated
evidence-bundle and registry coverage.

Deliverables:

- `evidence/chains/neighbor_delivery_rejection_chain_bundle.json`;
- registration in `evidence/chains/manifest.json`;
- focused rejection-bundle tests;
- registry tests updated for two chain bundles;
- chain evidence documentation and project navigation updates.

Status: accepted in
`docs/adr/0094-neighbor-delivery-rejection-chain-evidence-bundle.md`.
Implemented in `evidence/chains/neighbor_delivery_rejection_chain_bundle.json`,
with tests in
`tests/test_neighbor_delivery_rejection_chain_evidence_bundle.py`.

## ADR-0095: Chain Demo Registry Report

Goal: expose the whole transition-chain evidence registry through the vertical
chain demo report.

Deliverables:

- `--registry` mode in `autarkic_systems.chain_demo`;
- registry payloads summarizing bundle count, accepted count, failed count,
  missing paths, registry validation, and per-bundle demo reports;
- argparse rejection for ambiguous `--bundle` plus `--registry` target
  selection;
- missing registered bundle handling that returns structured failure output
  instead of crashing;
- documentation update for the registry demo command.

Status: accepted in `docs/adr/0095-chain-demo-registry-report.md`.
Implemented in `autarkic_systems/chain_demo.py`, with tests in
`tests/test_chain_demo_report.py`.

## ADR-0096: Project Status Report

Goal: provide one operator-facing status report over the current evidence
surface and blocked command-token frontier.

Deliverables:

- `autarkic_systems/project_status.py`;
- `tests/test_project_status_report.py`;
- text and JSON CLI output through
  `python -m autarkic_systems.project_status`;
- transition evidence registry summary with 8 bundles;
- transition-chain evidence registry summary with 2 bundles;
- blocked command-token summary for `standard-signal`, `write-buf-zero`, and
  `write-buf-one`;
- structured failure output for missing source-status files;
- human-facing status report documentation and public navigation updates.

Status: accepted in `docs/adr/0096-project-status-report.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0097: Project Status Registry Failures

Goal: make project status registry path failures structured report output
instead of tracebacks.

Deliverables:

- missing transition registry handling in `autarkic_systems.project_status`;
- missing chain registry handling in `autarkic_systems.project_status`;
- JSON and text output that names missing registry files;
- focused tests for both missing registry paths and CLI failure exit;
- documentation update for the status failure contract.

Status: accepted in `docs/adr/0097-project-status-registry-failures.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0098: Project Status Invalid Registries

Goal: distinguish malformed registry files from missing registry files in the
project status report.

Deliverables:

- invalid transition registry classification as `registry-json`;
- invalid chain registry classification as `registry-json`;
- text output that names invalid registry files separately from missing
  registry files;
- focused tests covering invalid transition and chain registries;
- documentation update for the refined status failure contract.

Status: accepted in `docs/adr/0098-project-status-invalid-registries.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0099: Project Status Frontier Failure Summary

Goal: give the project status frontier section a compact machine-readable
failure-subject summary.

Deliverables:

- `frontier.failed_subjects` in `autarkic_systems.project_status` JSON output;
- empty frontier failure subject list on the checked-in accepted path;
- `source-status-file` for missing source-status files;
- `source-status-json` for malformed source-status files;
- stable ordering when both source-status failure modes are present;
- focused tests and documentation for the frontier JSON contract.

Status: accepted in
`docs/adr/0099-project-status-frontier-failure-summary.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0100: Project Status Source Status Shape

Goal: reject source-status JSON that parses but lacks the minimal shape needed
by the project status frontier report.

Deliverables:

- source-status top-level object check in `autarkic_systems.project_status`;
- required non-empty text `decision` check;
- required non-empty text `safe_next_slice` check;
- `source-status-schema` frontier failure subject for shape-invalid
  source-status files;
- focused tests covering `{}` and non-object JSON source-status inputs;
- documentation update for the source-status shape contract.

Status: accepted in `docs/adr/0100-project-status-source-status-shape.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0101: Project Status Schema Version

Goal: make the project status JSON contract explicitly versioned.

Deliverables:

- top-level `schema_version` field in `autarkic_systems.project_status`;
- initial schema version `1`;
- in-process report and JSON CLI tests for the schema version;
- documentation update for the project status JSON contract.

Status: accepted in `docs/adr/0101-project-status-schema-version.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0102: Project Status Source Command Shape

Goal: require source-status records consumed by project status to name the
command tokens they contribute to the blocked frontier.

Deliverables:

- `source-status-schema` failure for source-status JSON that has process fields
  but no extractable command tokens;
- continued acceptance for the checked-in `command`, `commands`, and
  `blocked_runtime_commands` source-status forms;
- focused tests covering commandless source-status JSON; and
- documentation update for the source-status command-token shape.

Status: accepted in `docs/adr/0102-project-status-source-command-shape.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0103: Project Status Source Command Attribution

Goal: expose which blocked command tokens each accepted source-status artifact
contributes to the project status frontier.

Deliverables:

- `commands` list on each accepted `frontier.source_statuses` entry;
- schema bump from project status `schema_version: 1` to `schema_version: 2`;
- focused in-process and JSON CLI tests for source command attribution; and
- documentation update for the project status schema change.

Status: accepted in
`docs/adr/0103-project-status-source-command-attribution.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0104: Project Status Nonempty Source Commands

Goal: reject blank command-token strings in source-status records consumed by
project status.

Deliverables:

- `source-status-schema` failure for source-status command fields containing
  blank strings;
- unchanged `schema_version: 2` project status JSON shape;
- focused tests covering blank command-token rejection; and
- documentation update for the nonempty source command-token contract.

Status: accepted in
`docs/adr/0104-project-status-nonempty-source-commands.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0105: Project Status Nonempty Source Text

Goal: reject whitespace-only source-status `decision` and `safe_next_slice`
fields in project status.

Deliverables:

- `source-status-schema` failure for blank source-status decision text;
- `source-status-schema` failure for blank source-status safe-next text;
- unchanged `schema_version: 2` project status JSON shape;
- focused tests covering both blank text fields; and
- documentation update for the nonempty source-status text contract.

Status: accepted in
`docs/adr/0105-project-status-nonempty-source-text.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0106: Project Status Command Token Types

Goal: reject non-text command-list entries in source-status records consumed by
project status.

Deliverables:

- `source-status-schema` failure for non-string entries in `commands`;
- `source-status-schema` failure for non-string entries in
  `blocked_runtime_commands`;
- unchanged `schema_version: 2` project status JSON shape;
- focused tests covering non-text command-token rejection; and
- documentation update for the source-status command-token type contract.

Status: accepted in
`docs/adr/0106-project-status-command-token-types.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0107: Project Status Command Field Shapes

Goal: reject malformed command-token field container shapes in source-status
records consumed by project status.

Deliverables:

- `source-status-schema` failure for non-text `command`;
- `source-status-schema` failure for non-list `commands`;
- `source-status-schema` failure for non-list `blocked_runtime_commands`;
- unchanged `schema_version: 2` project status JSON shape;
- focused tests covering each malformed command-token field shape; and
- documentation update for the command-token field-shape contract.

Status: accepted in
`docs/adr/0107-project-status-command-field-shapes.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0108: Project Status Resolution Questions

Goal: expose source-status resolution question IDs from the project status
frontier.

Deliverables:

- `required_resolution_questions` list on each accepted
  `frontier.source_statuses` entry;
- schema bump from project status `schema_version: 2` to `schema_version: 3`;
- focused in-process and JSON CLI tests for resolution-question attribution;
  and
- documentation update for the project status schema change.

Status: accepted in
`docs/adr/0108-project-status-resolution-questions.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0109: Project Status Resolution Question Shape

Goal: reject malformed `required_resolution_questions` metadata in
source-status records consumed by project status.

Deliverables:

- `source-status-schema` failure for non-list
  `required_resolution_questions`;
- `source-status-schema` failure for non-object resolution-question entries;
- `source-status-schema` failure for blank or missing `question_id` values;
- unchanged `schema_version: 3` project status JSON shape;
- focused tests covering malformed resolution-question metadata; and
- documentation update for the resolution-question shape contract.

Status: accepted in
`docs/adr/0109-project-status-resolution-question-shape.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0110: Project Status Text Resolution Questions

Goal: render accepted blocker resolution question IDs in the default project
status text report.

Deliverables:

- `Resolution questions:` section in `format_project_status_report`;
- standard-signal question IDs visible in text status output;
- write-buffer question IDs visible in text status output;
- unchanged `schema_version: 3` project status JSON shape; and
- focused tests covering the text-report question section.

Status: accepted in
`docs/adr/0110-project-status-text-resolution-questions.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0111: Project Status Resolution Question Summaries

Goal: expose source-status resolution question summaries from the project
status frontier.

Deliverables:

- `resolution_questions` list on each accepted `frontier.source_statuses`
  entry;
- each `resolution_questions` item includes `question_id` and `summary`;
- schema bump from project status `schema_version: 3` to `schema_version: 4`;
- default text status renders question IDs with summaries;
- existing `required_resolution_questions` ID lists remain present; and
- focused in-process, JSON CLI, and text-output tests for summary-bearing
  resolution questions.

Status: accepted in
`docs/adr/0111-project-status-resolution-question-summaries.md`. Implemented
in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0112: Project Status Blocked Runtime Surfaces

Goal: expose source-status blocked runtime surfaces from the project status
frontier.

Deliverables:

- `blocked_runtime_surfaces` list on each accepted
  `frontier.source_statuses` entry;
- schema bump from project status `schema_version: 4` to `schema_version: 5`;
- default text status renders blocked runtime surfaces under each contributing
  command label;
- `source-status-schema` failures for malformed `blocked_runtime_surfaces`
  fields; and
- focused in-process, JSON CLI, text-output, and malformed-surface tests.

Status: accepted in
`docs/adr/0112-project-status-blocked-runtime-surfaces.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0113: Transition Registry JSON Entries

Goal: make transition evidence registry JSON list the concrete registered
transition bundles.

Deliverables:

- `bundles` array in `registry_validation_report_payload`;
- each entry includes `bundle_id`, `path`, `claim_id`, and `expected_status`;
- JSON CLI output includes the same bundle entries;
- unchanged registry validation semantics and manifest schema; and
- focused in-process and JSON CLI tests for the transition registry payload.

Status: accepted in `docs/adr/0113-transition-registry-json-entries.md`.
Implemented in `autarkic_systems/evidence_bundle.py`, with tests in
`tests/test_evidence_bundle_registry.py`.

## ADR-0114: Transition Registry JSON Failure Summary

Goal: give transition evidence registry JSON the same compact failure-summary
surface as chain registry JSON.

Deliverables:

- `failed_subjects` array in `registry_validation_report_payload`;
- successful registry JSON reports `failed_subjects: []`;
- failed registry JSON reports rejected validation subjects in order;
- JSON CLI output includes the same failure summary; and
- unchanged registry validation semantics and manifest schema.

Status: accepted in
`docs/adr/0114-transition-registry-json-failure-summary.md`. Implemented in
`autarkic_systems/evidence_bundle.py`, with tests in
`tests/test_evidence_bundle_registry.py`.

## ADR-0115: Project Status Registry Bundles

Goal: make project status JSON list the concrete transition and chain registry
bundle entries checked by the first diagnostic command.

Deliverables:

- `bundles` array in `transition_evidence`;
- `bundles` array in `chain_evidence`;
- missing or malformed registry summaries report `bundles: []`;
- schema bump from project status `schema_version: 5` to
  `schema_version: 6`;
- unchanged registry validation semantics, source-status validation
  semantics, and default text status output; and
- focused in-process and JSON CLI tests for the project status bundle arrays.

Status: accepted in
`docs/adr/0115-project-status-registry-bundles.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0116: Project Status Text Registry Bundles

Goal: render concrete transition and chain registry bundle IDs in the default
project status text report.

Deliverables:

- `Transition evidence bundles:` section in `format_project_status_report`;
- transition bundle IDs and paths visible in text status output;
- `Chain evidence bundles:` section in `format_project_status_report`;
- chain bundle IDs and paths visible in text status output;
- missing or malformed registry summaries render `none` for the affected
  bundle section;
- unchanged project status JSON shape at `schema_version: 6`; and
- focused tests covering green and failed registry text output.

Status: accepted in
`docs/adr/0116-project-status-text-registry-bundles.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0117: Project Status Source AS Boundary

Goal: require source-status records consumed by project status to explain the
AS boundary they enforce.

Deliverables:

- non-empty top-level `as_boundary` requirement for accepted source-status
  records;
- `source-status-schema` failure for missing `as_boundary`;
- `source-status-schema` failure for blank `as_boundary`;
- top-level `as_boundary` in
  `sources/recipient_non_init_command_source_status.json`;
- unchanged project status JSON shape at `schema_version: 6`; and
- focused tests covering accepted checked-in boundaries and malformed
  source-status boundary text.

Status: accepted in
`docs/adr/0117-project-status-source-as-boundary.md`. Implemented in
`autarkic_systems/project_status.py` and
`sources/recipient_non_init_command_source_status.json`, with tests in
`tests/test_project_status_report.py`.

## ADR-0118: Project Status Text AS Boundaries

Goal: render accepted source-status AS boundaries in the default project
status text report.

Deliverables:

- `AS boundaries:` section in `format_project_status_report`;
- recipient non-init AS boundary visible in text status output;
- standard-signal command-token AS boundary visible in text status output;
- write-buffer command-token AS boundary visible in text status output;
- unchanged project status JSON shape at `schema_version: 6`; and
- focused tests covering the text boundary section.

Status: accepted in
`docs/adr/0118-project-status-text-as-boundaries.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0119: Self Non-Init Boundary Coverage

Goal: make the existing unsupported self-command claim/proof boundary explicit
for every blocked non-init command token.

Deliverables:

- positive self-mailbox unsupported manifest examples for `standard-signal`,
  `write-buf-zero`, and `write-buf-one`;
- positive self-target command-buffer append-boundary manifest examples for
  self `standard-signal`, self `write-buf-zero`, and self `write-buf-one`;
- proof-certificate steps for every new manifest example;
- unchanged Universal Cell runtime behavior; and
- focused tests proving the manifest/proof surface covers all three blocked
  self-command tokens.

Status: accepted in
`docs/adr/0119-self-non-init-boundary-coverage.md`. Implemented in
`claims/transition_claims.json` and `claims/proof_certificates.json`, with
tests in `tests/test_self_mailbox_unsupported_claim.py` and
`tests/test_command_buffer_unsupported_claim.py`.

## ADR-0120: Evidence Bundle Covered Examples

Goal: let transition evidence bundles name the positive manifest examples they
cover separately from the single trace-aligned primary example.

Deliverables:

- optional `covered_positive_examples` field on transition evidence bundles;
- validator checks that each covered example exists, is positive, has the
  bundle expected status, and evaluates true;
- covered-example lists in the unsupported self-mailbox and unsupported
  self-target command-buffer bundles;
- drifted covered-example rejection tests; and
- unchanged Universal Cell runtime behavior, schematic traces, SVGs, claims,
  and proof certificates.

Status: accepted in
`docs/adr/0120-evidence-bundle-covered-examples.md`. Implemented in
`autarkic_systems/evidence_bundle.py`,
`evidence/self_mailbox_unsupported_bundle.json`, and
`evidence/command_buffer_unsupported_bundle.json`, with tests in
`tests/test_self_mailbox_unsupported_evidence_bundle.py` and
`tests/test_command_buffer_unsupported_evidence_bundle.py`.

## ADR-0121: Registry Covered Example JSON

Goal: expose transition bundle positive-example coverage in the first-run JSON
registry and project-status surfaces.

Deliverables:

- `positive_example` in each transition registry JSON bundle entry;
- `covered_positive_examples` in each transition registry JSON bundle entry;
- structured fallback values when a bundle cannot be loaded;
- project status JSON `schema_version: 7`;
- unchanged project status text output; and
- focused tests covering registry JSON, CLI JSON, project status JSON, and
  missing-bundle fallback entries.

Status: accepted in
`docs/adr/0121-registry-covered-example-json.md`. Implemented in
`autarkic_systems/evidence_bundle.py` and
`autarkic_systems/project_status.py`, with tests in
`tests/test_evidence_bundle_registry.py` and
`tests/test_project_status_report.py`.

## ADR-0122: Project Status Text Covered Examples

Goal: render transition bundle positive and covered examples in the default
project status text report.

Deliverables:

- `positive example:` lines for transition bundles with `positive_example`;
- `covered examples:` lines for transition bundles with
  `covered_positive_examples`;
- unsupported self-mailbox and self-target command-buffer coverage visible in
  text;
- unchanged project status JSON at `schema_version: 7`; and
- focused project-status text tests.

Status: accepted in
`docs/adr/0122-project-status-text-covered-examples.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0123: Project Status Source-Status Cross-Links

Goal: expose source-status cross-links in project status JSON so automation can
inspect the source-review trail behind the blocked command-token frontier.

Deliverables:

- `additional_source_statuses` arrays on accepted
  `frontier.source_statuses` entries;
- `adr`, `path`, and `summary` fields for each cross-link;
- empty arrays for source-status records without cross-links;
- `source-status-schema` failures for malformed cross-link containers,
  entries, or required text fields;
- project status JSON `schema_version: 8`; and
- focused project-status JSON and schema tests.

Status: accepted in
`docs/adr/0123-source-status-cross-links-json.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0124: Project Status Text Source-Status Cross-Links

Goal: render source-status cross-links in the default project status text
report so human operators can inspect the source-review trail behind the
blocked command-token frontier.

Deliverables:

- an `Additional source statuses:` text section;
- command-grouped source-status cross-links rendered as `ADR -> path: summary`;
- Guile ASMSIM, ASMSIM process-buffer, and official TLA cross-links visible
  for the standard-signal and write-buffer blockers;
- `Additional source statuses: none` when accepted source-status records have
  no cross-links;
- unchanged project status JSON at `schema_version: 8`; and
- focused project-status text tests.

Status: accepted in
`docs/adr/0124-source-status-cross-links-text.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0125: Project Status Source-Status Cross-Link Paths

Goal: require source-status cross-links consumed by project status to point to
existing files.

Deliverables:

- `source-status-schema` failure for missing
  `additional_source_statuses[].path` targets;
- checked-in standard-signal and write-buffer cross-links still accepted;
- unchanged project status JSON at `schema_version: 8`;
- unchanged default text layout from ADR-0124; and
- focused project-status schema tests.

Status: accepted in
`docs/adr/0125-source-status-cross-link-paths.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0126: Project Status Source-Status Cross-Link JSON Targets

Goal: require source-status cross-links consumed by project status to point to
JSON object artifacts, not merely existing files.

Deliverables:

- `source-status-schema` failure for invalid JSON
  `additional_source_statuses[].path` targets;
- `source-status-schema` failure for non-object JSON cross-link targets;
- checked-in standard-signal and write-buffer cross-links still accepted;
- unchanged project status JSON at `schema_version: 8`;
- unchanged default text layout from ADR-0124; and
- focused project-status schema tests.

Status: accepted in
`docs/adr/0126-source-status-cross-link-json-targets.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0127: Standard-Signal Self-Mailbox Exception Evidence

Goal: promote the PRC formal-model self-mailbox exception into the
standard-signal command-semantics source-status artifact.

Deliverables:

- a `formal_model_self_mailbox_exception` witness in
  `sources/standard_signal_command_semantics_status.json`;
- tests that read the PRC formal model and verify the self-mailbox exception
  anchor;
- human-facing source-status documentation that explains the narrowed
  self-target-surface question;
- unchanged Universal Cell runtime behavior;
- unchanged project status JSON at `schema_version: 8`; and
- focused standard-signal source-status tests.

Status: accepted in
`docs/adr/0127-standard-signal-self-mailbox-exception.md`. Implemented in
`sources/standard_signal_command_semantics_status.json` and
`docs/standard-signal-command-semantics-status.md`, with tests in
`tests/test_standard_signal_command_semantics_status.py`.

## ADR-0128: Standard-Signal Command Offset Resolution

Goal: resolve the standard-signal `command-table-offset` question in favor of
the formal PRC stem command-buffer map already encoded by ADR-0026.

Deliverables:

- a `resolved_resolution_questions` entry for `command-table-offset` in
  `sources/standard_signal_command_semantics_status.json`;
- removal of `command-table-offset` from unresolved
  `required_resolution_questions`;
- tests proving the resolved decision points at
  `sources/stem_command_buffer_map.json`;
- project-status tests proving the unresolved standard-signal queue no longer
  includes `command-table-offset`;
- unchanged Universal Cell runtime behavior;
- unchanged project status JSON at `schema_version: 8`; and
- focused standard-signal and project-status tests.

Status: accepted in
`docs/adr/0128-standard-signal-command-offset-resolution.md`. Implemented in
`sources/standard_signal_command_semantics_status.json` and
`docs/standard-signal-command-semantics-status.md`, with tests in
`tests/test_standard_signal_command_semantics_status.py` and
`tests/test_project_status_report.py`.

## ADR-0129: Write-Buffer Command Bit Source Evidence

Goal: record the source-backed sub-decision that the named write-buffer commands
carry literal append bits, without widening runtime execution.

Deliverables:

- a `command_bit_source` witness in
  `sources/write_buffer_command_semantics_status.json`;
- tests proving `write-buf-zero` maps to literal `0` and `write-buf-one` maps
  to literal `1`;
- formal-model, RAA, SEMSIM, and FSMSIM loci for that literal bit source;
- unchanged unresolved write-buffer question IDs;
- unchanged Universal Cell runtime behavior;
- unchanged project status JSON at `schema_version: 8`; and
- focused write-buffer source-status tests.

Status: accepted in
`docs/adr/0129-write-buffer-command-bit-source.md`. Implemented in
`sources/write_buffer_command_semantics_status.json` and
`docs/write-buffer-command-semantics-status.md`, with tests in
`tests/test_write_buffer_command_semantics_status.py`.

## ADR-0130: Project Status Resolved Resolution Questions

Goal: expose already settled source-status resolution questions in project
status JSON and text so future work can distinguish closed decisions from the
remaining command-token frontier.

Deliverables:

- project status JSON `schema_version: 9`;
- `resolved_resolution_questions` arrays on accepted
  `frontier.source_statuses` entries;
- the standard-signal `command-table-offset` decision visible with its
  `sources/stem_command_buffer_map.json` source-status path;
- a default text `Resolved resolution questions:` section;
- `Resolved resolution questions: none` fallback when no accepted source-status
  records have resolved questions;
- `source-status-schema` failures for malformed resolved-question metadata; and
- focused project-status tests.

Status: accepted in
`docs/adr/0130-project-status-resolved-questions.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0131: Project Status Resolved Question Source Paths

Goal: require resolved source-status questions rendered by project status to
point at live JSON object artifacts when they name a `source_status` path.

Deliverables:

- `source-status-schema` failure for missing
  `resolved_resolution_questions[].source_status` targets;
- `source-status-schema` failure for invalid JSON resolved-question source
  targets;
- `source-status-schema` failure for non-object JSON resolved-question source
  targets;
- checked-in standard-signal `command-table-offset` source path still accepted;
- unchanged project status JSON at `schema_version: 9`;
- unchanged default text layout from ADR-0130; and
- focused project-status schema tests.

Status: accepted in
`docs/adr/0131-resolved-question-source-paths.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0132: Project Status Resolved Question Details

Goal: carry operator-critical optional details from resolved source-status
questions into project status JSON and text.

Deliverables:

- project status JSON `schema_version: 10`;
- `formal_command_offset: 0` visible on the standard-signal
  `command-table-offset` resolved question;
- the RAA legacy divergence visible on that resolved question;
- default text detail lines for formal command offset and legacy divergence;
- `source-status-schema` failures for malformed optional detail metadata; and
- focused project-status tests.

Status: accepted in
`docs/adr/0132-project-status-resolved-question-details.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0133: Predicate Result Certificates

Goal: make the transition proof-certificate layer less implicit by adding a
certificate rule that names the predicate evaluated for a manifest example.

Deliverables:

- `predicate-result` proof-certificate rule support;
- optional `predicate` metadata on parsed certificate steps;
- rejection for missing or mismatched `predicate-result` predicate metadata;
- the first fixed-output preservation certificate migrated to
  `predicate-result`;
- transition object-language proof-object rules updated to include
  `predicate-result`; and
- focused proof-certificate and object-language tests.

Status: accepted in `docs/adr/0133-predicate-result-certificates.md`.
Implemented in `autarkic_systems/proof_certificates.py`,
`autarkic_systems/object_language.py`, `claims/proof_certificates.json`, and
`language/transition_claim_language.json`, with tests in
`tests/test_proof_certificates.py` and `tests/test_object_language.py`.

## ADR-0134: Proof Certificate CLI

Goal: make the transition proof-certificate layer directly inspectable from
the command line.

Deliverables:

- `python -m autarkic_systems.proof_certificates` text output;
- `--format json` output with accepted state, claim count, certificate count,
  result count, and per-claim verification results;
- `--claims` and `--certificates` path overrides;
- exit code `0` for accepted proof-certificate surfaces and `1` for rejected
  surfaces; and
- focused CLI tests covering successful and failing manifests.

Status: accepted in `docs/adr/0134-proof-certificate-cli.md`. Implemented in
`autarkic_systems/proof_certificates.py`, with tests in
`tests/test_proof_certificates.py`.

## ADR-0135: Transition Claim CLI

Goal: make the base single-transition claim manifest directly inspectable from
the command line.

Deliverables:

- `python -m autarkic_systems.claim_manifest` text output;
- `--format json` output with accepted state, claim count, example count,
  matched count, result count, and per-example evaluation results;
- `--claims` path override;
- exit code `0` for accepted claim-example surfaces and `1` for mismatched
  example expectations; and
- focused CLI tests covering successful and failing manifests.

Status: accepted in `docs/adr/0135-transition-claim-cli.md`. Implemented in
`autarkic_systems/claim_manifest.py`, with tests in
`tests/test_claim_manifest.py`.

## ADR-0136: Transition Object Language CLI

Goal: make the base transition object-language layer directly inspectable from
the command line.

Deliverables:

- `python -m autarkic_systems.object_language` text output;
- `--format json` output with accepted state, language ID, claim count,
  certificate count, result count, and per-result validation details;
- `--language`, `--claims`, and `--certificates` path overrides;
- exit code `0` for accepted language surfaces and `1` for rejected language
  or claim/proof surfaces; and
- focused CLI tests covering successful and failing language manifests.

Status: accepted in `docs/adr/0136-transition-object-language-cli.md`.
Implemented in `autarkic_systems/object_language.py`, with tests in
`tests/test_object_language.py`.

## ADR-0137: Chain Object Language CLI

Goal: make the transition-chain object-language layer directly inspectable
from the command line.

Deliverables:

- `python -m autarkic_systems.chain_object_language` text output;
- `--format json` output with accepted state, language ID, claim count,
  certificate count, result count, and per-result validation details;
- `--language`, `--claims`, and `--certificates` path overrides;
- exit code `0` for accepted chain language surfaces and `1` for rejected
  language or chain claim/proof surfaces; and
- focused CLI tests covering successful and failing chain language manifests.

Status: accepted in `docs/adr/0137-chain-object-language-cli.md`. Implemented
in `autarkic_systems/chain_object_language.py`, with tests in
`tests/test_chain_object_language.py`.

## ADR-0138: Project Status Language Surfaces

Goal: include the base and chain object-language validation surfaces in the
first project diagnostic command.

Deliverables:

- project status JSON `schema_version: 11`;
- `transition_language` summary with accepted state, language ID, paths,
  counts, failed subjects, result count, and validation results;
- `chain_language` summary with the same shape;
- compact transition and chain language lines in default text output;
- CLI path overrides for transition/chain language, claim, and certificate
  manifests; and
- focused project-status tests covering JSON, text, and CLI output.

Status: accepted in `docs/adr/0138-project-status-language-surfaces.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0139: Project Status Language Failure Text

Goal: make rejected language summaries diagnosable from the default project
status text report.

Deliverables:

- `Language failures: none` when transition and chain language summaries are
  accepted;
- compact transition language failed-subject text when the base language
  summary is rejected;
- compact chain language failed-subject text when the chain language summary
  is rejected;
- unchanged project status JSON at `schema_version: 11`; and
- focused project-status tests for accepted and rejected language text.

Status: accepted in `docs/adr/0139-project-status-language-failure-text.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0140: Project Status Claim And Proof Surfaces

Goal: include the base transition claim-example evaluator and
proof-certificate verifier in the first project diagnostic command.

Deliverables:

- project status JSON `schema_version: 12`;
- `transition_claims` summary with accepted state, path, claim count, example
  count, matched count, failed subjects, result count, and per-example
  validation results;
- `transition_proof_certificates` summary with accepted state, paths, claim
  count, certificate count, failed subjects, result count, and
  per-certificate validation results;
- compact transition claim and proof-certificate lines in default text output;
- compact claim/proof failed-subject text when either lower surface is
  rejected; and
- focused project-status tests covering JSON, text, CLI output, and rejected
  claim/proof fixtures.

Status: accepted in
`docs/adr/0140-project-status-claim-proof-surfaces.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0141: Project Status Chain Claim Surface

Goal: include the transition-chain claim validator in the first project
diagnostic command.

Deliverables:

- project status JSON `schema_version: 13`;
- `chain_claims` summary with accepted state, language ID, paths, claim count,
  certificate count, failed subjects, result count, and chain validation
  results;
- compact transition-chain claim line in default text output;
- compact chain-claim failed-subject text when the surface is rejected; and
- focused project-status tests covering JSON, text, CLI output, and a rejected
  chain proof-certificate fixture.

Status: accepted in
`docs/adr/0141-project-status-chain-claim-surface.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0142: Write-Buffer Standard-Signal Interaction Resolution

Goal: remove the settled write-buffer bit-source/high-rail-derivation question
from the unresolved queue without widening write-buffer runtime execution.

Deliverables:

- a `resolved_resolution_questions` entry for `standard-signal-interaction` in
  `sources/write_buffer_command_semantics_status.json`;
- removal of `standard-signal-interaction` from unresolved write-buffer
  `required_resolution_questions`;
- write-buffer source-status tests proving the remaining unresolved queue is
  limited to execution surface, buffer-full behavior, and post-append clearing;
- project-status tests proving JSON/text expose the resolved write-buffer
  decision and preserve project status `schema_version: 13`;
- unchanged Universal Cell runtime behavior; and
- focused write-buffer and project-status tests.

Status: accepted in
`docs/adr/0142-write-buffer-standard-signal-interaction.md`. Implemented in
`sources/write_buffer_command_semantics_status.json` and
`docs/write-buffer-command-semantics-status.md`, with tests in
`tests/test_write_buffer_command_semantics_status.py` and
`tests/test_project_status_report.py`.

## ADR-0143: Standard-Signal Self-Mailbox Resolution Detail

Goal: expose the formal-model self-mailbox exception as a resolved
standard-signal sub-decision without widening command-token execution.

Deliverables:

- a `resolved_resolution_questions` entry for
  `self-mailbox-standard-signal-binary-input-equivalence` in
  `sources/standard_signal_command_semantics_status.json`;
- unchanged unresolved standard-signal `self-target-surface` blocker;
- standard-signal source-status tests proving the resolved detail points at
  the formal self-mailbox exception;
- project-status tests proving JSON/text expose the resolved standard-signal
  self-mailbox equivalence decision while preserving project status
  `schema_version: 13`;
- unchanged Universal Cell runtime behavior; and
- focused standard-signal and project-status tests.

Status: accepted in
`docs/adr/0143-standard-signal-self-mailbox-resolution-detail.md`. Implemented
in `sources/standard_signal_command_semantics_status.json` and
`docs/standard-signal-command-semantics-status.md`, with tests in
`tests/test_standard_signal_command_semantics_status.py` and
`tests/test_project_status_report.py`.

## ADR-0144: Resolution Question Evidence Surface

Goal: expose the source conflict or missing authority behind each unresolved
command-token blocker from the first project diagnostic command.

Deliverables:

- project status JSON `schema_version: 14`;
- `resolution_question_evidence` arrays on accepted source-status entries;
- default text `Resolution question evidence:` output grouped by command;
- fail-closed source-status schema validation for malformed evidence metadata;
- standard-signal and write-buffer source-status evidence for each unresolved
  question;
- unchanged Universal Cell runtime behavior; and
- focused project-status tests covering JSON, text, and malformed evidence
  fixtures.

Status: accepted in `docs/adr/0144-resolution-question-evidence.md`.
Implemented in `autarkic_systems/project_status.py`,
`sources/standard_signal_command_semantics_status.json`, and
`sources/write_buffer_command_semantics_status.json`, with tests in
`tests/test_project_status_report.py`.

## ADR-0145: Source-Status Frontier CLI

Goal: expose the blocked command-token source-status frontier directly without
requiring the full project status report.

Deliverables:

- `python -m autarkic_systems.source_status` text output;
- `python -m autarkic_systems.source_status --format json` with
  `schema_version: 1`;
- accepted/rejected status derived from missing or invalid source-status
  paths;
- reuse of the existing project-status frontier validation contract;
- missing-path and schema-invalid fixture tests; and
- unchanged Universal Cell runtime behavior.

Status: accepted in `docs/adr/0145-source-status-frontier-cli.md`.
Implemented in `autarkic_systems/source_status.py`, with tests in
`tests/test_source_status_frontier_cli.py`.

## ADR-0146: Resolution Evidence Question Matching

Goal: prevent source-status evidence from attaching to misspelled or stale
unresolved question IDs.

Deliverables:

- fail-closed validation for
  `resolution_question_evidence[].question_id` values that do not match a
  `required_resolution_questions[].question_id` in the same source-status
  record;
- unchanged project status `schema_version: 14`;
- unchanged source-status frontier `schema_version: 1`;
- project-status and source-status frontier tests covering the mismatch; and
- unchanged Universal Cell runtime behavior.

Status: accepted in `docs/adr/0146-resolution-evidence-question-match.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py` and
`tests/test_source_status_frontier_cli.py`.

## ADR-0147: Resolution Evidence Coverage

Goal: require every unresolved source-status question to carry a matching
source evidence entry.

Deliverables:

- fail-closed validation when a source-status record has unresolved
  `required_resolution_questions` but no `resolution_question_evidence`;
- fail-closed validation when evidence covers only part of the unresolved
  question list;
- unchanged project status `schema_version: 14`;
- unchanged source-status frontier `schema_version: 1`;
- project-status and source-status frontier tests covering missing and partial
  coverage; and
- unchanged Universal Cell runtime behavior.

Status: accepted in `docs/adr/0147-resolution-evidence-coverage.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py` and
`tests/test_source_status_frontier_cli.py`.

## ADR-0148: Standard-Signal Recipient Surface Resolution

Goal: move the standard-signal recipient command-message surface from
unresolved to the existing recipient non-init rejection boundary.

Deliverables:

- `recipient-surface` removed from standard-signal unresolved
  `required_resolution_questions`;
- `recipient-surface` added to standard-signal
  `resolved_resolution_questions`;
- standard-signal blocked runtime surfaces narrowed to self-mailbox and
  self-target command-buffer surfaces;
- project-status and source-status frontier text/JSON output showing the
  settled recipient-surface decision;
- focused standard-signal, project-status, and source-status frontier tests;
  and
- unchanged Universal Cell runtime behavior.

Status: accepted in
`docs/adr/0148-standard-signal-recipient-surface-resolution.md`. Implemented
in `sources/standard_signal_command_semantics_status.json`, with tests in
`tests/test_standard_signal_command_semantics_status.py`,
`tests/test_project_status_report.py`, and
`tests/test_source_status_frontier_cli.py`.

## ADR-0149: Resolution Question Disjointness

Goal: reject source-status records that report the same question as both
unresolved and resolved.

Deliverables:

- shared source-status validation for overlap between
  `required_resolution_questions[].question_id` and
  `resolved_resolution_questions[].question_id`;
- project-status and source-status frontier schema-failure tests covering the
  overlap;
- unchanged project status `schema_version: 14`;
- unchanged source-status frontier `schema_version: 1`; and
- unchanged accepted frontier payload shape.

Status: accepted in `docs/adr/0149-resolution-question-disjointness.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py` and
`tests/test_source_status_frontier_cli.py`.

## ADR-0150: Standard-Signal Command Token Binary-Input Resolution

Goal: resolve the standard-signal command-token/binary-input equivalence
question without selecting self-target command-token behavior.

Deliverables:

- `command-token-vs-binary-input` removed from standard-signal unresolved
  `required_resolution_questions`;
- `command-token-vs-binary-input` added to standard-signal
  `resolved_resolution_questions`;
- standard-signal unresolved source evidence narrowed to `self-target-surface`;
- project-status and source-status frontier text/JSON output showing the
  settled negative equivalence decision;
- focused standard-signal, project-status, and source-status frontier tests;
  and
- unchanged Universal Cell runtime behavior.

Status: accepted in
`docs/adr/0150-standard-signal-command-token-binary-input-resolution.md`.
Implemented in `sources/standard_signal_command_semantics_status.json`, with
tests in `tests/test_standard_signal_command_semantics_status.py`,
`tests/test_project_status_report.py`, and
`tests/test_source_status_frontier_cli.py`.

## ADR-0151: Standard-Signal Self-Target Resolution

Goal: resolve the remaining standard-signal self-target-surface question
through existing unsupported preservation boundaries.

Deliverables:

- `self-target-surface` removed from standard-signal unresolved
  `required_resolution_questions`;
- `self-target-surface` added to standard-signal
  `resolved_resolution_questions`;
- standard-signal unresolved source evidence reduced to an empty list;
- existing self-mailbox unsupported and command-buffer unsupported evidence
  bundles updated to name the standard-signal settled boundary;
- project-status and source-status frontier text/JSON output showing no live
  standard-signal resolution questions; and
- unchanged Universal Cell runtime behavior.

Status: accepted in `docs/adr/0151-standard-signal-self-target-resolution.md`.
Implemented in `sources/standard_signal_command_semantics_status.json`,
`evidence/self_mailbox_unsupported_bundle.json`, and
`evidence/command_buffer_unsupported_bundle.json`, with tests in
`tests/test_standard_signal_command_semantics_status.py`,
`tests/test_project_status_report.py`, and
`tests/test_source_status_frontier_cli.py`.

## ADR-0152: Write-Buffer Recipient Surface Resolution

Goal: resolve delivered recipient write-buffer command messages through the
existing recipient non-init rejection boundary while keeping self-target
write-buffer execution questions open.

Deliverables:

- `recipient-command-message` removed from write-buffer blocked runtime
  surfaces;
- `recipient-surface` added to write-buffer `resolved_resolution_questions`;
- the old unresolved `recipient-vs-stem-surface` question replaced by
  `self-target-surface`;
- write-buffer unresolved evidence updated to describe only the self-target
  surface;
- project-status and source-status frontier text/JSON output showing the
  settled recipient surface and narrowed self-target question; and
- unchanged Universal Cell runtime behavior.

Status: accepted in
`docs/adr/0152-write-buffer-recipient-surface-resolution.md`. Implemented in
`sources/write_buffer_command_semantics_status.json`, with tests in
`tests/test_write_buffer_command_semantics_status.py`,
`tests/test_project_status_report.py`, and
`tests/test_source_status_frontier_cli.py`.

## ADR-0153: Write-Buffer Self-Target Surface Resolution

Goal: resolve self-target write-buffer command tokens through the existing
unsupported preservation boundaries while keeping append execution semantics
open.

Deliverables:

- `self-target-surface` removed from write-buffer unresolved
  `required_resolution_questions`;
- `self-target-surface` added to write-buffer `resolved_resolution_questions`;
- write-buffer unresolved source evidence narrowed to `buffer-full-boundary`
  and `post-append-clearing`;
- existing self-mailbox unsupported and command-buffer unsupported evidence
  bundles updated to name the write-buffer settled boundary;
- project-status and source-status frontier text/JSON output showing only
  buffer-full and post-append clearing as live write-buffer questions; and
- unchanged Universal Cell runtime behavior.

Status: accepted in
`docs/adr/0153-write-buffer-self-target-surface-resolution.md`. Implemented in
`sources/write_buffer_command_semantics_status.json`,
`evidence/self_mailbox_unsupported_bundle.json`, and
`evidence/command_buffer_unsupported_bundle.json`, with tests in
`tests/test_write_buffer_command_semantics_status.py`,
`tests/test_project_status_report.py`, and
`tests/test_source_status_frontier_cli.py`.

## ADR-0154: Source-Status Execution Readiness Gate

Goal: make command-token execution readiness machine-checkable so unresolved
write-buffer execution semantics cannot be mistaken for an implementation-ready
frontier.

Deliverables:

- optional `execution_readiness` extraction and text rendering in
  project-status and source-status frontier reports;
- project-status schema bumped to `15`;
- source-status frontier schema bumped to `2`;
- schema rejection for malformed readiness objects, non-boolean
  `execution_change_allowed`, and readiness blockers that do not match live
  unresolved `required_resolution_questions`;
- write-buffer source-status `execution_readiness` marked `blocked`, with
  execution changes disallowed until `buffer-full-boundary` and
  `post-append-clearing` are resolved; and
- unchanged Universal Cell runtime behavior.

Status: accepted in
`docs/adr/0154-source-status-execution-readiness-gate.md`. Implemented in
`autarkic_systems/project_status.py`, `autarkic_systems/source_status.py`, and
`sources/write_buffer_command_semantics_status.json`, with tests in
`tests/test_project_status_report.py` and
`tests/test_source_status_frontier_cli.py`.

## ADR-0155: Execution Readiness Coverage

Goal: require blocked execution-readiness gates to name every live unresolved
question that still blocks execution.

Deliverables:

- schema rejection for blocked readiness objects that omit one or more live
  `required_resolution_questions` IDs from
  `blocked_by_resolution_questions`;
- unchanged project-status schema `15`;
- unchanged source-status frontier schema `2`; and
- unchanged Universal Cell runtime behavior.

Status: accepted in `docs/adr/0155-execution-readiness-coverage.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0156: Execution Readiness Allowed-Question Guard

Goal: prevent a source-status record from allowing execution changes while it
still has live unresolved questions.

Deliverables:

- schema rejection for `execution_readiness.execution_change_allowed: true`
  when `required_resolution_questions` is non-empty;
- unchanged project-status schema `15`;
- unchanged source-status frontier schema `2`; and
- unchanged Universal Cell runtime behavior.

Status: accepted in
`docs/adr/0156-execution-readiness-allowed-question-guard.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0157: Execution Readiness Blocked Consistency

Goal: prevent contradictory readiness metadata where execution is marked
blocked but execution changes are allowed.

Deliverables:

- schema rejection for `execution_readiness.decision: blocked` combined with
  `execution_change_allowed: true`;
- unchanged project-status schema `15`;
- unchanged source-status frontier schema `2`; and
- unchanged Universal Cell runtime behavior.

Status: accepted in
`docs/adr/0157-execution-readiness-blocked-consistency.md`. Implemented in
`autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0158: Resolution Question ID Uniqueness

Goal: prevent duplicate source-status question IDs from creating ambiguous
frontier output or hiding behind set-based evidence/readiness checks.

Deliverables:

- schema rejection for duplicate
  `required_resolution_questions[].question_id` values;
- schema rejection for duplicate
  `resolved_resolution_questions[].question_id` values;
- unchanged project-status schema `15`;
- unchanged source-status frontier schema `2`; and
- unchanged Universal Cell runtime behavior.

Status: accepted in `docs/adr/0158-resolution-question-id-uniqueness.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0159: Write-Buffer Full-Boundary Resolution

Goal: resolve the write-buffer full-buffer boundary without widening runtime
execution.

Deliverables:

- `buffer-full-boundary` removed from write-buffer unresolved
  `required_resolution_questions`;
- `buffer-full-boundary` added to write-buffer `resolved_resolution_questions`;
- structured source-status basis for the formal less-than-full write guard and
  RAA `buffer-full?` guard;
- write-buffer execution-readiness blockers narrowed to
  `post-append-clearing`;
- unchanged project-status schema `15`;
- unchanged source-status frontier schema `2`; and
- unchanged Universal Cell runtime behavior.

Status: accepted in
`docs/adr/0159-write-buffer-full-boundary-resolution.md`. Implemented in
`sources/write_buffer_command_semantics_status.json` and
`docs/write-buffer-command-semantics-status.md`, with tests in
`tests/test_write_buffer_command_semantics_status.py`,
`tests/test_project_status_report.py`, and
`tests/test_source_status_frontier_cli.py`.

## ADR-0160: Write-Buffer Post-Append Resolution

Goal: resolve the final write-buffer post-append clearing question without
widening runtime execution.

Deliverables:

- `post-append-clearing` removed from write-buffer unresolved
  `required_resolution_questions`;
- `post-append-clearing` added to write-buffer
  `resolved_resolution_questions`;
- structured source-status basis for selecting RAA/FSMSIM buffer preservation
  and recording SEMSIM buffer clearing as legacy divergence;
- write-buffer `execution_readiness` marked ready, with execution changes
  allowed for a later implementation ADR;
- unchanged project-status schema `15`;
- unchanged source-status frontier schema `2`; and
- unchanged Universal Cell runtime behavior.

Status: accepted in
`docs/adr/0160-write-buffer-post-append-resolution.md`. Implemented in
`sources/write_buffer_command_semantics_status.json` and
`docs/write-buffer-command-semantics-status.md`, with tests in
`tests/test_write_buffer_command_semantics_status.py`,
`tests/test_project_status_report.py`, and
`tests/test_source_status_frontier_cli.py`.

## ADR-0161: Write-Buffer Command Execution

Goal: implement the source-ready write-buffer append slice for direct
self-mailbox and completed self-target command-buffer commands.

Deliverables:

- direct `self_mailbox` `write-buf-zero` / `write-buf-one` commands append
  literal `0` / `1`, clear the mailbox source, and preserve the control rail;
- completed self-target command buffers decoding to `write-buf-zero` /
  `write-buf-one` append the literal command bit as the new buffer content and
  clear the command-buffer source;
- unsupported self-mailbox and self-target command-buffer claims narrow to
  `standard-signal`;
- new write-buffer transition claims, proof certificates, and object-language
  vocabulary cover the append behavior;
- transition-chain language admits the new sender result statuses while
  preserving the non-neighbor-delivery chain boundaries;
- source-status and project-status reports mark write-buffer self-target
  execution implemented while recipient write-buffer command-message input
  remains rejected; and
- unchanged project-status schema `15` and source-status frontier schema `2`.

Status: accepted in
`docs/adr/0161-write-buffer-command-execution.md`. Implemented in
`autarkic_systems/universal_cell.py`,
`autarkic_systems/transition_predicates.py`, the transition claim/proof
manifests, the transition object languages, write-buffer source-status
artifacts, and focused runtime/claim/status tests.

## ADR-0162: Write-Buffer Execution Evidence Bundles

Goal: register the ADR-0161 write-buffer execution surfaces as integrated
transition evidence bundles without changing runtime behavior.

Deliverables:

- a schematic-linked trace and renderer-locked SVG for direct self-mailbox
  `write-buf-one` execution;
- a schematic-linked trace and renderer-locked SVG for completed self-target
  command-buffer `write-buf-one` execution;
- `evidence/self_mailbox_write_buffer_bundle.json` covering
  `UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED`;
- `evidence/self_command_buffer_write_buffer_bundle.json` covering
  `UC-STEM-COMMAND-BUFFER-SELF-WRITE-BUFFER-APPENDED`;
- evidence registry expansion from eight to ten transition bundles;
- source-status safe-next movement from the completed evidence task to
  recipient write-buffer command-message source resolution; and
- unchanged project-status schema `15` and source-status frontier schema `2`.

Status: accepted in
`docs/adr/0162-write-buffer-execution-evidence-bundle.md`. Implemented in the
schematic trace/SVG validators, the new trace and SVG artifacts, the transition
evidence registry, write-buffer and stem source-status records, and focused
trace/SVG/evidence/status tests.

## ADR-0163: Recipient Write-Buffer Rejection Coverage

Goal: make delivered recipient write-buffer rejection explicit in the existing
recipient non-init claim/proof/evidence surface.

Deliverables:

- positive upstream `write-buf-zero` and `write-buf-one` rejection examples in
  `UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED`;
- proof-certificate steps for both new positive examples;
- recipient non-init evidence-bundle `covered_positive_examples` listing the
  standard-signal primary example plus both write-buffer rejection examples;
- project-status transition claim coverage updated from 37 to 39 matched
  examples;
- updated recipient/write-buffer source-status documentation; and
- unchanged Universal Cell runtime behavior, trace artifacts, SVG artifacts,
  project-status schema `15`, and source-status frontier schema `2`.

Status: accepted in
`docs/adr/0163-recipient-write-buffer-rejection-coverage.md`. Implemented in
the transition claim/proof manifests, recipient non-init evidence bundle,
recipient source-status record, and focused claim/evidence/status tests.

## ADR-0164: Neighbor Write-Buffer Zero Rejection Chain Coverage

Goal: extend the transition-chain claim surface so neighbor-delivered
`write-buf-zero` rejection is explicit alongside the existing `write-buf-one`
rejection path.

Deliverables:

- a completed neighbor-c `write-buf-zero` handoff example in
  `tests/test_neighbor_delivery_recipient_chain.py`;
- a negative consumed-chain example for delivered `write-buf-zero`;
- a positive rejected-chain example for delivered `write-buf-zero`;
- proof-certificate steps for both new chain examples;
- chain-claim CLI and project-status text updated from seven to nine evaluated
  chain examples; and
- unchanged Universal Cell runtime behavior, chain traces, SVGs, evidence
  bundles, project-status schema `15`, and source-status frontier schema `2`.

Status: accepted in
`docs/adr/0164-neighbor-write-buffer-zero-rejection-chain.md`. Implemented in
the transition-chain claim/proof manifests and focused chain helper,
chain-claim CLI, and project-status tests.

## ADR-0165: Standard-Signal Execution Readiness Boundary

Goal: make the settled `standard-signal` unsupported boundary explicit as
execution-readiness metadata.

Deliverables:

- `sources/standard_signal_command_semantics_status.json` exposes
  `execution_readiness.decision: preserved-unsupported`;
- execution changes for `standard-signal` command-token behavior remain
  disallowed unless new source evidence replaces the existing unsupported
  boundary;
- project-status JSON/text and source-status frontier JSON/text render the
  standard-signal readiness decision alongside write-buffer readiness; and
- unchanged Universal Cell runtime behavior, claims, proof certificates,
  traces, SVGs, evidence bundles, project-status schema `15`, and
  source-status frontier schema `2`.

Status: accepted in
`docs/adr/0165-standard-signal-execution-readiness.md`. Implemented in the
standard-signal source-status record and focused source-status/project-status
tests.

## ADR-0166: Standard-Signal Safe-Next Boundary

Goal: align source-status safe-next wording with the ADR-0165
preserved-unsupported standard-signal boundary.

Deliverables:

- `sources/standard_signal_command_semantics_status.json` points future
  standard-signal work at new source evidence before any execution change;
- recipient non-init and multi-command source-status records point their
  safe-next fields at recipient write-buffer command-message semantics;
- project-status and source-status frontier reports render the narrowed
  safe-next queue; and
- unchanged Universal Cell runtime behavior, claims, proof certificates,
  traces, SVGs, evidence bundles, project-status schema `15`, and
  source-status frontier schema `2`.

Status: accepted in
`docs/adr/0166-standard-signal-safe-next-boundary.md`. Implemented in the
source-status records and focused source-status/project-status tests.

## ADR-0167: Recipient Write-Buffer Readiness Question

Goal: make the remaining recipient write-buffer command-message surface an
explicit live source-status question.

Deliverables:

- `sources/write_buffer_command_semantics_status.json` lists
  `recipient-command-message-surface` as a live resolution question with
  matching source evidence;
- write-buffer execution readiness changes from broad `implemented` to
  `self-target-implemented-recipient-blocked`;
- project-status JSON/text and source-status frontier JSON/text render the
  recipient write-buffer question, evidence, and readiness blocker; and
- unchanged Universal Cell runtime behavior, claims, proof certificates,
  traces, SVGs, evidence bundles, project-status schema `15`, and
  source-status frontier schema `2`.

Status: accepted in
`docs/adr/0167-recipient-write-buffer-readiness-question.md`. Implemented in
the write-buffer source-status record and focused write-buffer/source-status/
project-status tests.

## ADR-0168: Recipient Write-Buffer Surface Resolution

Goal: resolve delivered recipient `write-buf-zero` and `write-buf-one`
command-message semantics as source-ready append behavior while preserving
the current runtime rejection boundary until implementation.

Deliverables:

- `sources/write_buffer_command_semantics_status.json` resolves
  `recipient-command-message-surface` as
  `execute-recipient-write-buffer-command-message-append`;
- write-buffer `required_resolution_questions` and
  `resolution_question_evidence` are empty again;
- write-buffer execution readiness is
  `recipient-command-message-source-ready`, with execution changes allowed and
  no blockers;
- recipient-facing source-status records keep the checked current runtime
  rejection boundary visible while moving their safe-next guidance to
  recipient write-buffer command-message implementation;
- project-status JSON/text and source-status frontier JSON/text render the
  source-ready recipient write-buffer readiness and implementation safe-next
  slice; and
- unchanged Universal Cell runtime behavior, claims, proof certificates,
  traces, SVGs, evidence bundles, project-status schema `15`, and
  source-status frontier schema `2`.

Status: accepted in
`docs/adr/0168-recipient-write-buffer-surface-resolution.md`. Implemented in
the write-buffer and recipient source-status records plus focused
write-buffer/source-status/project-status/recipient frontier tests.

## ADR-0169: Recipient Write-Buffer Command Execution

Goal: implement delivered recipient `write-buf-zero` and `write-buf-one`
command-message append behavior.

Deliverables:

- fixed and stem recipient cells append the command's literal bit for a single
  delivered write-buffer command message;
- the active command source is cleared while role, memory, output, automail,
  self-mailbox, control, and existing buffer contents are preserved;
- the full-buffer boundary still reports `stem-buffer-full` without changing
  the cell;
- single delivered `standard-signal` command messages and multi-command
  conflicts remain rejected;
- a new transition claim/proof/object-language surface records recipient
  write-buffer append execution;
- delivered write-buffer neighbor handoffs move to the consumed-chain examples,
  while delivered `standard-signal` becomes the rejection-chain witness;
- source/project status report only `standard-signal` as blocked and move the
  write-buffer safe-next slice to evidence-bundle promotion; and
- project-status schema `15` and source-status frontier schema `2` remain
  unchanged.

Status: accepted in
`docs/adr/0169-recipient-write-buffer-command-execution.md`. Implemented in
runtime, claim/proof/language, chain, source-status, and project-status
surfaces.

## ADR-0170: Recipient Write-Buffer Command Evidence Bundle

Goal: promote ADR-0169 recipient write-buffer command-message append behavior
into the transition evidence registry.

Deliverables:

- `schematics/recipient_write_buffer_command_message_trace.json` records one
  upstream `write-buf-zero` recipient append trace;
- `schematics/recipient_write_buffer_command_message_trace.svg` is generated
  from that trace and checked against renderer output;
- `evidence/recipient_write_buffer_command_message_bundle.json` ties the
  recipient write-buffer claim, proof certificate, trace, SVG, hardware map,
  and source-status boundaries together;
- `evidence/manifest.json` now registers 11 transition evidence bundles;
- write-buffer source status marks the recipient evidence bundle implemented;
- project/source status keep `standard-signal` as the only blocked command and
  active safe-next frontier before the follow-up source review; and
- project-status schema `15` and source-status frontier schema `2` remain
  unchanged.

Status: accepted in
`docs/adr/0170-recipient-write-buffer-command-evidence-bundle.md`. Implemented
in trace, SVG, evidence-bundle, registry, source-status, and project-status
surfaces.

## ADR-0171: Standard-Signal Source Review Snapshot

Goal: perform the remaining source-review gate before any standard-signal
command-token execution change.

Deliverables:

- `sources/standard_signal_source_review_status.json` records the dated review
  snapshot for AS, AFS, PRC, SJAS, Proflog, and LeanTAP remote heads;
- the PRC remote and local witness heads remain at
  `7e82c73fac8f108faac801a5c65e2c2b92653ba5`;
- `sources/standard_signal_command_semantics_status.json` links the latest
  source review and keeps execution changes disallowed;
- recipient non-init and multi-command source-status records move to the
  `no-standard-signal-command-token-execution-change-without-new-source-evidence`
  guard;
- project/source status keep `standard-signal` as the only blocked command but
  render no active aggregate safe-next slice; and
- Universal Cell runtime behavior, claims, proof certificates, traces, SVGs,
  evidence bundles, project-status schema `15`, and source-status frontier
  schema `2` remain unchanged.

Status: accepted in
`docs/adr/0171-standard-signal-source-review-snapshot.md`. Implemented in the
standard-signal source-review snapshot, source-status records, and focused
source-status/project-status tests.

## ADR-0172: Consumed-Input Predicate Result Certificates

Goal: make the consumed-input clearing proof certificate name the predicate it
evaluates instead of relying only on manifest-example lookup.

Deliverables:

- `UC-FIXED-CONSUMED-INPUT-CLEARED` proof-certificate steps use
  `predicate-result`;
- both consumed-input certificate steps name `consumed_input_cleared`;
- proof-certificate text/JSON and aggregate project-status reports render the
  consumed-input certificate as two predicate-result steps; and
- Universal Cell runtime behavior, transition claims, object-language schema,
  evidence bundles, source-status records, and status schema versions remain
  unchanged.

Status: accepted in
`docs/adr/0172-consumed-input-predicate-result-certificates.md`. Implemented in
the proof-certificate manifest and focused proof/project-status tests.

## ADR-0173: Memory Rule Predicate Result Certificates

Goal: make the fixed-role memory-rule proof certificate name the predicate it
evaluates instead of relying only on manifest-example lookup.

Deliverables:

- `UC-FIXED-MEMORY-RULE` proof-certificate steps use `predicate-result`;
- both memory-rule certificate steps name `fixed_role_memory_rule`;
- proof-certificate text/JSON and aggregate project-status reports render the
  memory-rule certificate as two predicate-result steps; and
- Universal Cell runtime behavior, transition claims, object-language schema,
  evidence bundles, source-status records, and status schema versions remain
  unchanged.

Status: accepted in
`docs/adr/0173-memory-rule-predicate-result-certificates.md`. Implemented in
the proof-certificate manifest and focused proof/project-status tests.

## ADR-0174: Stem-Init Predicate Result Certificates

Goal: make the stem-init reset proof certificate name the predicate it
evaluates instead of relying only on manifest-example lookup.

Deliverables:

- `UC-FIXED-STEM-INIT-RESET` proof-certificate steps use
  `predicate-result`;
- both stem-init certificate steps name `stem_init_resets_to_stem`;
- proof-certificate text/JSON and aggregate project-status reports render the
  stem-init certificate as two predicate-result steps; and
- Universal Cell runtime behavior, transition claims, object-language schema,
  evidence bundles, source-status records, and status schema versions remain
  unchanged.

Status: accepted in
`docs/adr/0174-stem-init-predicate-result-certificates.md`. Implemented in the
proof-certificate manifest and focused proof/project-status tests.

## ADR-0175: Automail Predicate Result Certificates

Goal: make the stem automail reconfiguration proof certificate name the
predicate it evaluates instead of relying only on manifest-example lookup.

Deliverables:

- `UC-STEM-AUTOMAIL-RECONFIGURES` proof-certificate steps use
  `predicate-result`;
- both automail certificate steps name `automail_reconfigures_stem`;
- proof-certificate text/JSON and aggregate project-status reports render the
  automail certificate as two predicate-result steps; and
- Universal Cell runtime behavior, transition claims, object-language schema,
  evidence bundles, source-status records, and status schema versions remain
  unchanged.

Status: accepted in
`docs/adr/0175-automail-predicate-result-certificates.md`. Implemented in the
proof-certificate manifest and focused proof/project-status tests.

## ADR-0176: Stem Buffer Predicate Result Certificates

Goal: make the stem buffer accumulation proof certificate name the predicate
it evaluates instead of relying only on manifest-example lookup.

Deliverables:

- `UC-STEM-BUFFER-ACCUMULATES` proof-certificate steps use
  `predicate-result`;
- all four stem-buffer certificate steps name `stem_buffer_accumulates`;
- proof-certificate text/JSON and aggregate project-status reports render the
  stem-buffer certificate as four predicate-result steps; and
- Universal Cell runtime behavior, transition claims, object-language schema,
  evidence bundles, source-status records, and status schema versions remain
  unchanged.

Status: accepted in
`docs/adr/0176-stem-buffer-predicate-result-certificates.md`. Implemented in
the proof-certificate manifest and focused proof/project-status tests.

## ADR-0177: Self-Mailbox Init Predicate Result Certificates

Goal: make the self-mailbox init command proof certificate name the predicate
it evaluates instead of relying only on manifest-example lookup.

Deliverables:

- `UC-STEM-SELF-MAILBOX-INIT-COMMAND` proof-certificate steps use
  `predicate-result`;
- both self-mailbox init certificate steps name
  `self_mailbox_executes_init_command`;
- proof-certificate text/JSON and aggregate project-status reports render the
  self-mailbox init certificate as two predicate-result steps; and
- Universal Cell runtime behavior, transition claims, object-language schema,
  evidence bundles, source-status records, and status schema versions remain
  unchanged.

Status: accepted in
`docs/adr/0177-self-mailbox-init-predicate-result-certificates.md`.
Implemented in the proof-certificate manifest and focused proof/project-status
tests.

## ADR-0178: Self-Mailbox Unsupported Predicate Result Certificates

Goal: make the self-mailbox unsupported-command preservation proof certificate
name the predicate it evaluates instead of relying only on manifest-example
lookup.

Deliverables:

- `UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED` proof-certificate steps use
  `predicate-result`;
- both self-mailbox unsupported certificate steps name
  `self_mailbox_preserves_unsupported_command`;
- proof-certificate text/JSON and aggregate project-status reports render the
  self-mailbox unsupported certificate as two predicate-result steps; and
- Universal Cell runtime behavior, transition claims, object-language schema,
  evidence bundles, source-status records, and status schema versions remain
  unchanged.

Status: accepted in
`docs/adr/0178-self-mailbox-unsupported-predicate-result-certificates.md`.
Implemented in the proof-certificate manifest, focused proof/project-status
tests, and the self-mailbox unsupported claim note.

## ADR-0179: Self-Mailbox Write-Buffer Predicate Result Certificates

Goal: make the direct self-mailbox write-buffer append proof certificate name
the predicate it evaluates instead of relying only on manifest-example lookup.

Deliverables:

- `UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED` proof-certificate steps use
  `predicate-result`;
- all three self-mailbox write-buffer certificate steps name
  `self_mailbox_write_buffer_appends_literal`;
- proof-certificate text/JSON and aggregate project-status reports render the
  self-mailbox write-buffer certificate as three predicate-result steps; and
- Universal Cell runtime behavior, transition claims, object-language schema,
  evidence bundles, source-status records, and status schema versions remain
  unchanged.

Status: accepted in
`docs/adr/0179-self-mailbox-write-buffer-predicate-result-certificates.md`.
Implemented in the proof-certificate manifest and focused proof/project-status
tests.

## ADR-0180: Self Command-Buffer Init Predicate Result Certificates

Goal: make the completed self-target command-buffer init dispatch proof
certificate name the predicate it evaluates instead of relying only on
manifest-example lookup.

Deliverables:

- `UC-STEM-COMMAND-BUFFER-SELF-INIT` proof-certificate steps use
  `predicate-result`;
- both self command-buffer init certificate steps name
  `stem_command_buffer_executes_self_init`;
- proof-certificate text/JSON and aggregate project-status reports render the
  self command-buffer init certificate as two predicate-result steps; and
- Universal Cell runtime behavior, transition claims, object-language schema,
  evidence bundles, source-status records, and status schema versions remain
  unchanged.

Status: accepted in
`docs/adr/0180-self-command-buffer-init-predicate-result-certificates.md`.
Implemented in the proof-certificate manifest, focused proof/project-status
tests, and the self command-buffer init claim note.

## ADR-0181: Command-Buffer Unsupported Predicate Result Certificates

Goal: make the completed self-target command-buffer unsupported-preservation
proof certificate name the predicate it evaluates instead of relying only on
manifest-example lookup.

Deliverables:

- `UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED` proof-certificate steps use
  `predicate-result`;
- both command-buffer unsupported certificate steps name
  `stem_command_buffer_preserves_unsupported_completion`;
- proof-certificate text/JSON and aggregate project-status reports render the
  command-buffer unsupported certificate as two predicate-result steps;
- the command-buffer unsupported claim note matches the current
  standard-signal-only boundary; and
- Universal Cell runtime behavior, transition claims, object-language schema,
  evidence bundles, source-status records, and status schema versions remain
  unchanged.

Status: accepted in
`docs/adr/0181-command-buffer-unsupported-predicate-result-certificates.md`.
Implemented in the proof-certificate manifest, focused proof/project-status
tests, and the command-buffer unsupported claim note.

## ADR-0182: Self Command-Buffer Write-Buffer Predicate Result Certificates

Goal: make the completed self-target command-buffer write-buffer append proof
certificate name the predicate it evaluates instead of relying only on
manifest-example lookup.

Deliverables:

- `UC-STEM-COMMAND-BUFFER-SELF-WRITE-BUFFER-APPENDED` proof-certificate steps
  use `predicate-result`;
- all three self command-buffer write-buffer certificate steps name
  `stem_command_buffer_executes_self_write_buffer`;
- proof-certificate text/JSON and aggregate project-status reports render the
  self command-buffer write-buffer certificate as three predicate-result
  steps; and
- Universal Cell runtime behavior, transition claims, object-language schema,
  evidence bundles, source-status records, and status schema versions remain
  unchanged.

Status: accepted in
`docs/adr/0182-self-command-buffer-write-buffer-predicate-result-certificates.md`.
Implemented in the proof-certificate manifest and focused proof/project-status
tests.

## ADR-0183: Neighbor Command-Buffer Delivery Predicate Result Certificates

Goal: make the completed neighbor-target command-buffer delivery proof
certificate name the predicate it evaluates instead of relying only on
manifest-example lookup.

Deliverables:

- `UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED` proof-certificate steps use
  `predicate-result`;
- both neighbor command-buffer delivery certificate steps name
  `stem_command_buffer_delivers_neighbor_command`;
- proof-certificate text/JSON and aggregate project-status reports render the
  neighbor command-buffer delivery certificate as two predicate-result steps;
  and
- Universal Cell runtime behavior, transition claims, object-language schema,
  evidence bundles, source-status records, and status schema versions remain
  unchanged.

Status: accepted in
`docs/adr/0183-neighbor-command-buffer-delivery-predicate-result-certificates.md`.
Implemented in the proof-certificate manifest, focused proof/project-status
tests, and the neighbor command-buffer delivery claim note.

## ADR-0184: Recipient Init Command-Message Predicate Result Certificates

Goal: make the recipient init command-message proof certificate name the
predicate it evaluates instead of relying only on manifest-example lookup.

Deliverables:

- `UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED` proof-certificate steps use
  `predicate-result`;
- all three recipient init command-message certificate steps name
  `recipient_init_command_message_processed`;
- proof-certificate text/JSON and aggregate project-status reports render the
  recipient init command-message certificate as three predicate-result steps;
  and
- Universal Cell runtime behavior, transition claims, object-language schema,
  evidence bundles, source-status records, and status schema versions remain
  unchanged.

Status: accepted in
`docs/adr/0184-recipient-init-command-message-predicate-result-certificates.md`.
Implemented in the proof-certificate manifest, focused proof/project-status
tests, and the recipient init command-message claim note.

## ADR-0185: Recipient Write-Buffer Command-Message Predicate Result Certificates

Goal: make the recipient write-buffer command-message proof certificate name the
predicate it evaluates instead of relying only on manifest-example lookup.

Deliverables:

- `UC-RECIPIENT-WRITE-BUFFER-COMMAND-MESSAGE-APPENDED` proof-certificate steps
  use `predicate-result`;
- all three recipient write-buffer command-message certificate steps name
  `recipient_write_buffer_command_message_appends_literal`;
- proof-certificate text/JSON and aggregate project-status reports render the
  recipient write-buffer command-message certificate as three predicate-result
  steps; and
- Universal Cell runtime behavior, transition claims, object-language schema,
  evidence bundles, source-status records, and status schema versions remain
  unchanged.

Status: accepted in
`docs/adr/0185-recipient-write-buffer-command-message-predicate-result-certificates.md`.
Implemented in the proof-certificate manifest, focused proof/project-status
tests, and the recipient write-buffer command evidence-bundle note.

## ADR-0186: Recipient Non-Init Command-Message Predicate Result Certificates

Goal: make the recipient non-init command-message rejection proof certificate
name the predicate it evaluates instead of relying only on manifest-example
lookup.

Deliverables:

- `UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED` proof-certificate steps use
  `predicate-result`;
- all four recipient non-init command-message certificate steps name
  `recipient_non_init_command_message_rejected`;
- proof-certificate text/JSON and aggregate project-status reports render the
  recipient non-init command-message certificate as four predicate-result steps;
- the checked transition proof-certificate manifest no longer contains
  `manifest-example` rules; and
- Universal Cell runtime behavior, transition claims, object-language schema,
  evidence bundles, source-status records, and status schema versions remain
  unchanged.

Status: accepted in
`docs/adr/0186-recipient-non-init-command-message-predicate-result-certificates.md`.
Implemented in the proof-certificate manifest, focused proof/project-status
tests, and the recipient non-init rejection claim/evidence notes.

## ADR-0187: Chain Predicate Result Certificates

Goal: extend predicate-named proof steps from base transition claims to the
transition-chain claim surface.

Deliverables:

- chain proof-certificate verifier support for `predicate-result` steps;
- chain object-language support for the `predicate-result` proof-object rule;
- `UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED` proof-certificate steps use
  `predicate-result` and name `neighbor_delivery_consumed_by_recipient`;
- `UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-REJECTED` proof-certificate steps use
  `predicate-result` and name `neighbor_delivery_rejected_by_recipient`;
- verifier rejection tests for missing or mismatched chain predicate metadata;
- the checked chain proof-certificate manifest no longer contains
  `manifest-example` rules; and
- Universal Cell runtime behavior, transition-chain claims, evidence bundles,
  source-status records, and status schema versions remain unchanged.

Status: accepted in `docs/adr/0187-chain-predicate-result-certificates.md`.
Implemented in the chain proof-certificate verifier, chain object language,
chain proof-certificate manifest, focused chain/project-status tests, and chain
claim/language summary docs.

## ADR-0188: Proof Rule Status Summary

Goal: make the checked proof-certificate rule mix visible from aggregate
project status.

Deliverables:

- `proof_rule_audit` in project-status JSON;
- transition, chain, and combined proof-step counts by rule;
- default status text rendering of the accepted combined audit as
  `Proof rule audit: predicate-result=49, manifest-example=0`;
- source-specific rejected audit summaries when certificate manifests cannot be
  loaded; and
- no changes to transition behavior, claims, proof certificates, evidence
  bundles, source-status records, or blocked frontier semantics.

Status: accepted in `docs/adr/0188-proof-rule-status-summary.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py` and summary docs in
`docs/project-status-report.md`.

## ADR-0189: Compact Project Status Summary

Goal: add a short operator-facing status digest without weakening the full
audit report.

Deliverables:

- `format_project_status_summary` over the existing project-status payload;
- `python -m autarkic_systems.project_status --format summary`;
- six-line summary output covering accepted state, evidence counts, claim
  counts, proof-rule audit, blocked commands, and safe next slice;
- summary output omits full evidence bundle listings and source-status boundary
  paragraphs; and
- project-status JSON schema and validation semantics remain unchanged.

Status: accepted in `docs/adr/0189-compact-project-status-summary.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py` and summary docs in
`docs/project-status-report.md`.

## ADR-0190: GitHub Submission Status

Goal: make the current GitHub submission evidence visible from a local command.

Deliverables:

- `autarkic_systems/github_submission.py`;
- `python -m autarkic_systems.github_submission` text and JSON reports;
- current branch, `HEAD`, origin/fork remote URL, fork-main match, origin-main
  divergence, and upstream tracking issue fields;
- deterministic fake-runner tests for the git command surface; and
- no GitHub API dependency.

Status: accepted in `docs/adr/0190-github-submission-status.md`.
Implemented in `autarkic_systems/github_submission.py`, with tests in
`tests/test_github_submission_status.py`.

## ADR-0191: End-Of-Month Handoff Status

Goal: provide one local command that combines project health and GitHub
submission evidence for the active end-of-month objective.

Deliverables:

- `autarkic_systems/handoff.py`;
- `python -m autarkic_systems.handoff` text and JSON reports;
- accepted handoff state only when project status is accepted and current
  `HEAD` is visible on fork `main`;
- injected project/submission builders for deterministic tests; and
- no new validation authority beyond existing project-status and
  GitHub-submission reports.

Status: accepted in `docs/adr/0191-end-of-month-handoff-status.md`.
Implemented in `autarkic_systems/handoff.py`, with tests in
`tests/test_handoff_status.py`.

## ADR-0192: Submission Ref Freshness

Goal: make the local freshness of fork submission evidence explicit.

Deliverables:

- `fork/main` remote-tracking reflog timestamp in GitHub submission status;
- JSON `fork_main.remote_ref_freshness` with state, checked ref, update time,
  age, and max age;
- text line rendering fork-main freshness;
- deterministic clock and freshness-window test seams; and
- handoff JSON/text inherits the same submission freshness field.

Status: accepted in `docs/adr/0192-submission-ref-freshness.md`.
Implemented in `autarkic_systems/github_submission.py`, with tests in
`tests/test_github_submission_status.py` and `tests/test_handoff_status.py`.

## ADR-0193: Refresh Remotes Before Handoff

Goal: let operators explicitly refresh inspected remote-tracking refs before
submission or handoff status is rendered.

Deliverables:

- `--refresh-remotes` for `python -m autarkic_systems.github_submission`;
- `--refresh-remotes` for `python -m autarkic_systems.handoff`;
- explicit fetches from fork `main` to `refs/remotes/fork/main` and origin
  `main` to `refs/remotes/origin/main`;
- text and JSON refresh-result reporting; and
- requested refresh failures reject submission and handoff status.

Status: accepted in `docs/adr/0193-refresh-remotes-before-handoff.md`.
Implemented in `autarkic_systems/github_submission.py` and
`autarkic_systems/handoff.py`, with tests in
`tests/test_github_submission_status.py` and `tests/test_handoff_status.py`.

## ADR-0194: Two-Cell Network Witness

Goal: make the existing neighbor-delivery chain inspectable as a bounded
network-shaped execution witness.

Deliverables:

- `autarkic_systems/network_witness.py`;
- structured witness payload with sender before/after state, recipient
  before/before-step/after state, delivered tuple, and ordered events;
- `python -m autarkic_systems.network_witness` text and JSON output over named
  fixture cases;
- consumed init delivery, consumed write-buffer delivery, rejected
  standard-signal delivery, blocked recipient, and sender-not-delivered tests;
  and
- no scheduler, timing, topology, output-clearing, or new command semantics.

Status: accepted in `docs/adr/0194-two-cell-network-witness.md`. Implemented
in `autarkic_systems/network_witness.py`, with tests in
`tests/test_two_cell_network_witness.py` and operator notes in
`docs/two-cell-network-witness.md`.

## ADR-0195: Complete Network Witness Fixture Surface

Goal: expose every checked two-cell witness shape through the witness CLI.

Deliverables:

- `recipient-not-ready` CLI fixture case;
- `sender-not-delivered` CLI fixture case;
- JSON/text tests for those failure-shape fixtures;
- operator note coverage for all five witness fixture cases; and
- no new transition behavior.

Status: accepted in
`docs/adr/0195-complete-network-witness-fixtures.md`. Implemented in
`autarkic_systems/network_witness.py`, with tests in
`tests/test_two_cell_network_witness.py`.

## ADR-0196: Post-Handoff Signal Witness

Goal: show one durable recipient behavior after an accepted init-family
neighbor-delivery handoff.

Deliverables:

- `autarkic_systems/network_sequence.py`;
- post-handoff witness payload over delivery witness plus one recipient
  follow-up input;
- text and JSON CLI output for accepted and rejected fixture cases;
- tests for routed follow-up, non-init handoff rejection, and malformed
  follow-up rejection; and
- no scheduler, timing, topology, output-clearing, or new command semantics.

Status: accepted in `docs/adr/0196-post-handoff-signal-witness.md`.
Implemented in `autarkic_systems/network_sequence.py`, with tests in
`tests/test_post_handoff_signal_witness.py` and operator notes in
`docs/post-handoff-signal-witness.md`.

## ADR-0197: Post-Handoff Sequence Claim

Goal: name and check the ADR-0196 post-handoff signal witness as a claim.

Deliverables:

- `autarkic_systems/network_sequence_predicates.py`;
- `autarkic_systems/network_sequence_claims.py`;
- `claims/network_sequence_claims.json`;
- `claims/network_sequence_proof_certificates.json`;
- text and JSON CLI validation; and
- positive/negative example and incomplete-certificate tests.

Status: accepted in `docs/adr/0197-post-handoff-sequence-claim.md`.
Implemented in `autarkic_systems/network_sequence_predicates.py` and
`autarkic_systems/network_sequence_claims.py`, with tests in
`tests/test_network_sequence_claims.py` and operator notes in
`docs/network-sequence-claims.md`.

## ADR-0198: Network Sequence Evidence Bundle

Goal: make the post-handoff sequence claim discoverable as a checked evidence
bundle.

Deliverables:

- `autarkic_systems/network_sequence_evidence_bundle.py`;
- `evidence/sequences/post_handoff_signal_bundle.json`;
- `evidence/sequences/manifest.json`;
- text and JSON CLI validation for one bundle or the registry;
- checks for sequence claim, proof certificate, executable witness, underlying
  chain bundle, source-status files, and boundary text; and
- no scheduler, timing, topology, output-clearing, project-status, or new
  command semantics.

Status: accepted in `docs/adr/0198-network-sequence-evidence-bundle.md`.
Implemented in `autarkic_systems/network_sequence_evidence_bundle.py`, with
tests in `tests/test_network_sequence_evidence_bundle.py` and operator notes in
`docs/network-sequence-evidence-bundles.md`.

## ADR-0199: Project Status Sequence Evidence

Goal: make aggregate project status fail closed over the checked
network-sequence evidence registry.

Deliverables:

- `sequence_evidence` in project-status JSON;
- aggregate acceptance that includes the network-sequence registry result;
- default text and compact summary output naming the sequence evidence count;
- `--sequence-registry` override for alternate registry paths;
- structured `registry-file` / `registry-json` failures for sequence registry
  problems; and
- project-status schema version `17`.

Status: accepted in `docs/adr/0199-project-status-sequence-evidence.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py`.

## ADR-0200: Project Status Sequence Claims

Goal: make aggregate project status account for the network-sequence
claim/proof surface, not only the sequence evidence registry.

Deliverables:

- `sequence_claims` in project-status JSON;
- aggregate acceptance that includes network-sequence claim validation;
- default text and compact summary output naming the sequence claim count;
- proof-rule audit counts that include sequence proof certificates;
- `--sequence-claims` and `--sequence-certificates` overrides; and
- project-status schema version `18`.

Status: accepted in `docs/adr/0200-project-status-sequence-claims.md`.
Implemented in `autarkic_systems/project_status.py`, with tests in
`tests/test_project_status_report.py` and `tests/test_handoff_status.py`.

## ADR-0201: Network Sequence Object Language

Goal: make the network-sequence claim syntax explicit instead of leaving it
implicit in Python and JSON conventions.

Deliverables:

- `language/network_sequence_claim_language.json`;
- `autarkic_systems/network_sequence_object_language.py`;
- text and JSON CLI validation;
- checks for required syntax classes, term vocabulary, predicate symbols,
  sentence shape, proof-object rules, and manifest pointers;
- claim/proof surface validation against the language; and
- no new runtime behavior, proof rules, evidence bundles, project-status
  fields, scheduler, topology, timing, or command semantics.

Status: accepted in `docs/adr/0201-network-sequence-object-language.md`.
Implemented in `autarkic_systems/network_sequence_object_language.py`, with
tests in `tests/test_network_sequence_object_language.py` and operator notes in
`docs/network-sequence-claim-language.md`.
