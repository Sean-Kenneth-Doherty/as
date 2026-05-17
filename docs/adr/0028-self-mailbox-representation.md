# ADR-0028: Self Mailbox Representation

Date: 2026-05-17

Status: Accepted

## Context

ADR-0027 identified self mailbox state as the first blocker for source-backed
stem command execution. The PRC formal model's process-buffer path routes
self-target messages through a self mailbox before special-message processing.
AS currently records automail, control, and buffer state, but it has no field
for that self mailbox.

Adding the field is representation work, not execution work. It should preserve
existing transition behavior while making future self-target command execution
possible to specify and test.

## Decision

Add an explicit `self_mailbox` field to `Cell`:

- the value is `_` when empty, or one of the eight ADR-0026 command IDs;
- loaders and validators must preserve it through claim manifests,
  schematic traces, and the transition-claim object language;
- current transitions may clear it only when the existing transition already
  resets the cell state;
- no command-buffer execution, neighbor delivery, or self special-message
  execution is added in this ADR.

## Success Criteria

- Red tests fail before implementation because `Cell` has no `self_mailbox`
  field and language/trace vocabularies do not name it.
- `Cell` defaults to an empty self mailbox and rejects unknown mailbox values.
- Existing reset-style transitions clear the self mailbox.
- The claim manifest, object language, and schematic trace surfaces expose the
  new field.
- Existing behavior tests continue to pass.

## Consequences

- Future self-target execution can target an explicit state field instead of
  overloading `automail`, `input`, or `output`.
- Existing checked schematic traces must include the field to keep "all Cell
  fields" validation honest.
- `standard-signal` remains represented but not interpreted as a command.

## After Action Report

Red step:

- `python -m unittest tests.test_self_mailbox_representation` failed because
  `Cell` had no `self_mailbox` attribute, `Cell.__init__` rejected the
  `self_mailbox` keyword, and the object-language and schematic-trace
  vocabularies did not name the field.

Green step:

- Added `CommandMessage` and `self_mailbox` support to
  `autarkic_systems/universal_cell.py`.
- Updated claim manifest parsing, object-language validation, schematic trace
  mapping, `language/transition_claim_language.json`, and checked schematic
  trace JSON artifacts.
- `python -m unittest tests.test_self_mailbox_representation` passed 7 tests.

Full verification:

- `python -m unittest discover` passed 143 tests.
- `python -m unittest tests.test_object_language tests.test_claim_manifest
  tests.test_single_node_schematic_trace tests.test_processor_memory_toggle_trace
  tests.test_stem_automail_reconfiguration_trace
  tests.test_stem_buffer_accumulation_trace tests.test_single_node_schematic_svg
  tests.test_processor_memory_toggle_svg tests.test_stem_automail_svg
  tests.test_stem_buffer_svg` passed 69 tests.
- `python -m py_compile autarkic_systems/universal_cell.py
  autarkic_systems/claim_manifest.py autarkic_systems/object_language.py
  autarkic_systems/schematic_trace.py tests/test_self_mailbox_representation.py`
  passed.
- `jq -e .` passed for the transition-claim language JSON and all four checked
  schematic trace JSON artifacts.
- `git diff --check` passed.

Coverage limits:

- This is representation only.
- It does not process `self_mailbox`.
- It does not deliver command messages to neighbor outputs.
- It does not interpret `standard-signal` as a command.
