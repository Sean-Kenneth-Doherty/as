# Proof Apparatus Options

Status: ADR-0010 decision note, 2026-05-17.

## Question

What should AS use as its first proof apparatus?

The immediate need is not a full Willard-style self-justifying system. The
immediate need is a transparent path from the current transition claims in
`claims/transition_claims.json` toward inspectable proof objects, while keeping
the later SJAS and Proflog direction open.

## Evidence Reviewed

| Candidate | Local witness | Useful evidence | Current limitation |
| --- | --- | --- | --- |
| Public Proflog/Fitting path | `/home/sean/Projects/_upstream/proflog/proflog.scm` and `/home/sean/Projects/_upstream/proflog/LPTableaus.pdf` | Public Proflog is explicitly Fitting-style semantic tableaux, includes equality-oriented discussion, iterative deepening, and three-valued ground-query behavior. SJAS `nachlass/LOG.md` reports much more recent Proflog work around code-level syntax, substitution, and `tableau-proof/3`. | Public `jpt4/proflog` main is not the same artifact described by the SJAS ADR-006x notes and failed the local Guile smoke test. AS should not make it a passing dependency yet. |
| LeanTAP/alphaLeanTAP | `/home/sean/Projects/_upstream/leanTAP` at `c17864a911c0c3cbd727b43743fdcb19b43714b8` | The Scheme source exposes a compact proof search relation with proof terms such as `conj`, `split`, `univ`, `savefml`, and `close`; the README describes a first-order classical theorem prover with Scheme and Clojure implementations; the tests cover Pelletier problems. | It is a useful transparent reference, but it is not Willard-specific, not an AS object-language checker, and does not by itself provide arithmetized proof codes for self-reference. |
| Minimal AS-local checker | Current AS code and claim manifest | The current project already has named predicate claims, executable examples, and strict fast tests. A tiny local checker can be designed around the exact proof obligations AS has now. | It will initially be a deliberately small proof-certificate checker, not a general theorem prover and not a self-justifying axiom system. |

## Decision

Start with a minimal AS-local proof-certificate checker for the current
transition-claim surface.

The first checker should validate small proof objects attached to claim IDs,
with enough structure to say which rule or executable witness justifies a
claim. It should be implemented only after a separate ADR defines the proof
object syntax and red tests.

This decision explicitly keeps LeanTAP and Proflog in scope:

- LeanTAP is the transparency reference for what a small tableaux prover can
  look like.
- Proflog/Fitting remains the most aligned long-term direction for
  SJAS-flavored tableaux, but AS must first recover or replace the active
  Proflog ADR-006x frontier before depending on it.

## Why Not Proflog First

Proflog is conceptually close to SJAS because it is built around semantic
tableaux, equality behavior, and logic-programming-style query execution. The
visible public repository, however, is currently a gap rather than a green
dependency:

- the active SJAS log describes Proflog ADR-0063 through ADR-0068 work that is
  not present on public `main`;
- the local Guile smoke test did not pass;
- adopting it first would tie AS to a missing implementation frontier before
  AS has even named its own proof-object surface.

The efficient move is to preserve Proflog as a major target while building a
small local bridge that can be tested now.

## Why Not LeanTAP First

LeanTAP is small and inspectable. It is also close enough to the ISLA notes to
serve as a reference implementation style. But adopting it as the first AS
apparatus would skip over AS-specific requirements:

- AS needs proof objects that point at substrate claims and manifest examples;
- later SJAS work needs inspectable coding and substitution vocabulary, not
  only host-language proof search;
- LeanTAP's useful proof terms are not yet the same as AS claim proof terms.

LeanTAP should inform design, not become the first dependency.

## Next ADR Shape

ADR-0011 defines the first tiny proof-object vocabulary for the existing
transition claims.

Implemented minimum deliverables:

- a JSON or Python-literal proof certificate format tied to claim IDs;
- red tests for accepted and rejected certificates;
- a checker that refuses unknown claim IDs, unknown rule names, malformed
  witnesses, and mismatched expected results;
- documentation that the checker is proof-certificate validation for current
  AS claims, not general theorem proving.

Implemented certificate clauses:

- `manifest-example`: a claim example was evaluated by the manifest evaluator;
- `predicate-result`: a named predicate returned the expected boolean result;

The current transition proof-certificate surface can be inspected directly with
`python -m autarkic_systems.proof_certificates` or with `--format json` for
machine-readable output.

Candidate future certificate clauses:

- `transition-witness`: a before/after transition pair matches a concrete
  Universal Cell step result.

## Non-Goals

- Do not claim an SJAS consistency theorem from this checker.
- Do not claim that AS has implemented Proflog, Fitting, or LeanTAP.
- Do not encode Willard-style arithmetized proof codes in the first local
  checker unless ADR-0011 explicitly narrows that work.
- Do not make public Proflog a hard dependency until the visible source gap is
  closed or deliberately replaced.
