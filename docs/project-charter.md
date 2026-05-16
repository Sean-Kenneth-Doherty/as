# Project Charter

## Purpose

Autarkic Systems seeks a theory and machinic implementation of artificial
cognitive sovereignty.

For this project, cognitive sovereignty means an artificial entity can maintain
meaningful confidence in its own reasoning and substrate because the relevant
logic, implementation, and physical computing assumptions are exposed to
inspection, reconfiguration, and eventual self-reference. The project is not
just a software agent, not just a proof-system project, and not just a hardware
architecture project. It is the integration layer where those lines of work are
made mutually legible.

## Subsumed Programs

Autarkic Systems currently sits above three named programs:

- Autarkic Formal Systems: the immediate formal-systems umbrella. At the first
  review snapshot, the public repository is only a placeholder, so its concrete
  obligations need to be made explicit here before implementation work can be
  honest.
- Pervasively Reconfigurable Computing: the body and substrate layer, aiming at
  computational elements whose behavior, routing, power, and reconfiguration
  are explicitly modeled rather than hidden beneath opaque hardware authority.
- Self-Justifying Axiom Systems: the logic and epistemic-security layer,
  aiming at formal systems that can prove selected consistency claims about
  themselves by carefully trading off expressivity and deduction method.

## Lower-Bound Deliverables

The prelude in `AGENTS.md` defines the lower bound as:

- assessment and organization of existing literature;
- novel conceptual contributions;
- executable artifacts wherever possible;
- schematics and simulation of hardware.

The first working interpretation of that lower bound is:

1. Build a curated knowledge map that connects PRC and SJAS into a single AFS
   story.
2. Identify the smallest executable artifacts that can test the integration,
   rather than treating the whole program as prose.
3. Preserve every significant design move as an ADR with success and failure
   criteria.
4. Keep slow or high-effort regressions separate from fast checks once code
   exists.
5. Record gaps explicitly when theory, implementation, or verification cannot
   yet reach the intended standard.

## Key Research Tensions

- Formal confidence vs. expressivity: SJAS-style systems gain self-confidence
  by weakening or tuning expressive resources. Any agent architecture must say
  exactly where this trade happens.
- Embodiment vs. abstraction: PRC insists that the computational substrate
  itself matters. A purely abstract proof assistant is insufficient if the
  final claim depends on opaque hardware.
- Reconfiguration vs. verification: self-modifying or reconfigurable systems
  need a checkable account of when changes preserve the guarantees the system
  depends on.
- Literature archive vs. executable progress: the program needs deep review,
  but the review must continuously narrow toward artifacts, tests, schematics,
  and simulations.

## Near-Term Definition Of Done

A near-term slice is done only when it has:

- an ADR or explicit log entry tying the work to the project objective;
- source-backed references to the subordinate material it uses;
- a fast verification path if it changes code or structured data;
- documented coverage limits if total verification is not available;
- an after-action note recording what the work changed and what remains open.
