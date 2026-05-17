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
or proof-apparatus clauses behind those claim IDs. ADR-0011 adds the first
minimal proof certificates over the manifest examples; richer object-language
proof clauses remain open.

Status update: ADR-0031 promotes the self-mailbox init-command execution subset
into a named transition claim with manifest examples and proof-certificate
coverage. ADR-0034 promotes the unresolved self-mailbox command boundary into a
preservation claim. ADR-0041 promotes the unsupported completed command-buffer
append boundary into a named claim.

## P2: Expand From Fixed Roles To Stem/Reconfiguration

Question: Which stem-cell transition subset is small enough to test without
pretending to reimplement all of PRC?

Why it matters: Reconfiguration is central to PRC and AS, while the current
probe only covers fixed wire/proc behavior.

Status: started by ADR-0008. `step_stem_cell` now covers automail
reconfiguration commands `wr`, `wl`, `pr`, and `pl`. ADR-0022 adds the first
standard-signal buffer accumulation subset: high-rail selection, matching and
non-matching bit append, explicit full-buffer boundary, and malformed-input
rejection. Full command decoding, target delivery, and dynamic reconfiguration
remain open. ADR-0009 added the corresponding `automail_reconfigures_stem`
predicate and manifest claim. ADR-0023 added the corresponding
`stem_buffer_accumulates` predicate and manifest claim for the buffer
accumulation subset. ADR-0024 added a schematic-linked trace for one matching
buffer append. ADR-0026 added the explicit five-bit target/command map needed
before command execution. ADR-0027 records the command-execution source-status
blockers: self mailbox state, command-message output representation, and
legacy source divergences. ADR-0028 adds explicit `self_mailbox` representation
but still leaves command-message output representation and execution semantics
open. ADR-0029 adds command-message channel tokens, leaving delivery and
execution semantics open. ADR-0030 adds the first self-mailbox init-command
execution slice while leaving write-buffer, `standard-signal`, and neighbor
delivery semantics open. ADR-0031 adds the corresponding named claim and
proof-certificate surface for that init-command execution slice. ADR-0032 adds
a schematic-linked trace for one `proc-l-init` self-mailbox command. ADR-0033
adds the corresponding rendered SVG view. ADR-0034 adds a named claim proving
that unsupported self-mailbox commands remain preserved rather than executed.
ADR-0035 adds a schematic-linked trace for one `write-buf-one` unsupported
self-mailbox command. ADR-0036 adds the corresponding rendered SVG view.
ADR-0037 adds the first narrow command-buffer execution slice: self-target
init-family commands when the fifth buffer bit is appended.
ADR-0038 promotes that dispatch into a named claim with proof-certificate
coverage. ADR-0039 adds the corresponding schematic-linked trace for one
completed `self/proc-l-init` command buffer. ADR-0040 adds the rendered SVG
view of that trace. ADR-0041 adds the named claim for completed command buffers
that still stop at the append boundary because they are neighbor-target or
self-target non-init commands. ADR-0042 adds a schematic-linked trace for one
decoded `neighbor-a/stem-init` buffer that remains at that boundary. ADR-0043
adds the rendered SVG view of that trace.

## P3: Choose The First Proof Apparatus

Question: Should AS start with a tiny local tableaux checker, a repaired public
Proflog, or a reference to another transparent tableaux implementation?

Why it matters: SJAS requirements depend on proof apparatus details; AS cannot
claim formal self-confidence without one.

Status: decided by ADR-0010. AS will start with a minimal local
proof-certificate checker over the current transition-claim surface, use
LeanTAP as a transparent tableaux reference, and keep Proflog/Fitting as the
long-term SJAS-aligned path once the active frontier is recovered or replaced.

Status update: ADR-0011 added the first local proof-certificate checker for the
current transition claims.

## P4: Define The First Object Language

Question: What syntax is sufficient for the first AS claims: transition
predicates only, IS(A)-style arithmetic fragments, or both?

Why it matters: AFS-R2 requires explicit syntax classes for terms, formulae,
sentences, proof objects, and substrate claims.

