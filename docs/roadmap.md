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
