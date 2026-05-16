# ADR-0002: Autarkic Formal System Requirements

Date: 2026-05-16

Status: Accepted

## Context

The AS prelude says Autarkic Systems subsumes Autarkic Formal Systems, which in
turn is a superset of PRC and SJAS. The public AFS repository, however, is only
a placeholder README at the reviewed snapshot. Without a working definition of
AFS, future implementation could drift into unrelated theorem proving,
hardware simulation, or general AI prose.

The subordinate review shows a clear pressure:

- PRC supplies the embodied substrate problem: a computing system should expose
  logic, routing, memory, power, and reconfiguration rather than hiding them
  behind opaque hardware authority.
- SJAS supplies the formal-confidence problem: a reasoning system may gain
  carefully scoped self-confidence by controlling its expressivity and proof
  apparatus.
- Recent SJAS notes also point to Proflog-adjacent executable work, but the
  public `jpt4/proflog` main branch does not contain the logged ADR-006x
  frontier and did not run under the available Guile interpreter.

## Decision

Define an Autarkic Formal System as a formal system package that connects:

1. an explicit object language;
2. a documented proof or refutation apparatus;
3. inspectable encodings for syntax, proofs, and substitution;
4. an explicit substrate transition model;
5. executable artifacts that can check selected claims across these layers.

Add:

- `docs/glossary.md` for project vocabulary;
- `docs/afs-requirements.md` for the requirement matrix, gap register, and
  first executable probe recommendation.

## Success Criteria

- AFS has a concrete working definition in this repository.
- Requirements cover both SJAS-style formal confidence and PRC-style substrate
  visibility.
- Known gaps are recorded instead of hidden.
- The next code-bearing ADR has a recommended target that can be tested.

## Consequences

- AS now has a standard for rejecting partial artifacts: no single theorem
  prover, hardware simulator, or essay satisfies AFS unless it connects to the
  other required layers.
- The next implementation should be deliberately small: a substrate/formal
  bridge around one Universal Cell transition invariant.
- ADR-0003 remains necessary because the project still lacks a machine-readable
  manifest of source snapshots and adjacent repositories.

## After Action Report

The requirement definition was added after:

- re-reading `AGENTS.md`;
- reviewing the local `afs`, `prc`, and `sjas` snapshots;
- listing public `jpt4` repositories and identifying `proflog` as an adjacent
  candidate;
- cloning `jpt4/proflog` at `77af848`;
- attempting `guile proflog.scm`, which failed with `Unbound variable: even`.

The ADR met its documentation success criteria. It did not add executable AS
code, so the test-first code requirement remains pending for the first
code-bearing ADR.
