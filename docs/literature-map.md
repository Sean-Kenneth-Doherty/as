# Literature Map

Status: first pass, 2026-05-17.

This map organizes sources by the role they play in Autarkic Systems. It is not
a claim that the literature review is complete. It is a working index for
turning source pressure into ADRs, executable probes, and proof obligations.

## Root And Integration Sources

| Source | Local witness | AS role | Current use |
| --- | --- | --- | --- |
| AS prelude and development rules | `AGENTS.md` | Defines the lower-bound objective: theory, literature organization, novel conceptual contributions, executable artifacts, and hardware schematics/simulation for cognitive sovereignty. | Governs all ADRs and documentation layers. |
| AFS placeholder | `/home/sean/Projects/_upstream/afs/README.md` | Names Autarkic Formal Systems but does not operationalize it. | Forces AS to define AFS requirements locally. |
| AS source manifest | `sources/manifest.json` | Pins the reviewed repository baseline. | Prevents source drift from silently changing conclusions. |

## PRC: Substrate And Embodiment

| Source | Local witness | AS role | Current use |
| --- | --- | --- | --- |
| PRC README | `/home/sean/Projects/_upstream/prc/README.md` | States the embodied-computation argument and the Universal Cell requirements: reversible logic, asynchronous operation, explicit signal/power routing, and organic component-wise reconfigurability. | Basis for AFS-R6 and AFS-R7. |
| GELC universality note | `/home/sean/Projects/_upstream/prc/theory/official/gelc-universality.txt` | Argues that geometrically explicit RLEM circuits can be computationally universal while making wires first-class formal objects. | Supports the decision to model routing as substrate logic, not implementation detail. |
| Universal Cell formal model | `/home/sean/Projects/_upstream/prc/theory/official/formal-model.txt` | Gives the state-machine vocabulary for roles, memory, input, output, automail, control, and buffer. | Source for the fixed-role transition probe. |
| Universal Cell Scheme simulator | `/home/sean/Projects/_upstream/prc/practice/asmsim.scm` | Executable research artifact for UC behavior. | Background only; not yet treated as trusted because first review found rough edges. |
| RALA, Morita RLEM, switchable circulator references | PRC README and GELC note reference sections | Prior art for reconfigurable asynchronous logic, reversible logic elements with memory, and possible physical implementation. | Needed for later hardware/schematic review. |

## SJAS: Formal Confidence

| Source | Local witness | AS role | Current use |
| --- | --- | --- | --- |
| SJAS README | `/home/sean/Projects/_upstream/sjas/README.md` | Defines the self-justifying logic program: consistency relative to PA plus self-provability of consistency under expressivity constraints. | Basis for AFS-R2 through AFS-R5. |
| Willard paper witness archive | `/home/sean/Projects/_upstream/sjas/nachlass/papers/README.md` | Maps many Willard primary texts to local/public witnesses and records gaps. | Primary source index for formal-confidence claims. |
| AS Willard definition map | `docs/willard-definition-map.md` and `sources/willard_definition_map.json` | Names the first exact Willard definitions, constructions, theorem statements, and boundaries that AS formal-confidence claims must preserve. | Active anchor map for P5 and later proof-code/object-language ADRs. |
| Works citing Willard archive | `/home/sean/Projects/_upstream/sjas/nachlass/works-citing-dew/README.md` | Maps second-order literature around self-verifying theories, provability of consistency, and AI-adjacent Loebian concerns. | Source for broader significance and related-work review. |
| ISLA notes | `/home/sean/Projects/_upstream/sjas/code/isla/notes.txt` | Records implementation notes for IS(A)/IS-lambda(A), grounding functions, tableaux with equality, and syntax/formula distinctions. | Candidate basis for the first syntax and proof-apparatus ADR. |
| ISLA Racket sketch | `/home/sean/Projects/_upstream/sjas/code/isla/isla.rkt` | Exploratory grammar and grounding-function implementation. | Background for future object-language validators. |
| Theta Clojure/core.logic experiments | `/home/sean/Projects/_upstream/sjas/code/theta/` | Experiments with Willard 2017 theta languages and relational arithmetic. | Background; not yet trusted as a green dependency. |

