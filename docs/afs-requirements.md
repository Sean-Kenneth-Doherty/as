# Autarkic Formal System Requirements

Status: first working definition, 2026-05-16.

## Definition

An Autarkic Formal System is a formal system package for cognitive sovereignty.
It must make a scoped self-confidence claim inspectable across three levels:

1. the formal language and proof apparatus;
2. the executable implementation of that apparatus;
3. the substrate model on which the implementation is supposed to run or be
   simulated.

The project should reject any artifact that is strong in only one level while
hiding decisive authority in another. A theorem prover that trusts opaque
hardware without comment is not enough. A hardware simulator without a formal
self-confidence story is not enough. A philosophical definition without an
executable check path is not enough.

## Requirement Matrix

| ID | Requirement | Source pressure | Verification direction | Current status |
| --- | --- | --- | --- | --- |
| AFS-R1 | Maintain a pinned source manifest for AS, AFS, PRC, SJAS, and adjacent executable frontiers. | `AGENTS.md` requires literature assessment and organized existing material. SJAS logs point outside SJAS to Proflog-adjacent work. | Machine-readable manifest plus a human review table. Check remote commit IDs and local availability. | Partially satisfied by `docs/subordinate-review.md`; needs ADR-0003. |
| AFS-R2 | Define an object language with explicit syntax classes for terms, formulae, sentences, proof objects, and substrate claims. | SJAS Type NS and ISLA notes distinguish terms, formulae, and quantified sentences; PRC needs substrate predicates. | Parser/validator tests over accepted and rejected examples before implementation. | Started by ADR-0012 with `language/transition_claim_language.json` and object-language validation for current transition claims. ADR-0226 adds `language/formal_arithmetic_language.json`, the first checked syntax-only Type-NS arithmetic surface with `delta0`, `pi1`, and `sigma1`. ADR-0227 adds a first checked codebook over that syntax, ADR-0228 adds capture-avoiding substitution examples, ADR-0231 adds a checked fixed-point target template, ADR-0232 adds token-level unary quotation examples, ADR-0233 adds a checked token-numeral sequence surface, ADR-0234 adds checked quotation-term constructors, ADR-0241 adds the `substitution_code(t,u)` term needed to state diagonal-substitution routes, ADR-0242 checks the first diagonal seed and quoted seed instance over that term, and ADR-0244 checks the first meta-level graph witness for that seed. Full IS(A), parser, evaluator, fixed-point equations, and deduction syntax remain open. |
| AFS-R3 | Choose and document a proof/refutation apparatus before implementation. | SJAS emphasizes semantic tableaux/resolution tradeoffs; Proflog and Fitting-style tableaux are current candidates. | Red tests for known provable, refutable, and unknown cases; extended suite for slower tableaux examples. | Direction chosen by ADR-0010: start with a minimal AS-local proof-certificate checker, use LeanTAP as a transparency reference, and defer Proflog as a dependency until the active frontier is recovered or replaced. ADR-0230 selects the current AS-local `predicate-result` proof-certificate checker as a checked deduction-apparatus target for the executable substrate surfaces without claiming Hilbert, tableau, or self-justifying proof machinery. |
| AFS-R4 | State the exact self-confidence claim and its limits. | SJAS gains self-provability of consistency only under tuned expressivity; overclaiming would erase the point of the program. | A scoped theorem/claim document mapping assumptions, language restrictions, and non-goals. | Started by ADR-0224 with `claims/formal_confidence_targets.json`, which records the current target as blocked. ADR-0226 removes the arithmetic-syntax blocker by pointing the target at `language/formal_arithmetic_language.json`; ADR-0227 removes the first proof-code blocker by pointing it at `language/formal_codebook.json`; ADR-0228 removes the substitution blocker by pointing it at `language/formal_substitution_examples.json`; ADR-0229 removes the consistency-level selection blocker by pointing it at `claims/consistency_level_targets.json`; ADR-0239 adds the checked `pi1`/`sigma1` complement surface needed by that Level-1 target; ADR-0240 makes the consistency-level target a fail-closed formal-confidence dependency; ADR-0230 removes the deduction-apparatus selection blocker by pointing it at `claims/deduction_apparatus_targets.json`; ADR-0231 narrows self-reference to `claims/fixed_point_targets.json`; ADR-0233 narrows the fixed-point target from raw token sequences to a checked quotation sequence dependency; ADR-0234 narrows it again to a checked quotation-term dependency; ADR-0235 records the naive equation candidate as not fixed; ADR-0236 makes that candidate a fail-closed formal-confidence dependency; ADR-0237 records why the naive direct embedding route is length-obstructed; ADR-0238 makes that obstruction a fail-closed formal-confidence dependency; ADR-0243 makes the checked diagonal seed a fail-closed formal-confidence dependency; ADR-0244 records the next substitution graph witness without promoting it to the aggregate target. Fixed-point construction remains blocked. |
| AFS-R5 | Use inspectable arithmetized encodings for syntax and proofs where self-reference depends on coding. | SJAS `nachlass/LOG.md` rejects opaque hash labels for faithful Willard-style proof coding. | Round-trip tests for formula/proof code decode, substitution, complement relations, and malformed codes. | Started by ADR-0227 with `language/formal_codebook.json` and `autarkic_systems/formal_code.py`, which round-trip tagged natural-number prefix sequences for arithmetic nodes and placeholder proof-line shells. ADR-0228 adds capture-avoiding substitution examples over those nodes. ADR-0232 adds unary numeral quotation for individual code tokens. ADR-0233 wraps quoted token numerals into a checked sequence object. ADR-0234 adds nested sequence term encoding for quotation terms. ADR-0235 checks the naive fixed-point equation candidate and records the code mismatch. ADR-0236 makes the aggregate formal-confidence surface validate that candidate dependency. ADR-0237 validates the direct quotation-term length-growth obstruction; ADR-0238 makes the aggregate formal-confidence surface validate that obstruction dependency. ADR-0239 adds checked `pi1`/`sigma1` complement examples. ADR-0241 adds a checked `substitution_code` term surface for later diagonal construction. ADR-0242 adds the checked diagonal seed, ADR-0243 makes that seed visible to aggregate formal-confidence validation, and ADR-0244 checks the seed self-application graph point. Fixed-point equation proof remains open. |
| AFS-R6 | Represent the computational substrate as an explicit transition system. | PRC Universal Cells are modeled as Mealy-machine-like elements with role, memory, input, output, automail, control, and buffer state. | State transition tests generated from a formal table; eventual model-checkable specification. | Started with the fixed-role probe in `autarkic_systems/universal_cell.py`; PRC still has broader Scheme/TLA incompleteness. |
| AFS-R7 | Treat reconfiguration as a first-class formal action, not an implementation side effect. | PRC's central claim is component-wise organic reconfigurability. AS needs to know when reconfiguration preserves guarantees. | Tests for role-change transitions and invariants such as signal conservation, buffer handling, and allowed command forms. | Started with `step_stem_cell` automail reconfiguration tests and `UC-STEM-AUTOMAIL-RECONFIGURES`; full stem buffer semantics remain open. |
| AFS-R8 | Bridge formal claims to substrate claims through named predicates and proof obligations. | AS must integrate SJAS formal confidence with PRC substrate visibility. | A small toy bridge: a proof-side predicate about a transition-system invariant, checked against executable substrate examples. | Started with `autarkic_systems/transition_predicates.py`, `claims/transition_claims.json`, and the ADR-0011 proof-certificate checker. SJAS-level claims remain open. |
| AFS-R9 | Keep executable artifacts minimal, transparent, and heavily commented. | `AGENTS.md` requires thorough comments and executable artifacts wherever possible. ISLA notes prefer transparent fidelity over performance. | Code review plus tests; comments must explain rationale, not merely restate syntax. | Open until code is added. |
| AFS-R10 | Split fast and extended verification suites. | Project-specific instructions require slower regressions outside the default fast path without neglecting them. | `make test` or equivalent for fast checks, plus documented extended command. | Open until code exists. |
| AFS-R11 | Trace literature claims to local or public witnesses. | SJAS has a Willard paper witness archive; PRC has theory notes and references; AS must not rely on vague memory. | Bibliography table with claim-to-source links and local witness hashes where available. | Partially satisfied by subordinate review; needs dedicated literature map. |
| AFS-R12 | Maintain a gap register for incomplete, stale, or contradictory artifacts. | PRC has incomplete TLA and research-grade Scheme; SJAS has placeholder tests and active work outside the visible public Proflog main branch. | Every roadmap slice identifies whether it closes, accepts, or defers known gaps. | Started below. |

