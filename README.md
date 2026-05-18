# Autarkic Systems

Autarkic Systems is the umbrella project for turning the Autarkic Formal
Systems research program into an organized theory and, where the theory is
ready, executable or simulable artifacts.

The lower-bound objective is an artificial entity that demonstrates cognitive
sovereignty: it should be able to reason about itself, its knowledge, and its
computational substrate without depending on opaque external authority as the
final source of confidence.

## Current Repository State

This repository has moved from its initial scaffolding stage into a narrow
executable evidence stack. The initial upstream commit contained only
`AGENTS.md` and its backup, so the first durable work made the project
legible; current work now layers checked Universal Cell transitions, claims,
proof certificates, object languages, evidence bundles, and status reports:

- `docs/project-charter.md` defines the umbrella project, key terms, and
  near-term research obligations.
- `docs/subordinate-review.md` records the first review of the referenced
  subordinate repositories.
- `docs/glossary.md` defines working project vocabulary.
- `docs/afs-requirements.md` defines the first requirement matrix for
  Autarkic Formal Systems.
- `docs/source-manifest.md` explains the pinned source manifest in
  `sources/manifest.json`.
- `docs/literature-map.md` and `docs/open-problems.md` connect reviewed
  sources to AS claims and next ADRs.
- `docs/proof-apparatus-options.md` records the first proof-apparatus
  direction decision.
- `docs/formal-confidence-target.md` records the first checked
  formal-confidence target boundary, explicitly marking current AS
  self-consistency claims as blocked pending fixed-point self-reference and
  deduction-apparatus work.
- `docs/formal-arithmetic-language.md` records the first checked syntax-only
  Type-NS arithmetic language surface for the formal-confidence path.
- `docs/formal-codebook.md` records the first checked proof-code encoding
  surface over that arithmetic language.
- `docs/formal-substitution.md` records the first checked capture-avoiding
  substitution surface over formal codebook nodes.
- `docs/consistency-level-target.md` records Level-1 consistency as the first
  selected AS formal-confidence target notion.
- `docs/deduction-apparatus-target.md` records the AS-local
  `predicate-result` proof-certificate checker as the current selected
  deduction-apparatus target.
- `docs/transition-claim-language.md` explains the first explicit object
  language for transition claims.
- `docs/transition-chain-claim-language.md` explains the first explicit object
  language for transition-chain claims.
- `docs/willard-definition-map.md` records the first definition-granularity map
  of Willard anchors needed for formal-confidence claims.
- `docs/proflog-frontier-status.md` records why public Proflog main is not a
  dependency-ready AS proof apparatus.
- `docs/prc-hardware-witness-map.md` records the first source-backed
  hardware/schematic evidence path for PRC-derived work.
- `docs/single-node-schematic-trace.md` records the first schematic-linked
  Universal Cell transition trace.
- `docs/single-node-schematic-svg.md` records the first rendered view of that
  structured schematic trace.
- `docs/processor-memory-toggle-trace.md` records the second schematic-linked
  Universal Cell trace, covering processor memory toggle behavior.
- `docs/processor-memory-toggle-svg.md` records the rendered view of that
  processor memory-toggle trace.
- `docs/stem-automail-reconfiguration-trace.md` records the third
  schematic-linked Universal Cell trace, covering one stem automail
  reconfiguration.
- `docs/stem-automail-reconfiguration-svg.md` records the rendered view of that
  stem automail reconfiguration trace.
- `docs/stem-buffer-accumulation.md` records the first standard-signal stem
  buffer accumulation behavior.
- `docs/stem-buffer-claim.md` records the named claim and proof-certificate
  surface for that buffer behavior.
- `docs/stem-buffer-accumulation-trace.md` records the schematic-linked trace
  for one matching stem buffer append.
- `docs/stem-buffer-accumulation-svg.md` records the rendered view of that stem
  buffer append trace.
- `docs/stem-command-buffer-map.md` records the source-backed five-bit stem
  command-buffer decoding map.
- `docs/stem-command-execution-source-status.md` records why full stem command
  execution is still blocked after the decoder map.
- `docs/recipient-command-consumption-source-status.md` records the
  source-backed boundary for recipient-side command-message inputs.
- `docs/recipient-non-init-command-source-status.md` records why non-init
  recipient command-message inputs remain blocked.
- `docs/recipient-non-init-command-rejection-claim.md` records the named claim
  and proof-certificate surface for that rejection boundary.
- `docs/recipient-non-init-command-rejection-trace.md` records the
  schematic-linked trace for one recipient non-init command-message rejection.
- `docs/recipient-non-init-command-rejection-svg.md` records the rendered view
  of that recipient non-init command-message rejection trace.
- `docs/write-buffer-command-semantics-status.md` records why write-buffer
  command execution is now source-resolved and implemented for direct
  self-mailbox, completed self-target command-buffer, and single recipient
  command-message surfaces. It records the narrowed source agreement that
  `write-buf-zero` / `write-buf-one` carry literal `0` / `1` append bits
  rather than high-rail-derived standard-signal values.
- `docs/standard-signal-command-semantics-status.md` records why
  `standard-signal` command-token execution is preserved as unsupported while
  ordinary standard-signal binary input stays implemented, and records the
  formal-model self-mailbox exception that prevents treating stem
  self-mailbox `standard-signal` as ordinary binary input by default. It also
  records that AS resolves the command-table offset question in favor of the
  formal PRC map where `standard-signal` is offset `0`, resolves the recipient
  command-message surface plus the command-token/binary-input equivalence and
  self-target surface questions, and gates future execution changes on new
  source evidence.
