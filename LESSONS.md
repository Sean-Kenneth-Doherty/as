# Lessons

## 2026-05-16

- A newborn research repository can still have strong intent. When the code
  tree is empty, the correct first artifact is a source-backed orientation
  scaffold, not premature implementation.
- In this project, "autarkic" has two coupled meanings that must remain joined:
  formal self-confidence and embodied control of the computational substrate.
- When one repo log points to adjacent implementation work, verify the public
  branch before treating it as current. In this case, SJAS describes newer
  Proflog work than public `jpt4/proflog` exposes on `main`.
- For this repo's standard-library Python tests, keep `tests/__init__.py` so
  plain `python -m unittest discover` finds the suite from the repository root.
- For AS formal-confidence work, a source list is not enough. Exact definition,
  theorem, construction, and boundary anchors should be made structured and
  testable before any self-consistency claim is implemented.
- Keep `_upstream` source checkouts out of the default fast-test critical path.
  Fast tests should validate pinned source-status facts and paths; live clone or
  smoke-test checks belong in ADR evidence or an explicit extended gate.
- For PRC hardware/schematic work, draw nothing until the source constraints
  are structured. The first useful artifact is a witness map that separates
  symbolic RLEM behavior, GELC geometry, UC state, reconfiguration support, and
  candidate physical implementation claims.
- A schematic trace is more useful when it is executable. Recording a diagram
  key and replaying its claimed transition through the Universal Cell probe
  catches drift that a static drawing would hide.
- A rendered schematic should be generated from the structured trace whenever
  practical. Otherwise the human-facing diagram becomes a second, weaker source
  of truth.
- Reusing the schematic trace schema for processor behavior is better than
  adding a one-off artifact. It keeps wire and processor evidence comparable
  while still testing role-specific behavior.
- When a second SVG render is added, generalize the renderer while preserving
  compatibility wrappers and exact-output tests for the first SVG. That keeps
  visual reuse from weakening drift protection.
- Stem reconfiguration evidence must name what it does not cover. A tested
  automail trace is useful, but it is not full stem buffering or dynamic
  circuit reconfiguration.
- A stem reconfiguration render must show the state change, not merely the
  node geometry. Role after-transition and automail consumption are part of the
  visual evidence contract.
- For stem behavior, implementing accumulation separately from command
  execution keeps the PRC source model honest. A full buffer should be an
  explicit boundary until command decoding and target routing are tested.
- After adding a new transition status or behavior, promote only the stable
  subset into the claim surface. The claim should repeat the boundary rather
  than smuggling in future command-decoding obligations.
- When a new stem trace is added, route validation by the actual stem subset.
  Automail and standard-signal buffering share role `stem` but have different
  evidence obligations.
- A buffer SVG has to show buffer state explicitly. The renderer should add
  trace-specific summary fields when generic role/memory/status text would
  hide the actual claim.
- Decode maps should become structured artifacts before execution code depends
  on them. This keeps command semantics reviewable and avoids magic numbers in
  transition logic.
- A source-backed decoder is not the same as source-backed execution. When
  legacy sketches disagree about target and command interpretation, record the
  disagreement before mutating the substrate model.
- Representation unblockers should propagate through every schema boundary.
  A new `Cell` field is not real project state until claim manifests, object
  language, and schematic traces all preserve it.
- Broadening what state can represent is not the same as broadening what
  transitions execute. Tests should prove command tokens are preserved or
  rejected at the current boundary before later routing semantics are added.
- When command semantics diverge by source, split the stable init-family cases
  from unresolved write-buffer or standard-signal cases instead of forcing one
  execution rule too early.
- Once a bounded execution subset is stable, give it a named claim before using
  it as a dependency. That keeps later command work tied to manifest examples
  and proof-certificate coverage rather than raw transition behavior alone.
- Stem schematic traces need dispatch by the active stem mechanism. Empty
  automail plus non-empty `self_mailbox` is mailbox execution, not buffer
  accumulation, even though both use `step_stem_cell`.
- Render summaries should follow the semantic cause of a state change. A
  self-mailbox init can change role like automail does, but its visible proof
  surface is mailbox consumption and cleared command state.
- Boundary behavior deserves claims too. When AS deliberately refuses to
  execute an unresolved command, a preservation claim is better than leaving
  that refusal as an informal test side effect.
- Trace dispatch should use the transition status when the same visible field
  can mean different mechanisms. Non-empty `self_mailbox` plus
  `self-mailbox-unsupported` is a preservation boundary, not an init command.
