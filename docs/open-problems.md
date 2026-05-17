# Open Problems

Status: first ranking, 2026-05-17.

These are project problems, not generic research wishes. Each one should be
able to generate one or more ADRs.

## P1: Formalize The Current Transition Predicates

Question: What is the smallest object-language vocabulary that can state the
four predicates already implemented over Universal Cell transition results?

Why it matters: This is the shortest bridge from executable substrate behavior
to formal claims.

Status: started by ADR-0007. `claims/transition_claims.json` names the current
predicate claims and executable examples. Remaining work is to add proof objects
or proof-apparatus clauses behind those claim IDs.

## P2: Expand From Fixed Roles To Stem/Reconfiguration

Question: Which stem-cell transition subset is small enough to test without
pretending to reimplement all of PRC?

Why it matters: Reconfiguration is central to PRC and AS, while the current
probe only covers fixed wire/proc behavior.

Status: started by ADR-0008. `step_stem_cell` now covers automail
reconfiguration commands `wr`, `wl`, `pr`, and `pl`. Full stem input
classification and buffer processing remain open. ADR-0009 added the
corresponding `automail_reconfigures_stem` predicate and manifest claim.

## P3: Choose The First Proof Apparatus

Question: Should AS start with a tiny local tableaux checker, a repaired public
Proflog, or a reference to another transparent tableaux implementation?

Why it matters: SJAS requirements depend on proof apparatus details; AS cannot
claim formal self-confidence without one.

Likely next artifact: an ADR comparing Fitting/Proflog, LeanTAP, and a minimal
local checker against transparency, testability, and Willard compatibility.

## P4: Define The First Object Language

Question: What syntax is sufficient for the first AS claims: transition
predicates only, IS(A)-style arithmetic fragments, or both?

Why it matters: AFS-R2 requires explicit syntax classes for terms, formulae,
sentences, proof objects, and substrate claims.

Likely next artifact: a parser/validator test suite for a tiny claim language.

## P5: Annotate Core Willard Sources At Definition Granularity

Question: Which definitions and theorem statements from Willard 2001, 2011,
2016, and 2020 are actually needed for the first AS formal-confidence claim?

Why it matters: Current SJAS evidence is strong at the repository level, but AS
needs exact theorem/definition anchors before it can make non-hand-wavy claims.

Likely next artifact: `docs/willard-definition-map.md` with local witness paths,
definition IDs, and AS relevance.

## P6: Recover Or Replace The Active Proflog Frontier

Question: Where is the Proflog ADR-006x work described in SJAS logs, and should
AS depend on it?

Why it matters: Public Proflog `main` does not match the active SJAS log and
does not run under Guile in this environment.

Likely next artifact: a source-status note or issue draft documenting the gap,
plus a decision on whether to repair, replace, or ignore public Proflog.

## P7: Hardware/Schematic Evidence Path

Question: What is the smallest schematic or simulation artifact that honors
PRC's physical implementation claims without requiring full hardware design?

Why it matters: The AS prelude explicitly includes schematics and hardware
simulation as lower-bound project content.

Likely next artifact: a PRC hardware witness map around RLEM, GELC, circulator,
RALA, and lattice geometry sources.
