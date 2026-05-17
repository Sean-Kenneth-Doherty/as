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