- No-op evidence still needs visible state. For unsupported commands, the
  important render fact is preservation of mailbox/control/buffer, not absence
  of visual change.
- Command-buffer execution should advance through previously claimed behavior.
  Dispatching self-target init buffers is acceptable because direct
  self-mailbox init semantics are already tested, claimed, and rendered.
- Once a command-buffer behavior is executable, claim it before drawing it.
  The schematic layer should rest on named transition claims where practical,
  not just ad hoc replay behavior.
- Completed-buffer traces need their own validation path when they share the
  same visible fields as accumulation traces. Status-dispatch keeps a
  processed command buffer from being mistaken for another append.
- Command-buffer renders should show the decoded command state directly. A
  role-changing dispatch can look like generic reconfiguration unless the SVG
  exposes buffer before/after and cleared command state.
- When a command-buffer case is deliberately not executed, name the append
  boundary before building the next behavior. That preserves the current
  frontier as a claim instead of an accidental hole between tests.
- Unsupported command-buffer traces should track the live frontier, not the
  frontier that existed when the trace was first written. Neighbor examples
  were useful before delivery landed; after ADR-0044, the unsupported trace
  belongs on self-target non-init commands.
- Unsupported command-buffer renders must show preservation as an active fact.
  When a once-unsupported neighbor command becomes delivered behavior, revise
  the trace and render instead of preserving stale evidence.
- New command-buffer behavior should enter the named claim surface before
  schematic evidence depends on it. That keeps later traces tied to explicit
  proof obligations instead of direct behavior tests alone.
- Delivery renders must expose the exact output channel, not only that output
  changed. Otherwise a wrong-channel command delivery can look visually valid.
- After delivery evidence is complete, decide recipient consumption from source
  status before changing runtime behavior. A delivered token is only half of
  the semantics.
- Recipient command-message consumption should land as init-family behavior
  first. Keeping `standard-signal`, write-buffer, and multi-command inputs at
  the rejection boundary avoids laundering unresolved command semantics through
  an otherwise source-backed slice.
- When recipient command behavior becomes executable, claim it before drawing
  it. Fixed upstream input and stem direct input are similar enough to share a
  predicate, but the predicate must still check the source-specific upstream
  clearing rule.
- A recipient command trace should show where the delivered token entered the
  cell. For fixed cells, the trace is clearer when it records upstream pull and
  upstream clearing instead of pretending the token started as direct input.
- Recipient command renders need their own summary branch. Generic role-change
  text hides the important proof surface: the upstream command token was
  consumed and the recipient's transient command state was cleared.
- When legacy command sources agree on command names but disagree on clearing
  and buffer behavior, record the divergence before implementing. The honest
  next step can be a claim over the current rejection boundary, not execution.
- Rejection claims should include the input source. Fixed direct input and
  fixed upstream input both reject non-init command messages, but upstream
  rejection must also prove the pulled command source was cleared.
- Rejection traces should show the rejected token as active state, not mere
  absence of execution. For pulled-upstream recipient commands, the trace must
  record source clearing and role/memory preservation together.
- Rejection renders need their own summary branch when the state mostly stays
  the same. Generic no-change rendering hides the evidence that the command
  source was actively rejected and cleared.
- A command name appearing in every source is not enough to implement it. For
  write-buffer commands, append semantics, clearing behavior, and buffer-full
  boundaries must agree before runtime execution is honest.
- A command-table entry can name behavior that already exists in another input
  class without defining command-token execution. For `standard-signal`, keep
  ordinary binary-input routing/buffering separate from command-message,
  self-mailbox, and self-target command-buffer execution until a source decides
  that bridge.
- Multiple simultaneous command-message tokens should not silently inherit a
  priority rule. When no source orders them, the honest policy is to reject and
  clear the active command input, then make that boundary visible in claims and
  traces.
- A trace validator can be reused when the behavioral contract is the same.
  Multi-command rejection is a recipient non-init rejection boundary with a
  different input shape, so routing the new artifact through the existing
  alignment check avoids inventing duplicate validation logic.
- A render branch can also be reused when the visible contract is the same.
  Multi-command rejection needs the same rejection summary as the single-token
  non-init case, with the simultaneous conflict kept visible in the input
  field and flow text.
- A newly found simulator witness is not automatically a green light. If it
  changes command names or uses numeric command values where other sources use
  named tokens, record that as source divergence before changing runtime
  behavior.
