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