## Gap Register

| Gap | Evidence | Consequence | Next action |
| --- | --- | --- | --- |
| AFS is only named, not defined, in `jpt4/afs`. | `jpt4/afs` contains only a placeholder README at the reviewed commit. | AS must supply the first operational AFS definition. | This document is the first definition; ADR-0003 should pin source manifests. |
| Public Proflog does not match the active SJAS log frontier. | `jpt4/proflog` public `main` has only two commits and no ADR-006x material, while SJAS `nachlass/LOG.md` records Proflog ADR-0063 through ADR-0068. | AS cannot treat the public Proflog repo as the full executable SJAS substrate. | Locate the active Proflog branch/repo or record it as unavailable. |
| Public Proflog test entry does not run under available Guile. | `guile proflog.scm` failed with `Unbound variable: even` at the embedded `P1` definition. | Current public Proflog is not a green dependency in this environment. | Do not build AS requirements on it as passing evidence; revisit if Chez/Racket or a fixed macro form is available. |
| PRC Universal Cell implementation is not yet a verified substrate. | `practice/asmsim.scm` appears to contain unresolved helper/name issues and `universal-cell.tla` is incomplete. | AS needs a clean executable probe before relying on PRC simulation claims. | ADR-0004 should consider a tiny transition verifier extracted from the formal model. |
| X/Twitter reference in `AGENTS.md` is uncaptured. | Direct web fetch returned no usable text and search found no reliable mirror. | Some intended project context may be missing. | Ask owner or find an archival mirror if the reference becomes important. |

## First Executable Probe Recommendation

The highest-leverage first code-bearing slice is a tiny substrate/formal bridge,
not a full theorem prover or full Universal Cell simulator.

Recommended ADR-0004 shape:

1. Extract a small, explicit transition table for one PRC Universal Cell role,
   probably wire or processor.
2. Write failing tests for accepted transitions, rejected malformed input, and
   one invariant such as output-not-overwritten.
3. Implement a minimal transition checker in a language chosen for clarity.
4. Add a formal-side predicate vocabulary that can state the invariant.
5. Document exactly what this does not yet prove about SJAS or PRC.

This gives AS an executable artifact while respecting the larger theory: it
tests whether a substrate claim can be represented and checked before trying to
make the system self-justify that claim.
