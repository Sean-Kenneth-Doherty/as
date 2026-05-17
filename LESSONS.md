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
- Stem reconfiguration evidence must name what it does not cover. A tested
  automail trace is useful, but it is not full stem buffering or dynamic
  circuit reconfiguration.