## Adjacent Proof Apparatus Sources

| Source | Local witness | AS role | Current use |
| --- | --- | --- | --- |
| Proflog public repo | `/home/sean/Projects/_upstream/proflog/proflog.scm` | Candidate Fitting-style semantic-tableaux implementation. | Background only; public main failed the local Guile smoke test and does not expose the newer SJAS ADR-006x frontier. |
| AS Proflog source-status note | `docs/proflog-frontier-status.md` and `sources/proflog_frontier_status.json` | Records the public-main visibility gap against SJAS ADR-006x logs. | Active P6 decision: do not depend on public Proflog main. |
| Fitting, "Tableaux for Logic Programming" | `/home/sean/Projects/_upstream/proflog/LPTableaus.pdf` | The immediate source for Proflog's intended proof/refutation apparatus. | Candidate proof-apparatus source for AFS-R3. |
| LeanTAP/alphaLeanTAP | `/home/sean/Projects/_upstream/leanTAP` | Candidate transparent tableaux prover direction referenced by ISLA notes. | Reviewed for ADR-0010; useful as a design reference, not the first AS dependency. |

## Claim-To-Source Map

| AS claim | Source support | Evidence status |
| --- | --- | --- |
| AS must join formal self-confidence to embodied substrate visibility. | AS prelude, PRC README, SJAS README. | Strong enough for roadmap and requirements. |
| AFS cannot currently be delegated to `jpt4/afs`. | AFS placeholder README. | Verified at reviewed commit. |
| Universal Cell routing is a valid first executable substrate slice. | PRC formal model, PRC README, GELC note. | Partially implemented in AS fixed-role probe. |
| Fixed-role transition predicates are only a bridge, not a proof of PRC. | PRC formal model has broader stem/automail/buffer behavior. | Explicit coverage limit in ADR-0004 and ADR-0005. |
| SJAS work requires careful expressivity/proof-apparatus tradeoffs. | SJAS README and Willard witness archive. | Strong enough for AFS requirements; detailed theorem claims still need paper-level annotation. |
| Proflog is relevant but not currently a passing dependency. | SJAS `nachlass/LOG.md`, public Proflog repo, failed Guile run. | Gap recorded in `docs/afs-requirements.md` and `sources/manifest.json`. |
| Public Proflog main must not be treated as the active ADR-006x implementation. | `docs/proflog-frontier-status.md`, `sources/proflog_frontier_status.json`, public `jpt4/proflog` main at `77af848`, and SJAS `nachlass/LOG.md`. | ADR-0014 records the source-status decision and maintainer question. |
| AS should start proof work with a tiny local certificate checker. | Current claim manifest, LeanTAP source, public Proflog source, SJAS Proflog boundary log. | Decision recorded in ADR-0010 and `docs/proof-apparatus-options.md`. |
| AS cannot claim Willard-style formal confidence until it preserves exact syntax, proof-code, deduction-method, and consistency-level anchors. | Willard 2001 Definitions 1.1/1.2 and Theorem 4.3; Willard 2011 Definitions 3.4/5.6/5.7 and Theorem 5.9; Willard 2016 Definitions 3.2/3.4/4.1 and Theorem 6.7; Willard 2020 Definitions 3.2/3.4 and Theorems 4.4/4.5. | First anchored in ADR-0013, `docs/willard-definition-map.md`, and `sources/willard_definition_map.json`. |

## Evidence Gaps

- The X/Twitter reference in `AGENTS.md` remains uncaptured.
- Willard 1993 and Willard 1997 public full-text witnesses were not available
  in the SJAS paper archive.
- PRC's Scheme simulator and TLA+ sketch need deeper verification before AS
  treats either as canonical.
- The active Proflog ADR-006x frontier described by SJAS logs is not present on
  public Proflog `main`; ADR-0014 records this as a do-not-depend decision.
- AS has not yet annotated the actual Willard papers at theorem/definition
  granularity beyond the first four-source ADR-0013 map.
- LeanTAP has now been reviewed as a transparency reference, but AS has not
  ported or executed it as a project dependency.
