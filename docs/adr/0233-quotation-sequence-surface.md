# ADR-0233: Quotation Sequence Surface

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0232 added token-level numeral quotation: individual formal code tokens
can now be represented as unary successor numerals. The fixed-point target
still names sequence-level quotation construction as open because a tuple of
quoted token numerals is not yet a named sequence object and still is not a
formal quotation term.

The next useful step is to add a checked token-numeral sequence surface. This
keeps progressing toward quotation while preserving the boundary: a checked
sequence object is still not a term inside the arithmetic object language and
does not prove a diagonal lemma.

## Decision

Add `language/formal_quotation_sequence_examples.json` and
`autarkic_systems.formal_quotation_sequence`. The surface will quote a
non-empty tuple of formal code tokens as a structured
`token-numeral-sequence` object whose items are the unary numerals from
ADR-0232.

The fixed-point target will be narrowed again: it will reference the sequence
quotation examples and replace `quotation-sequence-construction` with the
remaining `quotation-term-construction` obligation.

This does not implement pair/list coding in the arithmetic language, a formal
term for complete formula codes, a diagonal lemma, a fixed-point equation
proof, arithmetized proof predicates, self-consistency, runtime behavior,
command semantics, evidence bundles, or GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because the formal-quotation-sequence
  module and manifest do not exist.
- The sequence manifest references the token quotation examples and fixed-point
  target manifest.
- The validator quotes the current fixed-point target expected instance code as
  a `token-numeral-sequence` and checks token count plus endpoint depths.
- The validator rejects empty token sequences, endpoint-depth mismatches, and
  non-`token-numeral-sequence` status/kind mismatches.
- Text and JSON CLI modes expose the same validation surface.
- The fixed-point target points at the sequence quotation examples and remains
  blocked on full quotation-term construction plus diagonal/fixed-point proof
  work.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_formal_quotation_sequence
  tests.test_fixed_point_target tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live formal-quotation-sequence text/JSON, live fixed-point,
  live project-status summary, live handoff with `--refresh-remotes`,
  compileall, JSON checks, `git diff --check`, and the full default suite.

## After Action Report

Implemented. The red focused run failed before implementation because
`autarkic_systems.formal_quotation_sequence` and
`language/formal_quotation_sequence_examples.json` were absent, and the
fixed-point manifest had no `quotation_sequence_examples_path` field.

The implementation added `language/formal_quotation_sequence_examples.json`
and `autarkic_systems/formal_quotation_sequence.py`, with text/JSON CLI
validation and negative checks for empty token sequences, endpoint-depth
mismatches, and non-`token-numeral-sequence` kinds. The fixed-point target now
references the quotation sequence examples and names
`quotation-term-construction` as the remaining quotation obligation.

Focused green evidence:

```sh
python -m unittest tests.test_formal_quotation_sequence tests.test_fixed_point_target tests.test_project_status_report
# Ran 111 tests in 13.305s - OK
```

Live evidence:

```sh
python -m autarkic_systems.formal_quotation_sequence
# Formal quotation sequence: accepted; Example count: 2; Failed subjects: none
python -m autarkic_systems.fixed_point
# quotation_sequence_examples_path accepted; quotation_sequence dependency accepted
python -m autarkic_systems.formal_confidence --format json
# accepted true; failed_subjects []
python -m autarkic_systems.project_status --format summary
# Autarkic Systems summary: accepted; Formal confidence: 1 target; blocked=1
```

Regression evidence:

```sh
python -m compileall autarkic_systems tests
jq -e . language/formal_quotation_sequence_examples.json
jq -e . claims/fixed_point_targets.json
git diff --check
python -m unittest discover
# Ran 1027 tests in 21.850s - OK
```

The remaining boundary is still substantial: AS has a checked sequence object
over quoted code tokens, but no arithmetic-language pair/list quotation term,
no diagonal lemma proof, no fixed-point equation proof, no arithmetized proof
predicate, and no self-consistency theorem.