- `docs/standard-signal-source-review-status.md` records the ADR-0171
  source-head review snapshot that found no new `standard-signal`
  command-token execution evidence and converts the active review slice into a
  `no-` prefixed guard.
- `docs/guile-asmsim-command-semantics-status.md` records why the
  `guile-asmsim.scm` command witness strengthens the standard-signal and
  write-buffer blocker rather than resolving it.
- `docs/asmsim-process-buffer-status.md` records why the newer
  `practice/asmsim.scm` process-buffer witness is still source-blocked by
  incomplete message-code documentation.
- `docs/official-tla-universal-cell-status.md` records why the official PRC
  TLA files are partial/stub/empty and not executable UC authority.
- `docs/multi-command-recipient-input-policy-status.md` records the
  reject-and-clear policy for multiple simultaneous recipient command-message
  inputs.
- `docs/multi-command-recipient-rejection-trace.md` records the
  schematic-linked trace for one direct multi-command recipient rejection.
- `docs/multi-command-recipient-rejection-svg.md` records the rendered view of
  that multi-command recipient rejection trace.
- `docs/recipient-init-command-message-consumption.md` records the first
  executable recipient-side init-family command-message input slice.
- `docs/recipient-init-command-message-claim.md` records the named claim and
  proof-certificate surface for that recipient init command-message slice.
- `docs/recipient-init-command-message-trace.md` records the schematic-linked
  trace for one recipient init command-message transition.
- `docs/recipient-init-command-message-svg.md` records the rendered view of
  that recipient init command-message trace.
- `docs/recipient-init-transition-evidence-bundle.md` records the first
  integrated evidence bundle tying one recipient init transition to its claim,
  proof certificate, schematic trace, SVG render, and source-status boundaries.
- `docs/recipient-non-init-evidence-bundle.md` records the second integrated
  evidence bundle, tying one recipient non-init rejection boundary to the same
  cross-layer evidence surface.
- `docs/multi-command-rejection-evidence-bundle.md` records the third
  integrated evidence bundle, tying one simultaneous command-message rejection
  boundary to that evidence surface.
- `docs/self-mailbox-init-evidence-bundle.md` records the fourth integrated
  evidence bundle, tying one direct self-mailbox init transition to that
  evidence surface.
- `docs/self-mailbox-unsupported-evidence-bundle.md` records the fifth
  integrated evidence bundle, tying one direct unsupported self-mailbox
  preservation boundary to that evidence surface while naming all covered
  positive unsupported self-mailbox examples.
- `docs/self-mailbox-write-buffer-evidence-bundle.md` records the integrated
  evidence bundle for direct self-mailbox write-buffer append execution,
  covering both positive write-buffer command examples while tracing
  `write-buf-one`.
- `docs/recipient-write-buffer-command-message-trace.md` records the
  schematic-linked trace for one recipient write-buffer command-message append
  transition.
- `docs/recipient-write-buffer-command-message-svg.md` records the rendered
  view of that recipient write-buffer command-message trace.
- `docs/recipient-write-buffer-command-evidence-bundle.md` records the
  integrated evidence bundle for recipient write-buffer command-message append
  execution, covering both positive recipient write-buffer command examples
  while tracing upstream `write-buf-zero`.
- `docs/self-command-buffer-init-evidence-bundle.md` records the integrated
  evidence bundle tying one completed self-target command-buffer
  init dispatch to that evidence surface.
- `docs/command-buffer-unsupported-evidence-bundle.md` records the integrated
  evidence bundle tying one completed self-target non-init
  command-buffer append boundary to that evidence surface while naming all
  covered positive self-target non-init command-buffer examples.
- `docs/self-command-buffer-write-buffer-evidence-bundle.md` records the
  integrated evidence bundle for completed self-target command-buffer
  write-buffer append execution, covering both positive self-target
  write-buffer command examples while tracing `write-buf-one`.
- `docs/neighbor-command-buffer-delivery-evidence-bundle.md` records an
  integrated evidence bundle, tying one completed neighbor-target
  command-buffer delivery to that evidence surface.
- `docs/neighbor-delivery-recipient-chain.md` records the first executable
  two-step handoff from neighbor command-buffer delivery into recipient
  init-family command consumption.
- `docs/neighbor-delivery-chain-trace.md` records the composed-chain traces
  for the consumed init handoff and rejected non-init handoff.
- `docs/neighbor-delivery-chain-svg.md` records the rendered SVG views of the
  consumed and rejected composed-chain traces.
- `docs/neighbor-delivery-chain-claim.md` records the named consumed and
  rejected claim/proof-certificate surface for that two-step handoff,
  including delivered `write-buf-zero` and `write-buf-one` rejection examples.
- `docs/transition-chain-claim-language.md` records the syntax classes and
  validator boundary for transition-chain claims.
- `docs/neighbor-delivery-chain-evidence-bundle.md` records the first
  transition-chain evidence bundle, tying the two-step handoff to its claim,
  proof, language, underlying transition bundles, and source-status boundaries.
- `docs/chain-evidence-bundle-registry.md` records the registry for
  discovering and batch-validating transition-chain evidence bundles.
- `docs/vertical-chain-demo-report.md` records the compact first-run report
  over one checked transition-chain evidence path or the whole chain evidence
  registry.
- `docs/project-status-report.md` records the operator-facing status report
  over transition evidence, chain evidence, network-sequence evidence, and the
  blocked command-token frontier.
- `docs/source-status-frontier.md` records the focused source-status frontier
  command for inspecting blocked command-token semantics without the full
  project status surface.