Status: started by ADR-0012. `language/transition_claim_language.json` now
names the first explicit syntax classes for current transition claims, and
`autarkic_systems/object_language.py` validates the current claim/certificate
surface against that language. IS(A), Type NS, tableaux syntax, and
arithmetized proof-code syntax remain open.

## P5: Annotate Core Willard Sources At Definition Granularity

Question: Which definitions and theorem statements from Willard 2001, 2011,
2016, and 2020 are actually needed for the first AS formal-confidence claim?

Why it matters: Current SJAS evidence is strong at the repository level, but AS
needs exact theorem/definition anchors before it can make non-hand-wavy claims.

Status: started by ADR-0013. `docs/willard-definition-map.md` and
`sources/willard_definition_map.json` now identify the first definition,
construction, theorem, and boundary anchors from Willard 2001, 2011, 2016, and
2020, with local PDF witnesses and AS relevance. Remaining work is to turn one
of those anchors into executable syntax, proof-code, or proof-apparatus
machinery.

## P6: Recover Or Replace The Active Proflog Frontier

Question: Where is the Proflog ADR-006x work described in SJAS logs, and should
AS depend on it?

Why it matters: Public Proflog `main` does not match the active SJAS log and
does not run under Guile in this environment.

Status: started by ADR-0014. `docs/proflog-frontier-status.md` and
`sources/proflog_frontier_status.json` record that public Proflog main is
relevant background but not dependency-ready executable evidence. Remaining work
is to recover/publish the ADR-0063 through ADR-0068 source or choose an AS-local
replacement path.

## P7: Hardware/Schematic Evidence Path

Question: What is the smallest schematic or simulation artifact that honors
PRC's physical implementation claims without requiring full hardware design?

Why it matters: The AS prelude explicitly includes schematics and hardware
simulation as lower-bound project content.

Status: started by ADR-0015. `docs/prc-hardware-witness-map.md` and
`sources/prc_hardware_witness_map.json` now map the required PRC witnesses for
RLEM, GELC geometry, circulator physical hypotheses, RALA/reconfiguration
pressure, the UC formal model, the ASM simulator, and schematic figures.
ADR-0016 added the first AS-owned single-node triangular RLEM schematic key and
paired it with one executable Universal Cell transition trace. Remaining work
is to decide how larger GELC examples should be reconstructed. ADR-0017 added
a generated SVG render for the first structured key, with tests preventing
drift from the JSON trace. ADR-0018 added a processor memory-toggle trace using
the same schema and executable replay path. ADR-0019 added the first stem
automail reconfiguration trace. ADR-0020 added a generated SVG render for the
processor trace. ADR-0021 added a generated SVG render for the stem trace. Full
stem command decoding, dynamic reconfiguration, larger GELC examples, and
physical-simulation renders remain open. ADR-0025 added a generated SVG render
for the stem buffer trace. ADR-0027 blocks full stem command execution until
the state model for command-message outputs and self-target consumption is
explicit; ADR-0028 covers representation of the self mailbox, and ADR-0029
covers representation of command-message channel tokens. ADR-0030 executes
self-mailbox init-family commands only, with ADR-0031 adding the matching claim
and proof-certificate surface. ADR-0032 adds a schematic-linked trace for the
same bounded behavior, and ADR-0033 adds the rendered SVG view.
ADR-0034 records the remaining self-mailbox `standard-signal` and write-buffer
commands as a checkable unsupported boundary.
ADR-0035 adds a schematic-linked preservation trace for that boundary.
ADR-0036 adds the rendered SVG view.
ADR-0037 adds narrow self-target init command-buffer dispatch while leaving
neighbor routing and self-target non-init commands open.
ADR-0038 adds the corresponding claim/proof surface.
ADR-0039 adds the corresponding schematic-linked trace.
ADR-0040 adds the corresponding rendered SVG view.
ADR-0041 adds the corresponding unsupported completed-buffer boundary claim.
ADR-0042 adds the corresponding schematic-linked trace.
ADR-0043 adds the corresponding rendered SVG view.
