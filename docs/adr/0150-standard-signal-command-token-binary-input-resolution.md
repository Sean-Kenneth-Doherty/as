# ADR-0150: Standard-Signal Command Token Binary-Input Resolution

Date: 2026-05-18

## Status

Accepted.

## Context

After ADR-0148, the standard-signal source-status frontier still has two live
questions:

- whether a `standard-signal` command token should replay ordinary binary-input
  standard-signal behavior; and
- what self-mailbox and self-target command-buffer surfaces should do.

The first question is a source-equivalence question, not a runtime behavior
choice. AS already implements ordinary binary-input standard-signal behavior.
The command-token path is different: the formal model separately names
ordinary standard-signal processing and the command-table `standard-signal`
entry, while the reviewed legacy witnesses exclude `standard-signal` from
special-message dispatch and treat ordinary standard input separately.

## Decision

Move `command-token-vs-binary-input` from unresolved to resolved in
`sources/standard_signal_command_semantics_status.json`.

The resolved decision is:

`do-not-replay-ordinary-binary-input-standard-signal`

This ADR does not implement `standard-signal` command-token execution. It does
not decide whether self-mailbox or self-target command-buffer
`standard-signal` command tokens should be preserved, cleared/no-oped, or
executed through some other rule.

## Consequences

The standard-signal source-status frontier should now have only one unresolved
question: `self-target-surface`.

Future standard-signal command-token work should not argue that command tokens
automatically replay ordinary binary-input routing or high-rail accumulation.
It must choose an explicit self-target command-token boundary.

## Verification Plan

- Red: update standard-signal, project-status, and source-status frontier
  tests to expect `command-token-vs-binary-input` as resolved before changing
  the source artifact.
- Green: update the standard-signal source-status artifact and docs.
- Regression: run focused tests, both status CLIs in JSON mode, `py_compile`,
  `git diff --check`, and the full unittest suite.

## After Action Report

Implemented in `sources/standard_signal_command_semantics_status.json` and
the standard-signal/frontier docs. The standard-signal source-status frontier
now has only `self-target-surface` in `required_resolution_questions`, while
`command-token-vs-binary-input` appears in `resolved_resolution_questions`.

The red focused run executed 86 standard-signal, project-status, and
source-status frontier tests and failed because
`command-token-vs-binary-input` was still unresolved and absent from the
resolved question list.

The green focused run passed 86 tests. Source-status JSON was accepted at
`schema_version: 1` and showed only `self-target-surface` as unresolved for
standard-signal. Project-status JSON remained accepted at `schema_version: 14`,
`py_compile` and `git diff --check` passed, and `python -m unittest discover`
passed 659 tests.
