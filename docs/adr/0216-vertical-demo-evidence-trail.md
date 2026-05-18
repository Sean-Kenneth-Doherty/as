# ADR-0216: Vertical Demo Evidence Trail

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0214 added a top-level vertical demo digest, and ADR-0215 carried that
digest into the end-of-month handoff report. The digest now names the current
post-handoff signal-routing demonstration and the checked sequence evidence
bundle, but it does not expose the actual artifact trail a reader would follow
from the demo to the checked claim, proof, language, witness, trace, SVG,
underlying chain bundle, and source-status files.

The existing `autarkic_systems.network_sequence_demo` report already knows
that evidence trail and validates the same checked bundle. The top-level
vertical demo should reuse that surface instead of rebuilding path knowledge.

## Decision

Extend `autarkic_systems.vertical_demo` to include a structured evidence trail
derived from `build_network_sequence_demo_report`.

The digest will include:

- `evidence_trail`, a role-to-path list with existence flags;
- `missing_evidence_paths`, copied from the network-sequence demo report;
- `validation_subjects`, the checked validation subjects for the sequence
  demo path; and
- text output that lists the evidence trail under an `Evidence trail:` section.

Vertical demo acceptance will require both the aggregate project status and the
network-sequence demo report to be accepted.

This does not change runtime behavior, claims, proof rules, validation
authority, project-status schema, source-status decisions, registry schemas,
trace/SVG rendering, scheduler, topology, timing, or command semantics.

## Success Criteria

- Red tests fail before implementation because vertical demo JSON/text lacks
  `evidence_trail`, `missing_evidence_paths`, and `validation_subjects`.
- JSON output includes the sequence claim/proof/language/witness/trace/SVG,
  underlying chain bundle, and source-status evidence trail.
- Text output includes an `Evidence trail:` section with those paths.
- Accepted-path `missing_evidence_paths` is empty.
- Handoff output continues to carry the expanded vertical demo digest.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_vertical_demo_digest`.
- Green: the same focused suite passes after implementation.
- Regression: run adjacent vertical-demo, network-sequence demo, and handoff
  tests, `python -m autarkic_systems.vertical_demo`,
  `python -m autarkic_systems.handoff --refresh-remotes`,
  `python -m compileall -q autarkic_systems tests`, `git diff --check`, and
  the full default suite.

## After Action Report

Implemented in `autarkic_systems/vertical_demo.py`, with focused coverage in
`tests/test_vertical_demo_digest.py` and inherited handoff fixture coverage in
`tests/test_handoff_status.py`.

The red focused run failed as intended because the vertical demo digest lacked
`evidence_trail`, `missing_evidence_paths`, and `validation_subjects`, and text
output lacked an `Evidence trail:` section.

The implementation reuses `build_network_sequence_demo_report` to populate the
top-level vertical demo trail, requires both aggregate project status and the
network-sequence demo report to be accepted, and renders the trail in text
output. The trail now includes the checked sequence claim/proof/language
artifacts, witness implementation, trace, SVG, underlying chain bundle, and
source-status records.

Focused vertical-demo tests passed 4 tests. Adjacent handoff, vertical-demo,
and network-sequence demo tests passed 25 tests. Live vertical-demo and handoff
commands reported accepted status, no missing evidence paths, and the expanded
evidence trail. `compileall`, `git diff --check`, and the full default suite
passed; the full suite ran 907 tests.
