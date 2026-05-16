# ADR-0001: Project Orientation Scaffold

Date: 2026-05-16

Status: Accepted

## Context

The upstream AS repository was created with only `AGENTS.md` and `AGENTS.md~`.
`AGENTS.md` defines Autarkic Systems as an open-ended cross-disciplinary
investigation that subsumes AFS, PRC, and SJAS. It also requires ADR-led
development, careful documentation layering, strict test-first discipline for
code, and active forward motion.

The first useful work cannot be feature implementation because there is no
project structure, no implementation target, and no local design document that
maps the three subordinate programs into AS. Adding code before this would make
the branch look active while leaving the project's intent under-specified.

## Decision

Create an orientation scaffold before implementation:

- `README.md` as the current public entrypoint;
- `LOG.md` as the chronological development spine;
- `MEMORY.md` for high-priority future context;
- `LESSONS.md` for durable lessons learned;
- `docs/project-charter.md` for the first concrete interpretation of the
  umbrella objective;
- `docs/subordinate-review.md` for the first source-backed review of AFS, PRC,
  and SJAS;
- `docs/roadmap.md` for the first ADR-shaped work sequence.

No software code is added in this ADR. The strict red-green rule becomes active
for the first code-bearing ADR.

## Success Criteria

- The repository has a current entrypoint that explains its purpose without
  requiring out-of-band context.
- Every subordinate repository named in `AGENTS.md` is represented in a review.
- Reviewed commit snapshots are recorded.
- The next work item can be selected from a documented roadmap.
- The documentation layers required by `AGENTS.md` exist.

## Consequences

- Future work has a place to record evidence and course corrections.
- The project now has a conservative first integration hypothesis: PRC supplies
  the explicit substrate/body side, SJAS supplies the formal self-confidence
  side, and AFS/AS must define the interface between them.
- This does not yet satisfy the lower-bound objective of executable artifacts or
  hardware simulation. It only creates the map needed to pursue them honestly.

## After Action Report

The scaffold was added after reviewing:

- `jpt4/as` at `1a2fc06b75f5d33aee6655956c2a56df07a7bfb0`;
- `jpt4/afs` at `a61592eab02a93d480149ce3465af5e3271ca213`;
- `jpt4/prc` at `7e82c73fac8f108faac801a5c65e2c2b92653ba5`;
- `jpt4/sjas` at `f1c11af5f310d39f487c3b91ee1ca70f4ade8871`.

The scaffold met its success criteria as a documentation slice. Remaining
gaps:

- the referenced X/Twitter status was not captured;
- AFS still lacks a concrete definition beyond its name;
- no executable artifact exists in AS yet;
- the location and status of recent Proflog SJAS implementation work needs to
  be mapped before AS treats SJAS as fully represented.