- Explicit uncertainty comments in a source artifact are evidence. When a
  simulator says its process-buffer needs documentation or code confirmation,
  preserve that warning in machine-checkable status before building behavior on
  top of it.
- Formal-looking files still need source-status verification. A TLA file that
  is empty, a one-line stub, or an unfinished skeleton is context, not
  executable authority for command semantics.
- Evidence bundles should validate links, not merely list them. A useful
  bundle proves that its claim example, proof certificate, trace replay, SVG
  render, and source-status boundary still agree.
- Evidence bundles need a registry before there are many of them. Discovery
  should be machine-checkable, with duplicate and missing-path failures, not
  left to filesystem convention.
- A registry that only runs in unit tests is still too hidden for operators.
  Give important validation surfaces a direct command with meaningful exit
  codes once the underlying checks are stable.
- Evidence registries should include blocked-boundary examples, not only
  successful execution examples. A rejection bundle proves the negative
  frontier is just as inspectable as the green path.
- Multi-command policies deserve their own evidence bundle even when they
  share a rejection claim. The inspected question is not only "is rejection
  correct?" but also "did AS avoid inventing priority or sequencing?"
- A registry should fail closed over its artifact directory. If a bundle file
  can sit beside the manifest without being listed, the registry is only a
  partial index.
- Once a validation command matters to agents or CI, add JSON output before
  anyone starts scraping human `OK` lines.
- Integrated evidence can expose near-miss fixture drift. If a trace and a
  claim describe the same transition with different incidental state, align the
  artifacts so the bundle proves one exact path.
- Negative-frontier evidence bundles are useful for the same reason as green
  execution bundles: they prove AS preserved a boundary instead of merely
  failing to implement behavior.
- Evidence bundles should also cover decoded-command paths, not only direct
  mailbox or channel tokens. That proves the decoder, runtime transition,
  claim, proof, trace, and render stay aligned as a chain.
- When an evidence bundle covers a negative decoded-command path, keep the
  renderer docs honest about the exact active rail and completed buffer; small
  visible-detail drift undercuts the point of the bundle.
- Delivery evidence should stay separate from consumption evidence. A
  neighbor-target bundle proves that the decoded token reached the right output
  channel, while recipient execution still belongs to its own source-status
  and evidence path.
- A two-step chain is a useful middle layer before a simulator. It can prove
  sender and recipient transitions compose while still refusing topology,
  scheduling, overwrite, and non-init execution claims.
- Chain claims should not be smuggled into a single-transition language. When
  a claim depends on sender state, recipient preconditions, handoff state, and
  a second transition, give it a separate manifest shape until the project has
  a real chain object language.
- Chain language validation should execute the examples, not only inspect
  static JSON. Otherwise a status vocabulary can look complete while missing a
  real precondition or boundary status produced by the chain helper.
- Once a claim surface has its own manifest, language, and proof check, give it
  a direct validation command. Operators and agents should not have to know the
  unit-test module name to verify a project contract.
- Composed-chain evidence should not be silently added to a single-transition
  registry. Keep the chain artifact separate, then validate the claim, proof,
  language, lower-level bundles, and source blockers together.
- A composed handoff trace is a better precursor to SVG than immediately
  drawing two cells. First record the sender step, delivered tuple, recipient
  handoff state, recipient step, and chain replay in a machine-checked JSON
  artifact.
- Chain SVGs need the same renderer lock as single-transition SVGs. If the
  visual is checked in, validate exact renderer output and route it through the
  composed evidence bundle.
- Once chain evidence has its own artifact family, give it its own closed
  registry instead of relaxing the single-transition registry boundary.
- A CLI that can validate one artifact or a registry should reject ambiguous
  target flags instead of silently choosing one.
- Registry JSON should identify what it validated, not only how many entries
  passed. Include bundle IDs and paths so automation does not have to re-read
  the manifest.
- Registry JSON should also summarize why it failed. A small `failed_subjects`
  list saves automation from reimplementing result scanning.
- Keep bundle JSON and registry JSON contracts parallel where the semantics
  match; automation should not need different failure-scanning code for each.
- Once an evidence stack becomes deep enough, add a vertical demo surface that
  reuses validators and makes the integrated artifact inspectable from one
  command.
- Demo reports should expose artifact presence directly. A first-run surface
  should not require readers to infer missing files from lower-level validator
  details.