- `docs/evidence-bundle-registry.md` records the registry for discovering and
  batch-validating transition evidence bundles.
- `python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json`
  validates the evidence bundle registry from the command line, including
  closed-index checks for unregistered sibling bundle files.
- `python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json --format json`
  emits the same registry validation as machine-readable JSON, including the
  registered transition bundle IDs, paths, claim IDs, expected statuses, and
  positive and covered examples, plus compact registry-level and per-bundle
  failed-subject summaries.
- `docs/self-mailbox-init-claim.md` records the named claim and
  proof-certificate surface for the self-mailbox init-command subset.
- `docs/self-mailbox-unsupported-claim.md` records the named preservation
  claim for unresolved self-mailbox commands, with positive claim/proof
  examples for `standard-signal`, `write-buf-zero`, and `write-buf-one`.
- `docs/self-mailbox-init-trace.md` records the schematic-linked trace for one
  self-mailbox init command.
- `docs/self-mailbox-unsupported-trace.md` records the schematic-linked trace
  for one unsupported self-mailbox command.
- `docs/self-mailbox-write-buffer-trace.md` records the schematic-linked trace
  for one direct self-mailbox write-buffer append command.
- `docs/self-mailbox-init-svg.md` records the rendered view of that
  self-mailbox init trace.
- `docs/self-mailbox-unsupported-svg.md` records the rendered view of the
  unsupported self-mailbox trace.
- `docs/self-mailbox-write-buffer-svg.md` records the rendered view of the
  direct self-mailbox write-buffer trace.
- `docs/self-command-buffer-init-dispatch.md` records the first narrow
  command-buffer-to-behavior slice for self-target init commands.
- `docs/self-command-buffer-init-claim.md` records the named claim and
  proof-certificate surface for that command-buffer slice.
- `docs/command-buffer-unsupported-claim.md` records the named append-boundary
  claim for unsupported completed command buffers, with positive claim/proof
  examples for self `standard-signal`, self `write-buf-zero`, and self
  `write-buf-one`.
- `docs/neighbor-command-buffer-delivery-claim.md` records the named claim and
  proof-certificate surface for neighbor command-buffer delivery.
- `docs/self-command-buffer-init-trace.md` records the schematic-linked trace
  for one self-target command-buffer init dispatch.
- `docs/neighbor-command-buffer-delivery-trace.md` records the
  schematic-linked trace for one neighbor command-buffer delivery.
- `docs/neighbor-command-buffer-delivery-svg.md` records the rendered view of
  that neighbor command-buffer delivery trace.
- `docs/command-buffer-unsupported-trace.md` records the schematic-linked trace
  for one unsupported completed command buffer.
- `docs/self-command-buffer-write-buffer-trace.md` records the
  schematic-linked trace for one completed self-target command-buffer
  write-buffer command.
- `docs/command-buffer-unsupported-svg.md` records the rendered view of that
  unsupported command-buffer trace.
- `docs/self-command-buffer-init-svg.md` records the rendered view of that
  self command-buffer trace.
- `docs/self-command-buffer-write-buffer-svg.md` records the rendered view of
  that self command-buffer write-buffer trace.
- `autarkic_systems/universal_cell.py` now exposes explicit `self_mailbox`
  state for future self-target command execution.
- Universal Cell channel tuples can represent command-message tokens, and
  recipient-side init-family command-message inputs are now executable.
- `step_stem_cell` processes the self-mailbox init-family commands while
  leaving full command-buffer execution open.
- `step_stem_cell` also dispatches a just-completed self-target init-family
  command buffer and delivers just-completed neighbor-target command buffers to
  output channels. Recipient cells now consume init-family command-message
  inputs, while non-init recipient commands and self non-init command semantics
  remain open.
- `step_stem_cell` now executes direct self-mailbox and completed self-target
  command-buffer write-buffer commands, and recipient cells now execute single
  delivered write-buffer command messages. The transition evidence registry
  includes the two ADR-0162 self-target write-buffer execution bundles and
  the ADR-0170 recipient write-buffer command-message evidence bundle.
- `autarkic_systems/transition_chains.py` composes one neighbor delivery step
  with one recipient step, proving the delivered init-family token can be
  consumed without adding a general multi-cell simulator.
- `autarkic_systems/network_witness.py` records the same bounded two-cell
  neighbor-delivery execution as an inspectable network-shaped witness with
  sender state, recipient state, delivered tuple, event trail, and text/JSON
  CLI output.
- `autarkic_systems/network_sequence.py` records a bounded post-handoff
  witness showing that a delivered init command has a later recipient behavior:
  `proc-l-init` reconfigures the recipient to `proc/left`, after which a binary
  follow-up signal routes through the existing fixed-cell logic.
- `autarkic_systems/network_sequence_trace.py` validates the checked
  post-handoff sequence trace artifact, replaying the accepted delivery and
  follow-up path through the existing sequence helper.
- `autarkic_systems/network_sequence_svg.py` validates the rendered SVG view
  of that post-handoff sequence trace against the deterministic renderer.
- `autarkic_systems/network_sequence_claims.py` validates the first named claim
  and predicate-result proof certificate over that post-handoff signal witness.
- `autarkic_systems/network_sequence_object_language.py` validates the first
  network-sequence claim object language and checked sequence claim/proof
  surface.
- `autarkic_systems/network_sequence_evidence_bundle.py` validates the first
  evidence bundle and registry over the post-handoff signal witness claim,
  proof, object language, executable witness, checked trace, checked SVG,
  underlying delivery chain evidence, and source-status boundaries.
