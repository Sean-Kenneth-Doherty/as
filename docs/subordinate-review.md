# Subordinate Repository Review

Reviewed on 2026-05-16.

## Source Snapshots

| Program | Repository | Reviewed commit | Default branch | First-read status |
| --- | --- | --- | --- | --- |
| AS | `https://github.com/jpt4/as` | `1a2fc06b75f5d33aee6655956c2a56df07a7bfb0` | `main` | New umbrella repo with project constitution only. |
| AFS | `https://github.com/jpt4/afs` | `a61592eab02a93d480149ce3465af5e3271ca213` | `main` | Placeholder README only. |
| PRC | `https://github.com/jpt4/prc` | `7e82c73fac8f108faac801a5c65e2c2b92653ba5` | `master` | Mature research/code archive, mostly 2015-2020. |
| SJAS | `https://github.com/jpt4/sjas` | `f1c11af5f310d39f487c3b91ee1ca70f4ade8871` | `master` | Active research/code/literature archive, updated in 2026. |

The referenced X/Twitter status in `AGENTS.md` was not captured during the
first review because the web fetch exposed no usable text and search did not
locate a reliable mirror.

## AFS

`jpt4/afs` currently contains only:

- `README.md`: `# afs` and `Autarkic Formal Systems`.

Interpretation:

- AFS is named as the direct formal-systems layer under AS, but its public
  repository has not yet been made operational.
- AS therefore should initially act as the integrator that turns PRC and SJAS
  into an AFS roadmap rather than assuming AFS already supplies one.

Immediate obligations:

- Define what an Autarkic Formal System must be beyond the name.
- Map PRC's substrate constraints and SJAS's formal-confidence constraints into
  AFS-level requirements.
- Decide whether mature artifacts should stay in their original repositories,
  be vendored, or be represented by reproducible reference manifests.

## PRC

`jpt4/prc` presents Pervasively Reconfigurable Computing as a project to align
computers with their embodiment, make resource consumption visible and tunable,
and produce a platform acceptable to the investigator and a seed SAI.

Important reviewed elements:

- `README.md`: states the project argument, the division between `theory/` and
  `practice/`, and the Universal Cell/RLEM/GELC thrust.
- `theory/official/gelc-universality.txt`: argues by construction that certain
  geometrically explicit circuits of RLEMs are computationally universal.
- `theory/official/formal-model.txt`: defines the Universal Cell as a Mealy
  machine with explicit fields for state, role, upstream/input/output, memory,
  automail, control, and buffer.
- `practice/asmsim.scm`: a Chez Scheme simulator for the Universal Cell
  abstract state machine.
- `theory/project-log.txt`: records the reversible reconfiguration focus,
  especially the need for data movement, buffering, and logical gain at cell
  granularity.
- `theory/official/universal-cell.tla`: an incomplete TLA+ start.

AS relevance:

- PRC is the body/substrate side of cognitive sovereignty.
- Its key contribution is not just "hardware simulation"; it is the demand that
  routing, physical embodiment, and reconfiguration be explicit enough that a
  cognitive system is not trusting an opaque substrate.
- PRC gives AS a hardware and simulation agenda: recover the Universal Cell
  semantics, validate the simulator, and eventually connect formal reasoning to
  reconfiguration-preserving state transitions.

Observed technical risks:

- The active Scheme simulator appears research-grade and partially unfinished.
  Example concerns from first read include placeholder or malformed helper
  references such as `Esi-or-Esss@!x?`, duplicated `ir` definitions where one
  likely meant `il`, and a suspicious `(con! empty asm)` argument order.
- The TLA+ file is incomplete.
- There is no visible modern fast test harness.

## SJAS

`jpt4/sjas` presents Self-Justifying Axiom Systems as the formal-confidence
side of autarkic logic.

The README asks whether Willard's work on Goedel's Second Incompleteness
Theorem can be extended to other limitative theorems and programming-language
barriers. It frames SJAS as systems that retain consistency relative to Peano
Arithmetic and self-provability of consistency by weakening or tuning
expressivity.

Local objectives from the README:

1. Implement an interpreter for the Type NS languages in Willard 2017.
2. Formalize the proof of non-diagonalizability for Type NS languages in a
   stronger metalanguage such as Idris, Coq, or Agda.
3. Formalize as much of that proof as possible in a Type NS language itself.

Important reviewed elements:

- `README.md`: main research motivation and objectives.
- `lit/SJAS Literature.md`: literature map around Willard, self-verifying
  theories, encoding, self-interpretation, consistency, and related work.
- `nachlass/LOG.md`: recent active log of public-witness aggregation and
  Proflog-side SJAS implementation boundaries through May 2026.
- `code/isla/isla.rkt`: Racket implementation sketch for `IS-lambda(A)`,
  including grammar predicates and grounding functions.
- `code/sr/sr.rkt`: Racket sketch of Stellar Resolution from Eng and Seiller.
- `code/theta/`: Clojure/core.logic experiments for Willard 2017 theta
  languages and relational arithmetic.
- `code/sjl/` and `code/stellar/`: Clojure project skeletons, with failing
  placeholder tests still present.

AS relevance:

- SJAS is the logic/self-confidence side of cognitive sovereignty.
- It gives AS a formal agenda: characterize which language/deduction tradeoffs
  allow self-confidence without triggering standard diagonalization barriers.
- The active Proflog notes suggest a current frontier around inspectable
  arithmetized codes, structural decoding, substitution/proof vocabulary, and
  finite generated `IS#_D(beta)` substrates.

Observed technical risks:

- Several Clojure subprojects still carry template READMEs or placeholder
  failing tests.
- Some Racket/Clojure code is exploratory and records nontermination,
  duplicate generation, or invalid synthesis problems in comments.
- The recent active implementation frontier appears partly in adjacent Proflog
  work rather than wholly inside this repository, so AS needs to find and map
  that dependency before treating SJAS as fully captured.

## First Integration Hypothesis

AS should treat PRC and SJAS as complementary halves of the same autarkic
claim:

- SJAS asks: under what formal restrictions can a reasoning system have
  internally grounded confidence in its own consistency?
- PRC asks: under what substrate restrictions can a computing system expose and
  reconfigure its own physical/logical operation instead of trusting hidden
  authority?
- AFS should ask: what is the smallest formal architecture in which a reasoning
  system can talk about, verify, and safely reconfigure a substrate model while
  preserving the kind of self-confidence SJAS studies?

This hypothesis is only a working map. It needs to be challenged by deeper
literature review and by small executable experiments.
