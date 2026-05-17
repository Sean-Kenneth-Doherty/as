# Willard Definition Map

Status: first definition-granularity map, 2026-05-17.

This document summarizes the structured map in
`sources/willard_definition_map.json`. The map exists because AS cannot make an
honest formal-confidence claim from a general phrase like "Willard-style
self-justification". It must identify which definitions, constructions, theorem
statements, and boundary results later ADRs are preserving.

## How To Use This Map

- Use anchor IDs when a future ADR depends on a Willard definition or theorem.
- Treat each anchor as a constraint, not as implemented AS behavior.
- Before adding an SJAS-level proof object, identify which anchor supplies its
  language, deduction method, proof-code encoding, self-reference clause, and
  consistency notion.
- Keep AS transition-claim certificates separate from Willard self-consistency
  claims until an ADR explicitly bridges them.

## Core Anchors

| Anchor | Source locus | AS role |
| --- | --- | --- |
| `W2001-D1.1-PRENEX-STAR` | Willard 2001, Definition 1.1 | Prenex* and bounded-quantifier notation for any later arithmetic object language. |
| `W2001-D1.2-TANGIBILITY` | Willard 2001, Definition 1.2 and Tangibility Reflection Principle | Tangibility restriction for scoped reflection and self-confidence claims. |
| `W2001-SEC2-IS-MAPPING` | Willard 2001, Section 2 | Four-part IS(A) construction: constants, grounding functions, imported Pi-1 theorems, and self-referential consistency axiom. |
| `W2001-T4.3-IS-CONSISTENCY-PRESERVING` | Willard 2001, Theorem 4.3 | Positive consistency-preservation target for IS(.), under regular consistency assumptions. |
| `W2011-D3.4-GENERIC-CONFIGURATION` | Willard 2011, Definition 3.4 | Five-part checklist for SJAS-relevant configurations: language, bounded formula class, base axioms, deduction method, and proof coding. |
| `W2011-D5.6-LEVEL-K-CONSISTENCY` | Willard 2011, Definition 5.6 | Level(k) consistency vocabulary. |
| `W2011-D5.7-SELFCONSK` | Willard 2011, Definition 5.7 | SelfCons_k self-reference shape for proof-code-aware consistency claims. |
| `W2011-T5.9-EA-STABLE-SELF-JUSTIFYING` | Willard 2011, Theorem 5.9 | Positive theorem shape: EA-stability supports B + SelfCons_1(B,d) self-justification. |
| `W2016-D3.2-HILBERT-STYLE` | Willard 2016, Definition 3.2 | Separates Hilbert-style deduction from tableaux and local proof-certificate checking. |
| `W2016-D3.4-SELF-JUSTIFYING-CONFIGURATION` | Willard 2016, Definition 3.4 | Pair-based self-justifying configuration: axiom basis plus deduction apparatus. |
| `W2016-D4.1-INDETERMINATE-FUNCTION` | Willard 2016, Definition 4.1 | Theta-style indeterminate function boundary; not ordinary total-function semantics. |
| `W2016-T6.7-IQFS-CONSISTENCY-PRESERVING` | Willard 2016, Theorem 6.7 | IQFS consistency preservation, explicitly dependent on Conjecture 6.6. |
| `W2020-D3.2-SELF-JUSTIFYING-GENAC` | Willard 2020, Definition 3.2 | General axiom-configuration framing for self-justification. |
| `W2020-D3.4-TYPE-NS-A-S-M` | Willard 2020, Definition 3.4 | Classifies systems by successor/addition/multiplication totality assumptions. |
| `W2020-SEC4-TAB-XTAB-TAB1` | Willard 2020, Section 4 | Distinguishes Tab, Xtab, Tab-1, and Level-1 appreciation of self-consistency. |
| `W2020-T4.4-T4.5-LEM-BOUNDARY` | Willard 2020, Theorems 4.4 and 4.5 | Boundary: excluded middle as a proof theorem vs. logical axiom changes consistency behavior. |

## Immediate AS Constraints

AFS-R2 cannot be satisfied by a generic parser. The Willard path requires
separate syntax classes for bounded formulae, Pi/Sigma levels, proof objects,
and encoded substitution/proof predicates.

AFS-R3 cannot be satisfied by saying "use a theorem prover". The deduction
apparatus matters: Hilbert-style, Tab, Xtab, Tab-1, resolution, local proof
certificates, and Proflog-style tableaux have different self-reference
consequences.

AFS-R4 must state the exact consistency level, axiom basis, deduction method,
and formal weakness being used. In this map, the strongest immediate candidates
are IS(A)-style consistency preservation, SelfCons_k over a generic
configuration, and IQFS under its conjecture-dependent boundary.

AFS-R5 is the next major implementation gap. The current AS proof certificates
do not yet encode Willard-style proof codes, substitution vocabulary, or
self-reference. The map says where those requirements come from, but does not
implement them.

## Verification

Run:

```sh
python -m unittest tests.test_willard_definition_map
```

The test checks that all four core Willard sources are represented, local
witness paths are pinned under the SJAS checkout, anchor IDs and source loci are
unique, and every anchor states AS relevance. The live PDF checkout was used
when this map was written, but the default fast suite does not require the
disposable `_upstream` cache to be present.

## Open Follow-Ups

- Extend the map to Willard 1993, 1997, 2005, 2014, and secondary literature
  only after the four core sources are used by a concrete ADR.
- Decide whether the next executable slice should encode bounded formula
  classes, proof-code substitution, or a smaller transition-witness proof rule.
- Resolve P6 before depending on Proflog: the public Proflog main branch still
  does not expose the ADR-006x work described by SJAS logs.