- `autarkic_systems/network_sequence_demo.py` renders a vertical first-run
  report over the post-handoff sequence evidence bundle or registry, including
  validation results, artifact presence, checked trace/SVG, lower-level chain
  bundles, source-status boundaries, and explicit boundary terms.
- `autarkic_systems/chain_trace.py` validates the recorded transition-chain
  traces for consumed and rejected neighbor-delivery handoffs.
- `autarkic_systems/chain_svg.py` renders and validates transition-chain SVG
  views for consumed and rejected neighbor-delivery handoffs.
- `autarkic_systems/chain_claims.py` validates the transition-chain claim
  manifest and predicate-result proof certificates, and exposes
  `python -m autarkic_systems.chain_claims` for direct chain-claim validation.
- `autarkic_systems/chain_object_language.py` validates the first
  transition-chain claim language and checked chain claim surface, and exposes
  `python -m autarkic_systems.chain_object_language` for direct chain
  object-language validation.
- `autarkic_systems/chain_evidence_bundle.py` validates the first
  transition-chain evidence bundle and exposes
  `python -m autarkic_systems.chain_evidence_bundle` for direct text/JSON
  validation of one bundle or a chain registry.
- `autarkic_systems/chain_demo.py` renders vertical chain demo reports,
  reusing the chain evidence validator while summarizing one bundle or every
  registered chain bundle with its claim, executable chain, trace, SVG,
  lower-level evidence bundles, source-status boundaries, artifact-presence
  summary, and validation result.
- `autarkic_systems/project_status.py` renders one operator-facing report over
  the transition evidence registry, chain evidence registry, network-sequence
  evidence registry, base claim/proof/language surfaces, transition-chain
  claim/language surfaces, network-sequence claim/proof surface, and the
  checked proof-rule audit, plus the checked formal-confidence target boundary
  and live source-status frontier for blocked command-token semantics and their
  resolution-question IDs.
- `autarkic_systems/vertical_demo.py` renders a first-run vertical demo digest
  over the accepted stack: current demonstration, evidence counts,
  claim/proof counts, proof-rule mix, blocked command frontier, canonical
  registries, the checked network-sequence evidence bundle, and the concrete
  evidence trail from claim/proof/language artifacts through witness, trace,
  SVG, underlying chain bundle, and source-status records. It also surfaces
  the exact reproduction commands for the vertical demo, focused
  network-sequence JSON, compact project status, and refreshed handoff.
- `autarkic_systems/github_submission.py` renders local git evidence for the
  current GitHub submission path: current branch, `HEAD`, origin/fork remote
  URLs, fork `main` match state, origin `main` divergence, and the upstream
  tracking issue. It also renders a direct fork commit URL for the submitted
  `HEAD`, a fork `main` browser URL, a fork-hosted compare URL from
  `origin/main` to `HEAD`, and an origin `main` browser URL, normalizing common
  HTTPS and SSH GitHub remotes to web URLs.
- `autarkic_systems/handoff.py` composes the compact project status, vertical
  demo digest, and local GitHub submission status into one end-of-month
  handoff report.
- `autarkic_systems/formal_arithmetic.py` validates the first syntax-only
  formal arithmetic language manifest against the Willard definition map,
  checking the Type-NS profile, `delta0` bounded formula class, `pi1`/`sigma1`
  sentence classes, and placeholder-only proof-object boundary.
- `autarkic_systems/formal_code.py` validates and runs the first formal
  proof-code codebook, encoding and decoding tagged natural-number prefix
  sequences for terms, formulae, `pi1`/`sigma1` sentence wrappers, and
  placeholder proof-line shells.
- `autarkic_systems/formal_substitution.py` validates and runs the first
  capture-avoiding free-variable substitution surface over the formal codebook
  nodes, including binder-respecting and capture-rejection examples.
- `autarkic_systems/consistency_level.py` validates the first consistency-level
  target selection, tying Level-1 consistency to the checked arithmetic
  language, codebook, and substitution surface without claiming a proof.
- `autarkic_systems/formal_confidence.py` validates the first
  formal-confidence target manifest against the Willard definition map, keeping
  the current AS self-consistency claim explicitly blocked until fixed-point
  self-reference and deduction-apparatus choices exist.
- `claims/transition_claims.json` names the current executable transition
  claims and examples, including the self-mailbox init-command execution
  subset, unsupported-command preservation boundary, self-target command-buffer
  init dispatch, neighbor-target command-buffer delivery, recipient
  init-family command-message consumption, recipient non-init command-message
  rejection, and the self-target non-init completed-buffer append boundary.
- `python -m autarkic_systems.claim_manifest` validates those transition claim
  examples in text or JSON form.
- `claims/proof_certificates.json` adds the first tiny proof certificates over
  those transition claims, using explicit `predicate-result` steps for
  fixed-output preservation, consumed-input clearing, fixed-role memory
  behavior, stem-init reset behavior, and stem
  automail reconfiguration, buffer accumulation, and self-mailbox init command
  execution, unsupported-command preservation, and direct self-mailbox
  write-buffer append execution, plus completed self-target command-buffer init
  dispatch, unsupported-preservation, write-buffer append, and neighbor-target
  delivery boundaries, plus recipient init and write-buffer command-message
  processing and recipient non-init rejection, that name the evaluated
  predicates directly. The transition proof-certificate manifest no longer uses
  `manifest-example` rules.
- `python -m autarkic_systems.proof_certificates` validates the transition
  proof-certificate surface in text or JSON form.
- `python -m autarkic_systems.object_language` validates the transition claim
  language manifest and the checked claim/proof surface in text or JSON form.
