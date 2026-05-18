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
proof clauses remain open. ADR-0133 adds the first `predicate-result`
certificate steps for the fixed-output preservation claim, making the proof
object name the predicate it evaluates instead of relying only on the claim
manifest lookup. ADR-0135 exposes the base transition claim examples through
direct text and JSON CLI validation. ADR-0140 carries the base claim-example
and proof-certificate validator summaries into the aggregate project status
report.

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
that still stop at the append boundary; ADR-0044 narrows that boundary to
self-target non-init commands by delivering neighbor-target command buffers to
output channels. ADR-0042/ADR-0043 now use a self-target `write-buf-one`
trace/render for the remaining unsupported append boundary. ADR-0049 consumes
recipient-side init-family command-message inputs. ADR-0050 promotes that
recipient init slice into the named claim/proof surface. Recipient-side
non-init command-message consumption and self-target non-init execution remain
open. ADR-0051 adds a schematic-linked trace for the recipient init slice.
ADR-0052 adds the rendered SVG view of that trace.
ADR-0053 records recipient non-init command-message execution as blocked and
selects a named rejection-boundary claim as the next safe slice.
ADR-0054 promotes that rejection boundary into the named claim/proof surface.
ADR-0055 adds a schematic-linked trace for one fixed recipient upstream
`standard-signal` rejection.
ADR-0056 adds the rendered SVG view of that rejection trace.
ADR-0057 records write-buffer command execution as still source-blocked.
ADR-0058 records `standard-signal` command-token execution as still
source-blocked while preserving ordinary binary-input standard-signal behavior.
ADR-0059 selects reject-and-clear for multiple simultaneous recipient
command-message inputs.
ADR-0060 adds a schematic-linked trace for that multi-command rejection policy.
ADR-0065 adds the first integrated evidence bundle for the already implemented
recipient init transition, tying one runtime example to its claim, certificate,
trace, SVG, and source-status boundaries without widening command semantics.
ADR-0066 adds the evidence bundle registry so those integrated paths can be
discovered and batch-validated as they multiply.
ADR-0067 adds a module CLI so the registry can be validated directly from the
command line.
ADR-0068 adds a second registered evidence bundle for the recipient non-init
`standard-signal` rejection boundary.
ADR-0069 adds a third registered evidence bundle for the direct multi-command
recipient rejection boundary.
ADR-0070 makes that registry complete over sibling bundle files, so future
bundle artifacts cannot bypass the manifest silently.
ADR-0071 adds JSON CLI output so the registry can be consumed by automation
without parsing human-readable `OK` lines.
ADR-0072 registers the direct self-mailbox init transition as the fourth
evidence bundle and aligns its trace/SVG fixture with the named claim example.
ADR-0073 registers the direct unsupported self-mailbox preservation boundary as
the fifth evidence bundle and aligns its trace/SVG fixture with the named
preservation example.
ADR-0074 registers the completed self-target command-buffer init dispatch as
the sixth evidence bundle.
ADR-0075 registers the completed self-target non-init command-buffer append
boundary as the seventh evidence bundle.
ADR-0076 registers the completed neighbor-target command-buffer delivery path
as the eighth evidence bundle.
ADR-0077 adds the first executable two-step chain from neighbor delivery into
recipient init-family command consumption.
ADR-0078 promotes that handoff into a named chain claim and proof-certificate
surface.
ADR-0079 makes the chain-claim object language explicit for that surface.
ADR-0080 exposes chain-claim validation as a direct text/JSON CLI.
ADR-0081 adds the first composed-chain evidence bundle and CLI, tying that
chain surface to its underlying transition evidence bundles and source-status
boundaries.
ADR-0082 records that handoff as a dedicated two-step chain trace before any
SVG rendering work.
ADR-0083 adds the checked SVG render for that chain trace.
ADR-0084 adds a closed registry for transition-chain evidence bundles so future
chain bundles cannot sit unvalidated beside the manifest.
ADR-0085 makes chain evidence CLI target selection explicit.
ADR-0086 and ADR-0087 make chain registry JSON self-describing and
failure-summarizing.
ADR-0088 gives single-bundle chain JSON the same failure summary.
ADR-0089 adds a vertical chain demo report so the current claim-to-evidence
path can be inspected from one command.
ADR-0090 makes the demo explicit about artifact presence so missing traces,
renders, manifests, bundles, or source-status records are visible in the
first-run surface.
ADR-0091 promotes the delivered non-init rejection boundary into a named
transition-chain claim, proving the composed handoff can preserve a blocked
recipient command path as well as consume the init path.
ADR-0092 records that rejection boundary as a composed-chain trace before any
rendered SVG or evidence-bundle promotion.
ADR-0093 adds the renderer-locked SVG for that rejection trace and makes the
chain SVG renderer derive the handoff channel from the delivered tuple.
ADR-0094 adds the integrated evidence bundle for that rejection path and
registers it alongside the consumed chain bundle.
ADR-0095 extends the vertical chain demo report to the whole chain registry, so
both current composed paths can be inspected from one command.
ADR-0096 adds a project status command that validates the transition and chain
evidence registries and reports the blocked command-token frontier from the
current source-status records.
ADR-0097 hardens that status command so missing registry files are structured
report failures rather than tracebacks.
ADR-0098 distinguishes malformed registry files from missing registry files in
that status output.
ADR-0099 gives the frontier section the same compact failure-subject summary
for missing or malformed source-status files.
ADR-0100 makes source-status JSON shape part of that status check, so parseable
but unusable source-status records cannot pass as an empty frontier.
ADR-0101 adds a top-level project status schema version for automation.
ADR-0102 tightens the shape check so source-status records without command
tokens cannot erase the blocked-command frontier.
ADR-0103 attributes blocked commands to each source-status entry and bumps the
project status schema version to `2`.
ADR-0104 rejects blank command-token strings so the project status frontier
cannot contain invisible command terms.
ADR-0105 rejects whitespace-only source-status decision and safe-next text so
accepted frontier entries keep meaningful operator wording.
ADR-0106 rejects non-text command-list entries so malformed source-status
commands cannot disappear from the project report.
ADR-0107 rejects malformed command-token field container shapes so recognized
source-status command fields cannot be silently ignored.
ADR-0108 adds the blocked source-status resolution question IDs to project
status and bumps the schema version to `3`.
ADR-0109 rejects malformed resolution-question metadata so blocker question IDs
cannot be silently dropped from project status.
ADR-0110 renders those checked resolution question IDs in the default text
status report so the human first-run surface exposes the same blocker work
queue as the JSON report.
ADR-0111 adds the corresponding question summaries to project status JSON and
text output, bumping the schema version to `4` so the status report now carries
the blocker work queue without requiring a second source-status file pass.
ADR-0112 adds blocked runtime surfaces to project status JSON and text output,
bumping the schema version to `5` so the report now names where the unresolved
command-token questions apply.
ADR-0113 makes transition evidence registry JSON list the concrete registered
bundle entries, matching the self-describing chain registry payload pattern.
ADR-0114 adds the corresponding transition registry JSON `failed_subjects`
summary, matching the compact chain registry failure-summary contract.
ADR-0115 adds those concrete registry bundle entries to project status JSON
and bumps the schema version to `6`, so the first diagnostic command now names
the transition and chain bundles it checked.
ADR-0116 renders those checked bundle IDs and paths in the default text status
report without changing the JSON schema.
ADR-0117 requires non-empty top-level `as_boundary` text on source-status
records consumed by project status, and adds that boundary to the recipient
non-init command-message source-status artifact.
ADR-0118 renders those source-status AS boundaries in the default text status
report without changing the JSON schema.
ADR-0119 expands the existing self-mailbox unsupported and self-target
command-buffer unsupported claim/proof surfaces so each blocked self-command
token, `standard-signal`, `write-buf-zero`, and `write-buf-one`, has its own
positive manifest example.
ADR-0120 carries that explicit coverage into the integrated evidence-bundle
layer by letting the unsupported self-command bundles validate
`covered_positive_examples` while keeping one trace-aligned primary example.
ADR-0121 exposes transition bundle `positive_example` and
`covered_positive_examples` metadata in registry JSON and project-status JSON,
bumping project status to `schema_version: 7`.
ADR-0122 renders that transition bundle primary and covered positive-example
coverage in default project-status text while preserving `schema_version: 7`.
ADR-0123 exposes source-status `additional_source_statuses` cross-links in
project-status JSON and bumps the schema version to `8`, preserving the
source-review trail behind the blocked command-token frontier.
ADR-0124 renders those source-status cross-links in default project-status text
while preserving `schema_version: 8`.
ADR-0125 requires those source-status cross-link paths to exist, so project
status cannot accept or display dead source-review links.
ADR-0126 requires those cross-link targets to contain top-level JSON objects,
so existing junk files cannot pass as source-status trail artifacts.
ADR-0127 promotes the formal-model self-mailbox exception for
`standard-signal`, narrowing the self-target-surface question without changing
runtime behavior.
ADR-0128 resolves the `standard-signal` command-table offset question in favor
of the formal PRC map, leaving the command-token/binary-input,
recipient-surface, and self-target-surface questions open.
ADR-0143 exposes the formal-model self-mailbox exception as a resolved
self-mailbox equivalence decision: stem self-mailbox `standard-signal` must not
be treated as ordinary binary-input standard-signal behavior, though the
broader self-target-surface behavior remains open.
ADR-0129 records that `write-buf-zero` and `write-buf-one` carry literal `0`
and `1` append bits, narrowing standard-signal interaction without resolving
write-buffer execution.
ADR-0142 moves that standard-signal interaction question out of the unresolved
write-buffer queue: command bits are literal rather than high-rail-derived,
while execution surface, buffer-full behavior, and post-append clearing remain
open.
ADR-0130 exposes resolved source-status questions in project status JSON/text,
so `command-table-offset` appears as settled while the remaining command-token
frontier stays open.
ADR-0131 requires resolved-question source paths to exist and contain JSON
objects, so settled blocker decisions cannot point at dead artifacts.
ADR-0132 carries the resolved `command-table-offset` formal offset and RAA
legacy divergence into project status, so the settled decision trail is no
longer reduced to a label.
ADR-0144 adds source evidence for unresolved resolution questions to project
status JSON/text, so the first diagnostic report shows the conflict or absence
of authority behind the standard-signal and write-buffer blockers.
ADR-0145 adds a focused source-status frontier CLI over those same
command-token blocker records, letting agents inspect the semantic frontier
without running the full project status report.
ADR-0146 hardens that evidence trail by requiring evidence question IDs to
match live unresolved question IDs in the same source-status record.
ADR-0147 requires that trail to cover every live unresolved question ID, so a
frontier record cannot expose an open blocker without attached evidence.
ADR-0148 resolves the standard-signal `recipient-surface` question by tying
delivered recipient `standard-signal` command messages to the existing
recipient non-init rejection claim and evidence bundle, leaving only the
command-token/binary-input and self-target-surface standard-signal questions
open.
ADR-0150 resolves the standard-signal command-token/binary-input question as a
negative equivalence decision: command tokens do not replay ordinary
binary-input standard-signal behavior by default. The standard-signal frontier
now leaves only the self-target-surface question open.
ADR-0151 resolves that remaining standard-signal self-target-surface question
through the existing self-mailbox unsupported-preservation and self-target
command-buffer append-boundary claims. Standard-signal now has no unresolved
source-status questions; write-buffer remains the command-token semantics
frontier.
ADR-0152 resolves the write-buffer recipient surface through the existing
recipient non-init rejection boundary and narrows the remaining write-buffer
surface question to self-mailbox / self-target command-buffer behavior.
ADR-0153 resolves that write-buffer self-target surface through the existing
unsupported preservation boundaries, leaving buffer-full behavior and
post-append clearing as the live write-buffer source-status questions.
ADR-0154 turns those remaining write-buffer blockers into an explicit
execution-readiness gate, so append execution cannot be treated as
implementation-ready until both source questions are resolved.
ADR-0155 and ADR-0156 make that gate fail closed: blocked readiness must name
all live blockers, and allowed readiness is rejected while unresolved
questions remain.
ADR-0138 adds base and chain language summaries to project status, so the first
diagnostic command covers the object-language surfaces beneath evidence and
frontier reports.
ADR-0141 carries the transition-chain claim validator summary into project
status, so chain claim/proof failures are visible before evidence-bundle
debugging.

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
current transition claims. ADR-0133 adds the first explicit `predicate-result`
certificate rule while keeping AS below the bar for a general theorem prover.
ADR-0134 exposes the transition proof-certificate surface through direct text
and JSON CLI validation.

