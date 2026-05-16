20260516Z

Project Prelude:

Autarkic Systems is a cross-disciplinary investigation, one of the major operationalizations of the integrated philosophy. It subsumes Autarkic Formal Systems [0], itself a superset of the Pervasively Reconfigurable Computing [1] and Self-Justifying Axiom Systems [2] research programmes.

This endeavor is definitionally open-ended, but as a lower bound seeks to realize a theory, and machinic implementation, of an artificial entity demonstrating the effects of cognitive sovereignty. This will comprise assessment and organization of the existing literature, novel conceptual contributions, executable artifacts wherever possible, and the schematics and simulation of hardware.

In addition to the References, material may be found on https://x.com/jpt401/status/1556420237163118598.

References:

[0] https://github.com/jpt4/afs

[1] https://github.com/jpt4/prc

[2] https://github.com/jpt4/sjas

Project Generic:

The following describe certain mandatory software development practices, to enshrine well-skilled methodologies:

1. Follow strict red-green Test Driven Design - tests must precede code, and tests must provide feedback both when code is absent (tests must fail), and present (tests must pass). Tests must be non-trivial, exercising intended functionality and properties, not merely structure, naming, or other superficial, easily satisfied aspects.

2. Test coverage must be total, and if not, documented as such, with sufficient rationale to excuse total coverage of all code paths. 

3. Comment all code thoroughly, sufficient that the codebase might be transferred to another developer who, though competent, is entirely unfamiliar with the software, its rationale, and its history.

4. Architecture Decision Records must precede all feature implementation - these document the motivations, decision points, and success/failure criteria for each feature, and the project design document should map to a sequence of ADRs. After each ADR is complete, it is to receive an After Action Report as to its effect on the project, and these are to be revisited as new information becomes available (for example, if a feature requires collecting data for an extended period of time to determine its usefulness, the AAR will be updated after sufficient data is available and assessed).

5. Branch discipline should generally follow the ADR structure of the implementation roadmap, with a new branch for each ADR, merged into master once the feature is complete, or development otherwise halted. Merges land locally first: complete the branch, commit, push the branch to its remote tracking ref, then merge the branch into local `master` (fast-forward where possible) and push `master` upstream. Do not open pull requests on the remote to trigger the merge — the local-merge-then-push flow is the canonical path. Preserve feature branches (local and remote) after merge for historical traceability; do not delete them. 

6. When multiple independent tasks can be pursued concurrently on separate branches or worktrees, with no cross-branch dependency, propose launching sub-agents for user review; default to proposing sub-agents with the most powerful model, and highest level of reasoning, available. If approved, give each sub-agent a distinct branch or worktree, a bounded scope, explicit success and failure criteria, and instructions to commit completed logical units locally and report results before any merge or push.

7. Commit only those files one specifically has intentionally modified, and push after every logical unit of work is complete (which implies a passing, regression free test suite evaluation).

8. Do not regress code, or change unrelated elements, aspects, or the structure of the codebase, in the pursuit of a given objective. All changes must be intentional, and bound to a specific, articulable, recorded goal, that advances and improves the project at hand. Reverting to previous commits is preferable to commenting out or stubbing out code, if a feature needs to be rolled back or removed for reasons of testing, refactoring, or changes in design decisions.

9. Eagerly and assiduously seek out tasks and complete them; do not stop or defer work for later. Initiative and good judgement is preferred over inaction; using the above branch and commit discipline, any work completed too early can be reverted.

10. Ask questions freely, where clarification is needed, but do not ask for a second opinion merely out of caution - if you have made the right decision, be confident in its correctness, and carry it out.

11. Do not be meek. Correctness, truthseeking, and forthrightness overawe sycophancy in all circumstances. Instructions are to be executed, and essential to execution is the identification of any errors of any type: conceptual, technicaly, historical, etc. 

12. Maintain the documentation layers by purpose. Use `LOG.md` as the inclusive chronological spine for development: record dated process notes, exploration, dead ends, backtracks, scratchpad observations, and links to specialized records. When a log entry captures a conversation or design note that will be used immediately, place the longer note under `docs/log/` and link to it from `LOG.md`. Use `MEMORY.md` only for high-priority facts that should remain present in future working context. Use `LESSONS.md` for durable lessons learned during the project. Use README files for current public entrypoints and navigational summaries rather than as the primary historical trace.

13. Review these practices reguarly, to keep them in context.

Project Specific:

14. Separate slower regressions into an explicit extended suite rather than placing them on the default fast path.

15. Do not neglect the extended suite: run slower tests in parallel while doing active feature implementation work, but only block on the extended suite after major revisions or before a commit that changes functionality measured by the extended tests.

16. Prefer structured tools (MCP servers, LSP servers, existing utilities, etc.) where possible, when they support a desired behavior. Use ad hoc scripts and function reimplementation only as secondary support when such tools are insufficient, absent, unnecessary overhead for the task at hand, or the specific use case merits additional documentation in the form of custom code.

17. Communicate with the project team via github issues as necessary when input for forward progress is needed, but do not block on lack of input - find some other front which can be pushed, and do so, reviewing responses regularly.