- `claims/formal_confidence_targets.json` records
  `AS-FORMAL-CONFIDENCE-TARGET-001`, a blocked Willard-style
  formal-confidence target over the current AS proof/evidence surface and the
  first checked syntax-only arithmetic language, proof-code, substitution, and
  consistency-level and deduction-apparatus target artifacts.
- `python -m autarkic_systems.formal_arithmetic --format json` validates
  `language/formal_arithmetic_language.json`, including required Willard
  anchors, the Type-NS profile, `delta0`, `pi1`, `sigma1`, and the
  placeholder-only proof-object boundary.
- `python -m autarkic_systems.formal_code --format json` validates
  `language/formal_codebook.json`, including required Willard anchors, unique
  tag codes, manifest examples, and encode/decode round trips.
- `python -m autarkic_systems.formal_substitution --format json` validates
  `language/formal_substitution_examples.json`, including free-variable
  substitution examples, capture rejection, and expected encoded outputs.
- `python -m autarkic_systems.consistency_level --format json` validates
  `claims/consistency_level_targets.json`, including the Level-1 target,
  `pi1`/`sigma1` sentence classes, and non-claim status.
- `python -m autarkic_systems.deduction_apparatus --format json` validates
  `claims/deduction_apparatus_targets.json`, including the selected
  AS-local `predicate-result` proof-certificate checker and 52 checked
  certificate steps across the transition, transition-chain, and
  network-sequence surfaces.
- `python -m autarkic_systems.formal_confidence --format json` validates that
  target against `sources/willard_definition_map.json`, including required
  Willard anchors, required configuration fields, explicit blockers, and the
  next AS action.
- `claims/transition_chain_claims.json` names the executable two-step
  transition-chain claims for consumed init/write-buffer delivery and rejected
  standard-signal delivery.
- `claims/transition_chain_proof_certificates.json` adds matching
  predicate-result proof certificates for those chain claims.
- `language/transition_chain_claim_language.json` names the first explicit
  syntax classes for transition-chain claims, including chain proof-object
  `manifest-example` and `predicate-result` rules.
- `python -m autarkic_systems.chain_claims --format json` emits the
  transition-chain claim validation report as machine-readable JSON.
- `python -m autarkic_systems.chain_evidence_bundle --format json` emits the
  neighbor-delivery chain evidence-bundle validation report as
  machine-readable JSON.
- `python -m autarkic_systems.chain_evidence_bundle --registry evidence/chains/manifest.json --format json`
  emits the transition-chain evidence registry validation report as
  machine-readable JSON, including per-bundle failed subjects when a registered
  existing chain bundle rejects.
- `python -m autarkic_systems.chain_demo` emits the default transition-chain
  demo report in text form; `--registry evidence/chains/manifest.json` emits
  one report over every registered chain bundle, and `--format json` emits the
  same claim-to-evidence surfaces for automation, including artifact presence
  and missing-path summaries.
- `python -m autarkic_systems.network_witness --format json` emits the bounded
  two-cell neighbor-delivery witness as machine-readable JSON, including sender
  and recipient before/after state, delivered tuple, and ordered events.
- `python -m autarkic_systems.network_sequence --format json` emits the
  post-handoff signal witness as machine-readable JSON, including the
  underlying delivery witness, follow-up input, follow-up status, and recipient
  before/after follow-up state.
- `python -m autarkic_systems.network_sequence_claims --format json` validates
  the post-handoff signal claim and proof-certificate surface as
  machine-readable JSON.
- `python -m autarkic_systems.network_sequence_object_language --format json`
  validates the post-handoff network-sequence claim object language and checked
  claim/proof surface as machine-readable JSON.
- `python -m autarkic_systems.network_sequence_evidence_bundle --registry evidence/sequences/manifest.json --format json`
  validates the post-handoff network-sequence evidence-bundle registry as
  machine-readable JSON, including per-bundle failed subjects when a registered
  existing bundle rejects.
- `python -m autarkic_systems.network_sequence_demo --registry evidence/sequences/manifest.json --format json`
  renders the post-handoff network-sequence claim-to-evidence demo registry as
  machine-readable JSON, including per-bundle failed subjects when a registered
  existing bundle rejects.
- `python -m autarkic_systems.project_status --format summary` emits a compact
  operator digest over the accepted state, evidence counts, claim
  counts, proof-rule audit, formal-confidence target status mix, blocked
  commands, and safe next slice.
- `python -m autarkic_systems.github_submission` emits a local text/JSON
  submission-status report showing whether the current `HEAD` is visible on
  fork `main`, the fork commit URL for that `HEAD`, the fork `main` browser
  URL, the fork-hosted compare URL from `origin/main` to `HEAD`, the upstream
  origin `main` browser URL, how far local `HEAD` is ahead of upstream
  `origin/main`, and where upstream submission notes are tracked. The browser
  URLs are normalized from common GitHub HTTPS and SSH remote forms. It also
  reports local
  `fork/main` remote-tracking ref freshness from the git reflog so operators
  can see how recent the submission evidence is. `--refresh-remotes` fetches
  fork `main` and origin `main` into the inspected remote-tracking refs before
  reporting.
- `python -m autarkic_systems.handoff` emits a local text/JSON handoff report
  that combines accepted project status, the vertical demo digest, and GitHub
  submission evidence; it also accepts `--refresh-remotes` for a refreshed
  pre-handoff check.
- `python -m autarkic_systems.vertical_demo` emits a compact first-run digest
  for the current accepted demonstration, including the evidence trail and
  reproduction commands; `--format json` emits the same digest for automation.