## P4: Define The First Object Language

Question: What syntax is sufficient for the first AS claims: transition
predicates only, IS(A)-style arithmetic fragments, or both?

Why it matters: AFS-R2 requires explicit syntax classes for terms, formulae,
sentences, proof objects, and substrate claims.

Status: started by ADR-0012. `language/transition_claim_language.json` now
names the first explicit syntax classes for current transition claims, and
`autarkic_systems/object_language.py` validates the current claim/certificate
surface against that language. ADR-0136 exposes that base language/surface
check through direct text and JSON CLI validation. ADR-0137 gives the
transition-chain object language the same direct CLI surface. IS(A), Type NS,
tableaux syntax, and arithmetized proof-code syntax remain open.

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
neighbor routing and self-target non-init commands open at that point.
ADR-0038 adds the corresponding claim/proof surface.
ADR-0039 adds the corresponding schematic-linked trace.
ADR-0040 adds the corresponding rendered SVG view.
ADR-0041 adds the corresponding unsupported completed-buffer boundary claim.
ADR-0042 adds the corresponding schematic-linked trace.
ADR-0043 adds the corresponding rendered SVG view.
ADR-0044 delivers neighbor-target command buffers to output channels, narrowing
the remaining open command-buffer questions to recipient-side consumption and
self-target non-init commands.
ADR-0045 promotes that delivery behavior into the named claim/proof surface.
ADR-0046 adds the corresponding schematic-linked trace for one neighbor B
delivery case.
ADR-0047 adds the rendered SVG view of that trace.
ADR-0048 records the source-status decision for recipient-side command-message
inputs and allows the next executable slice to consume init-family command
messages only.
ADR-0049 implements that recipient init-family command-message consumption
slice while leaving non-init command messages blocked.
ADR-0050 promotes the recipient init-family slice into the named claim/proof
surface.
ADR-0051 adds the corresponding schematic-linked trace.
ADR-0052 adds the corresponding rendered SVG view.
ADR-0053 records the remaining recipient non-init command-message blockers.
ADR-0054 adds the corresponding named rejection-boundary claim.
ADR-0055 adds the corresponding schematic-linked rejection trace.
ADR-0056 adds the corresponding rendered SVG view.
ADR-0057 records the corresponding write-buffer semantics source-status
decision.
ADR-0058 records the corresponding `standard-signal` command-token semantics
source-status decision.
ADR-0062 records the corresponding `guile-asmsim.scm` command-semantics
source-status decision, strengthening the standard-signal/write-buffer blocker.
ADR-0063 records the corresponding `practice/asmsim.scm` process-buffer
source-status decision, again keeping command-token execution source-blocked.
ADR-0064 records the corresponding official TLA source-status decision: the
TLA files are partial, stub, or empty and do not resolve command semantics.
ADR-0065 records the first integrated evidence bundle for a recipient init
transition so the claim/proof/trace/render/source path can be inspected as one
artifact.
ADR-0066 records the registry for those integrated evidence bundles.
ADR-0067 exposes that registry validation as an operator-facing command.
ADR-0068 registers the recipient non-init rejection bundle, so the registry
covers both an executable init slice and a blocked-command rejection boundary.
ADR-0069 registers the multi-command rejection bundle, so the registry also
covers simultaneous command-token conflicts.
ADR-0070 adds a closed-index registry check for unregistered sibling bundle
files.
ADR-0071 adds machine-readable registry validation output.
ADR-0072 registers the direct self-mailbox init transition as an integrated
evidence bundle and claim-aligns the trace/SVG fixture.
ADR-0073 registers the direct unsupported self-mailbox preservation boundary as
an integrated evidence bundle and claim-aligns the trace/SVG fixture.
ADR-0074 registers the completed self-target command-buffer init dispatch as
an integrated evidence bundle.
ADR-0075 registers the completed self-target non-init command-buffer append
boundary as an integrated evidence bundle.
ADR-0076 registers the completed neighbor-target command-buffer delivery path
as an integrated evidence bundle.
ADR-0077 adds the first executable two-step chain from neighbor delivery into
recipient init-family command consumption without adding a scheduler or non-init
command execution.
ADR-0078 promotes that two-step handoff into a named chain claim and
proof-certificate surface while keeping it separate from the single-transition
claim language.
ADR-0079 makes the chain-claim object language explicit without widening it to
a general temporal, scheduling, or graph language.
ADR-0080 exposes chain-claim validation as a direct text/JSON CLI for agents
and automation.
ADR-0081 adds a separate composed-chain evidence bundle under
`evidence/chains/`, tying the chain claim, proof certificate, chain language,
two underlying transition evidence bundles, and source-status blockers into
one directly validated artifact.
ADR-0082 adds a dedicated transition-chain trace for the same handoff, replaying
the sender step, delivered tuple, recipient step, and whole-chain helper.
ADR-0083 renders that trace as an exact-output checked SVG while keeping the
JSON trace as authority.
ADR-0084 adds `evidence/chains/manifest.json` and registry validation for
composed-chain evidence bundles, keeping that index separate from the
single-transition evidence registry.
ADR-0059 records the corresponding multi-command recipient input policy
decision.
ADR-0060 records the corresponding multi-command recipient rejection trace.
ADR-0061 records the corresponding multi-command recipient rejection SVG.
