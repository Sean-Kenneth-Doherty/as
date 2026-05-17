# ADR-0065: Recipient Init Transition Evidence Bundle

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0049 through ADR-0052 created a complete narrow evidence path for one
recipient init-family command-message transition:

- executable behavior in `autarkic_systems/universal_cell.py`;
- a named transition claim and proof certificate;
- a schematic trace; and
- a checked SVG render.

Those artifacts are individually tested, but future readers still have to
discover the path by following several files. AS needs a small integrated
bundle format that proves one transition can be inspected end to end without
widening the transition semantics.

## Decision

Add a transition evidence bundle for the recipient `wire-r-init` command-message
case.

The bundle will point to:

- `UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED`;
- the positive manifest example `fixed upstream wire right init processed`;
- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/recipient_init_command_message_trace.json`;
- `schematics/recipient_init_command_message_trace.svg`;
- `sources/prc_hardware_witness_map.json`; and
- the source-status records that bound recipient command-message execution.

Add a loader and validator that checks the referenced claim, certificate,
schematic trace, SVG render, and source-status files as one bundle.

This ADR does not change Universal Cell runtime behavior and does not add
non-init recipient command execution.

## Success Criteria

- Red tests fail before implementation because the bundle loader or artifact is
  absent.
- The bundle records the claim ID, predicate, positive example, transition
  function, status, trace path, SVG path, proof certificate path, hardware
  witness map, and source-status paths.
- Validation proves the claim example exists and evaluates as expected.
- Validation proves the proof certificate for the claim is accepted.
- Validation proves the schematic trace executes and validates against the PRC
  hardware witness map.
- Validation proves the committed SVG matches the renderer for the schematic
  trace.
- Validation rejects drifted claim IDs and missing SVG paths.
- Runtime behavior remains unchanged.

## Consequences

AS gains its first first-class evidence bundle: a single artifact that ties one
runtime transition to claim, proof, schematic, render, and source-boundary
evidence. This should be the preferred shape for later “show me the evidence”
surfaces, without pretending that still-blocked command semantics are solved.

## Test Plan

- Red: `python -m unittest tests.test_recipient_init_transition_evidence_bundle`
  fails before the loader and artifact exist.
- Green: the same focused test passes after adding the bundle, loader, and
  validator.
- Regression: run the adjacent recipient claim/trace/SVG tests and the full
  default suite before commit.

## After Action Report

Implemented in `evidence/recipient_init_command_message_bundle.json` and
`autarkic_systems/evidence_bundle.py`.

The red run failed because `autarkic_systems.evidence_bundle` was absent. The
green implementation adds a bundle for the positive fixed-upstream
`wire-r-init` example under
`UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED`.

The validator loads the transition claim manifest, proof certificate manifest,
recipient init schematic trace, committed recipient init SVG, PRC hardware
witness map, and source-status records. It verifies that the claim example
evaluates true, the proof certificate is accepted, the trace executes and
matches the claim example, the trace validates against the hardware witness
map, the SVG matches renderer output, and the boundary source-status files
remain present and parseable.

Runtime behavior remains unchanged. Non-init recipient command execution,
`standard-signal` command-token execution, and write-buffer command-token
execution remain blocked by existing source-status records.