- `python -m autarkic_systems.project_status --format json` emits the current
  project status as schema-versioned machine-readable JSON: transition
  evidence accepted with 11 bundles, chain evidence accepted with 2 bundles,
  network-sequence evidence accepted with 1 bundle,
  transition claim examples accepted with 16 claims and 40 matched examples,
  transition proof certificates accepted with 16 claims and 16 certificates,
  transition-chain claims accepted with 2 claims, 9 examples, and 2
  certificates, network-sequence claims accepted with 1 claim and 1
  certificate, a proof-rule audit showing 52 checked `predicate-result` steps
  and 0 checked `manifest-example` steps,
  formal-confidence targets accepted with 1 blocked target,
  transition language accepted with 16 claims and 16 certificates, chain
  language accepted with 2 claims and 2 certificates, network-sequence language
  accepted with 1 claim and 1 certificate, concrete transition, chain, and
  network-sequence registry bundle entries, sequence evidence bundle failed
  subjects when present, and the current blocked
  `standard-signal`
  command-token frontier. The default text report also names the concrete
  transition, chain, and network-sequence evidence bundle IDs and paths,
  transition bundle positive and covered examples, claim/proof and language
  failed subjects when present, the
  standard-signal blocked runtime surfaces, source-status AS boundaries,
  execution-readiness gates, the resolution-question IDs and
  summaries that define the next source-backed decision work, the source
  evidence explaining why unresolved questions remain blocked, resolved
  question decisions that should not be reopened without new evidence, latest
  source-review gates for records that name one, and the source-status
  cross-links behind the blocked frontier. Schema version `2`
  attributes
  blocked commands to each
  accepted source-status entry, schema version `3` carries the source-status
  resolution-question IDs that still block command-token execution and rejects
  malformed resolution-question metadata, schema version `4` adds
  summary-bearing `resolution_questions` objects, schema version `5` adds
  checked `blocked_runtime_surfaces` lists, and schema version `6` adds
  registry `bundles` arrays to the transition and chain evidence summaries.
  Schema version `7` adds `positive_example` and
  `covered_positive_examples` to transition evidence bundle entries; the
  default text report renders those fields when present. Schema version `8`
  adds `additional_source_statuses` cross-links to accepted source-status
  entries so automation can inspect the source-review trail behind the
  blocked frontier; the default text report renders those cross-links when
  present. Schema version `9` adds `resolved_resolution_questions` to accepted
  source-status entries and renders a `Resolved resolution questions:` text
  section. Schema version `10` carries optional resolved-question detail fields
  such as formal command offset and legacy divergence into JSON/text. Schema
  version `11` adds transition and chain language summaries to JSON/text.
  Schema version `12` adds base transition claim and proof-certificate
  summaries to JSON/text. Schema version `13` adds the transition-chain claim
  summary to JSON/text. Schema version `14` adds
  `resolution_question_evidence` to accepted source-status entries and renders
  a `Resolution question evidence:` text section. Schema version `15` adds
  `execution_readiness` gates to accepted source-status entries and renders an
  `Execution readiness:` text section. Completed safe-next items whose
  source-status strings begin with `no-` are treated as guards rather than
  active aggregate next slices, so the current report renders `Safe next
  slice: none` while `standard-signal` remains blocked. Schema version `16`
  adds the proof-rule audit to JSON/text so the checked transition and chain
  proof-certificate rule mix is visible from project status. The summary output
  format preserves schema version `16` while rendering the same payload as a
  compact operator digest. Schema version `17` adds `sequence_evidence` from
  the network-sequence evidence registry, includes it in aggregate acceptance,
  renders it in text and summary output, and adds `--sequence-registry`.
  Schema version `18` adds `sequence_claims` from the network-sequence
  claim/proof surface, includes sequence certificates in the proof-rule audit,
  renders sequence claim counts in text and summary output, and adds
  `--sequence-claims` / `--sequence-certificates`.
  Schema version `19` adds `sequence_language` from the network-sequence
  object-language surface, includes it in aggregate acceptance, renders it in
  text output, and adds `--sequence-language`. Schema version `20` adds
  `sequence_evidence.bundle_failed_subjects`, preserving inner
  network-sequence evidence bundle failure subjects such as `sequence-trace`
  or `sequence-svg` when a registry bundle rejects. Schema version `21` adds
  `latest_source_review` to accepted source-status frontier entries, validates
  the linked review artifact, and renders a `Latest source reviews:` text
  section. Schema version `22` adds `formal_confidence` from the checked
  formal-confidence target manifest, includes it in aggregate acceptance,
  renders formal-confidence status and failures in text and summary output,
  and adds `--formal-confidence-targets` / `--willard-map`.
  Missing registries report
  `registry-file`, malformed registries report `registry-json`, and
  source-status path problems are summarized in `frontier.failed_subjects` as
  `source-status-file`, `source-status-json`, or `source-status-schema`;
  source-status records must also expose at least one blocked command token
  through `command`, `commands`, or `blocked_runtime_commands`, and blank
  command-token strings are rejected as schema failures. Source-status
  `decision` and `safe_next_slice` text must also be non-whitespace, and
  recognized command-token fields, source-status cross-links, and resolved
  question source paths must have the expected text/list/object shapes.
  Source-status `resolution_question_evidence` IDs must match unresolved
  `required_resolution_questions` IDs in the same source-status record.
  When a source-status record has unresolved `required_resolution_questions`,
  `resolution_question_evidence` must cover every unresolved question ID.
  Unresolved and resolved source-status question IDs must each be unique inside
  a single source-status record, so set-based coverage checks cannot hide
  duplicate blockers or duplicate settled decisions.
  When a source-status record declares `execution_readiness.decision` as
  `blocked`, its `blocked_by_resolution_questions` list must also cover every
  unresolved question ID. A source-status record also cannot set
  `execution_change_allowed` to `true` while unresolved
  `required_resolution_questions` remain, or while `execution_readiness.decision`
  is `blocked`.
  Source-status cross-link paths and resolved question source paths must also
  point to existing files that contain JSON objects.
  Accepted source-status records must also provide non-empty top-level
  `as_boundary` text so the JSON frontier explains the AS boundary it is
  enforcing.
