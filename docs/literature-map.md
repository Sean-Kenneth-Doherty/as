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
| AS PRC hardware witness map | `docs/prc-hardware-witness-map.md` and `sources/prc_hardware_witness_map.json` | Names the first exact PRC hardware/schematic witnesses and constraints before AS draws or simulates PRC-derived hardware. | Active anchor map for P7 and the next single-node schematic/trace ADR. |
| AS single-node schematic trace | `docs/single-node-schematic-trace.md` and `schematics/single_node_triangular_rlem_trace.json` | First AS-owned schematic key connecting one triangular RLEM/UC node to an executable Universal Cell transition. | Active P7 artifact for schematic-linked trace work. |
| AS single-node schematic SVG | `docs/single-node-schematic-svg.md` and `schematics/single_node_triangular_rlem_trace.svg` | First visible render of the structured single-node schematic trace. | Checked against renderer output so the diagram cannot drift from the JSON trace. |
| AS processor memory-toggle trace | `docs/processor-memory-toggle-trace.md` and `schematics/processor_memory_toggle_trace.json` | Second schematic-linked trace, covering processor routing plus memory toggle. | Extends P7 fixed-role coverage beyond wire behavior. |
| AS processor memory-toggle SVG | `docs/processor-memory-toggle-svg.md` and `schematics/processor_memory_toggle_trace.svg` | Visible render of the processor memory-toggle trace. | Checked against generic renderer output so the processor diagram cannot drift from the JSON trace. |
| AS stem automail reconfiguration trace | `docs/stem-automail-reconfiguration-trace.md` and `schematics/stem_automail_reconfiguration_trace.json` | Third schematic-linked trace, covering one stem automail reconfiguration into processor-left. | Extends P7 coverage into the first reconfiguration subset. |
| AS stem automail reconfiguration SVG | `docs/stem-automail-reconfiguration-svg.md` and `schematics/stem_automail_reconfiguration_trace.svg` | Visible render of the stem automail trace. | Checked against generic renderer output and exposes role/automail reconfiguration details. |
| AS stem buffer accumulation | `docs/stem-buffer-accumulation.md`, `autarkic_systems/universal_cell.py`, and `tests/test_stem_buffer_accumulation.py` | First standard-signal stem command-buffer subset. | Implements high-rail selection and 1/0 buffer append while leaving full command execution open. |
| AS stem buffer claim | `docs/stem-buffer-claim.md`, `claims/transition_claims.json`, and `claims/proof_certificates.json` | Named claim and proof-certificate surface for stem buffer accumulation. | Keeps ADR-0022 behavior available to later proof/object-language work. |
| AS stem buffer accumulation trace | `docs/stem-buffer-accumulation-trace.md` and `schematics/stem_buffer_accumulation_trace.json` | Schematic-linked trace for one matching-input stem buffer append. | Extends P7 beyond automail reconfiguration into standard-signal stem buffering. |
| AS stem buffer accumulation SVG | `docs/stem-buffer-accumulation-svg.md` and `schematics/stem_buffer_accumulation_trace.svg` | Visible render of the stem buffer accumulation trace. | Checked against generic renderer output and exposes control/buffer before/after details. |
| AS stem command-buffer map | `docs/stem-command-buffer-map.md` and `sources/stem_command_buffer_map.json` | Source-backed 32-value target/command decoder for five-bit stem buffers. | Prepares full-buffer command execution without embedding the encoding in transition code. |
| AS stem command execution source status | `docs/stem-command-execution-source-status.md` and `sources/stem_command_execution_source_status.json` | Source-status decision for why full command execution is blocked after decoding. | Separates the formal command table from unresolved self-mailbox, output-token, and legacy divergence questions. |
| AS self mailbox representation | `autarkic_systems/universal_cell.py`, `language/transition_claim_language.json`, and checked schematic traces | Explicit Cell field for self-target command delivery preparation. | Covers representation only; command execution and neighbor command outputs remain open. |

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
| AS hardware/schematic artifacts must preserve PRC's actual commitments rather than merely resembling PRC diagrams. | PRC README, GELC universality note, Morita RLEM witness, PRC formal model, ASM simulator, old Thiel/RALA notes, and PRC figures. | First anchored in ADR-0015, `docs/prc-hardware-witness-map.md`, and `sources/prc_hardware_witness_map.json`. |
| A PRC-derived schematic key can be tied to executable AS behavior before larger circuit design. | ADR-0015 witness map, AS Universal Cell probe, and `schematics/single_node_triangular_rlem_trace.json`. | First implemented in ADR-0016 with validation in `tests/test_single_node_schematic_trace.py`. |
| A rendered schematic can stay subordinate to a structured executable trace. | `schematics/single_node_triangular_rlem_trace.json`, `autarkic_systems/schematic_svg.py`, and `schematics/single_node_triangular_rlem_trace.svg`. | First implemented in ADR-0017 with exact renderer-output matching tests. |
| Schematic-linked traces can cover processor memory toggle without adding new UC semantics. | AS Universal Cell processor probe and `schematics/processor_memory_toggle_trace.json`. | Implemented in ADR-0018 with validation in `tests/test_processor_memory_toggle_trace.py`. |
| A generic schematic SVG renderer can render fixed-role wire and processor traces while preserving JSON authority. | `schematics/processor_memory_toggle_trace.json`, `schematics/processor_memory_toggle_trace.svg`, and `autarkic_systems/schematic_svg.py`. | Implemented in ADR-0020 with exact renderer-output matching tests for wire and processor SVGs. |
| Schematic-linked traces can cover the first stem automail reconfiguration subset without claiming full dynamic reconfiguration. | AS Universal Cell stem automail probe and `schematics/stem_automail_reconfiguration_trace.json`. | Implemented in ADR-0019 with validation in `tests/test_stem_automail_reconfiguration_trace.py`. |
| A stem reconfiguration SVG must expose role and automail changes, not only port geometry. | `schematics/stem_automail_reconfiguration_trace.json`, `schematics/stem_automail_reconfiguration_trace.svg`, and `tests/test_stem_automail_svg.py`. | Implemented in ADR-0021 with exact renderer-output matching and drift rejection. |
| Stem command-buffer behavior can advance in a bounded subset before full command execution. | PRC formal model, `autarkic_systems/universal_cell.py`, and `tests/test_stem_buffer_accumulation.py`. | Implemented in ADR-0022 for high-rail selection and bit accumulation only. |
| Stem buffer accumulation belongs in the named claim surface before command decoding depends on it. | `claims/transition_claims.json`, `claims/proof_certificates.json`, and `autarkic_systems/transition_predicates.py`. | Implemented in ADR-0023 with positive/negative manifest examples and certificate coverage. |
| Schematic-linked stem traces must distinguish automail reconfiguration from standard-signal buffer accumulation. | `autarkic_systems/schematic_trace.py` and `schematics/stem_buffer_accumulation_trace.json`. | Implemented in ADR-0024 with separate buffer alignment validation. |
| A stem buffer render must expose command-buffer state, not only role and port geometry. | `autarkic_systems/schematic_svg.py` and `schematics/stem_buffer_accumulation_trace.svg`. | Implemented in ADR-0025 with exact renderer-output matching and drift rejection. |
| Stem full-buffer execution needs an explicit target/command map before code mutates cells or routes messages. | PRC formal model, `sources/stem_command_buffer_map.json`, and `autarkic_systems/stem_command_map.py`. | Implemented in ADR-0026 as a validated decoder only. |
| Stem command execution needs source-status separation before AS trusts legacy simulator sketches. | PRC formal model, legacy `raa.scm`, legacy `semsim.scm`, legacy `fsmsim.scm`, and `sources/stem_command_execution_source_status.json`. | Implemented in ADR-0027 as a do-not-execute-yet decision with allowed narrower next slices. |
| Self-target stem command work needs a first-class mailbox field before execution. | PRC formal model process-buffer sketch, `autarkic_systems/universal_cell.py`, and `language/transition_claim_language.json`. | Implemented in ADR-0028 as representation only, with reset clearing and parser/trace preservation. |

## Evidence Gaps

- The X/Twitter reference in `AGENTS.md` remains uncaptured.
- Willard 1993 and Willard 1997 public full-text witnesses were not available
  in the SJAS paper archive.
- PRC's Scheme simulator and TLA+ sketch need deeper verification before AS
  treats either as canonical.
- AS has rendered the wire, processor, stem automail, and stem buffer
  PRC-derived traces, and has a stem command-buffer map. Full stem command
  execution, larger GELC, and physical-simulation renders remain open. ADR-0027
  records the current source-status blockers for execution; ADR-0028 clears the
  self-mailbox representation blocker only.
- The active Proflog ADR-006x frontier described by SJAS logs is not present on
  public Proflog `main`; ADR-0014 records this as a do-not-depend decision.
- AS has not yet annotated the actual Willard papers at theorem/definition
  granularity beyond the first four-source ADR-0013 map.
- LeanTAP has now been reviewed as a transparency reference, but AS has not
  ported or executed it as a project dependency.