- `python -m autarkic_systems.source_status --format json` emits a focused
  source-status frontier report as schema-versioned machine-readable JSON:
  accepted/rejected state, failed subjects, blocked command tokens,
  per-source decisions, blocked runtime surfaces, AS boundaries, unresolved
  questions, source evidence for those questions, resolved decisions,
  execution-readiness gates, latest source-review gates, source-status
  cross-links, missing/invalid source-status paths, and the safe next slice.
  The shared validator rejects
  frontier records whose question IDs are simultaneously unresolved and
  resolved, and rejects execution-readiness blockers that do not match live
  unresolved questions or only partially cover them. It also rejects readiness
  records that allow execution changes while unresolved questions remain or
  while the readiness decision is `blocked`, and rejects
  `latest_source_review` links that are missing, malformed, or disagree with
  their linked review artifact. Text mode renders the same frontier for
  operator diagnosis.
- `sources/willard_definition_map.json` makes the Willard anchor map
  machine-checkable.
- `sources/proflog_frontier_status.json` makes the Proflog source-status
  decision machine-checkable.
- `sources/prc_hardware_witness_map.json` makes the PRC hardware/schematic
  witness map machine-checkable.
- `sources/stem_command_buffer_map.json` makes the PRC stem command-buffer
  target/command map machine-checkable.
- `sources/stem_command_execution_source_status.json` makes the stem command
  execution source-status decision machine-checkable.
- `sources/recipient_command_consumption_source_status.json` makes the
  recipient command-consumption source-status decision machine-checkable.
- `sources/recipient_non_init_command_source_status.json` makes the recipient
  non-init command-message blocking decision machine-checkable.
- `sources/write_buffer_command_semantics_status.json` makes the write-buffer
  command semantics source-status decision machine-checkable, including the
  literal command bit-source evidence and the resolved standard-signal
  interaction, recipient-surface, and self-target-surface questions, plus the
  resolved full-buffer and post-append clearing boundaries. Its
  execution-readiness gate now marks direct self-mailbox, completed
  self-target command-buffer, and single recipient command-message append
  execution implemented.
- `sources/standard_signal_command_semantics_status.json` makes the
  `standard-signal` command-token semantics source-status decision
  machine-checkable, including the formal-model self-mailbox exception and the
  resolved command-table offset, self-mailbox equivalence, recipient
  command-message surface, command-token/binary-input, and self-target surface
  decisions. Its execution-readiness gate preserves the existing unsupported
  self-target command boundaries and forbids execution changes without new
  source evidence.
- `sources/standard_signal_source_review_status.json` makes the ADR-0171
  standard-signal source-review snapshot machine-checkable.
- `sources/guile_asmsim_command_semantics_status.json` makes the
  `guile-asmsim.scm` command-semantics source-status decision
  machine-checkable.
- `sources/asmsim_process_buffer_status.json` makes the newer ASMSIM
  process-buffer source-status decision machine-checkable.
- `sources/official_tla_universal_cell_status.json` makes the official TLA
  Universal Cell source-status decision machine-checkable.
- `sources/multi_command_recipient_input_policy_status.json` makes the
  multi-command recipient input policy decision machine-checkable.
- `evidence/recipient_init_command_message_bundle.json` makes one
  recipient-init transition evidence path inspectable across runtime, claim,
  proof, schematic, render, and source-status layers.
- `evidence/recipient_non_init_command_rejection_bundle.json` makes one
  recipient non-init rejection evidence path inspectable across the same
  layers.
- `evidence/multi_command_recipient_rejection_bundle.json` makes one
  multi-command rejection evidence path inspectable across the same layers.
- `evidence/self_mailbox_init_bundle.json` makes one direct self-mailbox init
  evidence path inspectable across the same layers.
- `evidence/self_mailbox_unsupported_bundle.json` makes one direct unsupported
  self-mailbox preservation evidence path inspectable across the same layers.
- `evidence/self_command_buffer_init_bundle.json` makes one completed
  self-target command-buffer init evidence path inspectable across the same
  layers.
- `evidence/command_buffer_unsupported_bundle.json` makes one completed
  self-target non-init command-buffer append-boundary evidence path
  inspectable across the same layers.
- `evidence/neighbor_command_buffer_delivery_bundle.json` makes one completed
  neighbor-target command-buffer delivery evidence path inspectable across the
  same layers.
- `evidence/chains/neighbor_delivery_chain_bundle.json` makes the two-step
  neighbor-delivery recipient-consumption chain inspectable across its claim,
  proof, language, chain trace, chain SVG, underlying transition bundles, and
  source-status layers.
- `evidence/chains/neighbor_delivery_rejection_chain_bundle.json` makes the
  delivered non-init recipient rejection chain inspectable across the same
  layers.
- `evidence/chains/manifest.json` indexes transition-chain evidence bundles
  for batch-validation.
- `evidence/manifest.json` indexes transition evidence bundles for
  batch-validation.
- `schematics/chains/neighbor_delivery_recipient_chain_trace.json` records the
  sender step, handoff tuple, recipient step, and whole-chain status for the
  neighbor-delivery recipient-consumption chain.
- `schematics/chains/neighbor_delivery_recipient_chain_trace.svg` renders that
  two-step chain trace as a checked SVG.
- `schematics/single_node_triangular_rlem_trace.json` makes the first
  schematic-linked transition trace machine-checkable.
- `schematics/single_node_triangular_rlem_trace.svg` is the generated rendered
  view checked against the JSON trace.
- `schematics/processor_memory_toggle_trace.json` makes the processor
  memory-toggle schematic trace machine-checkable.
- `schematics/processor_memory_toggle_trace.svg` is the generated rendered
  view checked against the processor JSON trace.
- `schematics/stem_automail_reconfiguration_trace.json` makes the stem
  automail reconfiguration schematic trace machine-checkable.
- `schematics/stem_automail_reconfiguration_trace.svg` is the generated
  rendered view checked against the stem JSON trace.
- `schematics/stem_buffer_accumulation_trace.json` makes the stem buffer
  accumulation schematic trace machine-checkable.
- `schematics/stem_buffer_accumulation_trace.svg` is the generated rendered
  view checked against the stem buffer JSON trace.
- `schematics/self_mailbox_init_trace.json` makes the self-mailbox init-command
  schematic trace machine-checkable.
- `schematics/self_mailbox_init_trace.svg` is the generated rendered view
  checked against the self-mailbox JSON trace.
- `schematics/self_mailbox_unsupported_trace.json` makes the unsupported
  self-mailbox preservation trace machine-checkable.
- `schematics/self_mailbox_unsupported_trace.svg` is the generated rendered
  view checked against the unsupported self-mailbox JSON trace.
- `schematics/self_command_buffer_init_trace.json` makes the self-target
  command-buffer init dispatch trace machine-checkable.
- `schematics/self_command_buffer_init_trace.svg` is the generated rendered
  view checked against the command-buffer JSON trace.
- `schematics/command_buffer_unsupported_trace.json` makes the unsupported
  completed command-buffer append-boundary trace machine-checkable.
- `schematics/command_buffer_unsupported_trace.svg` is the generated rendered
  view checked against the unsupported command-buffer JSON trace.
- `schematics/neighbor_command_buffer_delivery_trace.json` makes the neighbor
  command-buffer delivery trace machine-checkable.
- `schematics/neighbor_command_buffer_delivery_trace.svg` is the generated
  rendered view checked against the neighbor-delivery JSON trace.
- `schematics/recipient_init_command_message_trace.json` makes the recipient
  init command-message trace machine-checkable.
- `schematics/recipient_init_command_message_trace.svg` is the generated
  rendered view checked against the recipient JSON trace.
- `schematics/recipient_non_init_command_rejection_trace.json` makes the
  recipient non-init command-message rejection trace machine-checkable.
- `schematics/recipient_non_init_command_rejection_trace.svg` is the generated
  rendered view checked against the recipient rejection JSON trace.
- `schematics/multi_command_recipient_rejection_trace.json` makes the
  multi-command recipient rejection trace machine-checkable.
- `schematics/multi_command_recipient_rejection_trace.svg` is the generated
  rendered view checked against the multi-command rejection JSON trace.
- `docs/roadmap.md` maps the first sequence of ADR-scoped work.
- `docs/adr/` holds Architecture Decision Records and their after-action
  follow-ups.
- `LOG.md` is the chronological development spine.
- `MEMORY.md` preserves the few facts that should remain present in future
  working context.
- `LESSONS.md` records durable lessons learned while working this project.

## Fast Verification

```sh
python -m unittest discover
```

The current executable probes live in `autarkic_systems/universal_cell.py` and
`autarkic_systems/transition_predicates.py`, with claim-manifest,
proof-certificate, and object-language support in
`autarkic_systems/claim_manifest.py`, `autarkic_systems/proof_certificates.py`,
`autarkic_systems/object_language.py`, and
`autarkic_systems/willard_map.py`. Source-backed structured maps also live in
`autarkic_systems/prc_hardware_map.py` and
`autarkic_systems/stem_command_map.py`, with schematic-linked trace support in
`autarkic_systems/schematic_trace.py` and generated SVG support in
`autarkic_systems/schematic_svg.py`. They are covered by `tests/`.

## Subordinate Programs

Autarkic Systems currently subsumes three named programs:

- Autarkic Formal Systems (`jpt4/afs`): the immediate formal-systems layer.
  At the reviewed snapshot it is only a placeholder README, so this repository
  must supply the first serious integration structure.
- Pervasively Reconfigurable Computing (`jpt4/prc`): the embodied computing
  substrate. It studies Universal Cells, geometrically explicit logic circuits,
  reversible logic elements with memory, explicit routing, and physically
  grounded reconfiguration.
- Self-Justifying Axiom Systems (`jpt4/sjas`): the formal-confidence substrate.
  It studies Willard-style self-justifying axiom systems, self-provability of
  consistency under tuned expressivity, and executable fragments in Racket,
  Clojure/core.logic, and Proflog-adjacent work.

## Development Discipline

Follow `AGENTS.md` before changing this repository. In brief:

- ADRs precede feature implementation.
- Tests precede code when code is added.
- Documentation belongs in the right layer: `LOG.md` for chronology,
  `MEMORY.md` for high-priority future context, `LESSONS.md` for durable
  lessons, and README files for current entrypoints.
- Branches should follow the ADR structure of the work.

The default branch is currently `main`, even though `AGENTS.md` refers to
`master` in its generic branch-discipline text. Until the repository owner
changes the remote default branch, use `main` as the integration branch while
preserving the ADR-shaped branch flow.
