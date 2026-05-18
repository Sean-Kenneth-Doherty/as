"""End-of-month handoff status for AS.

The handoff report composes the current project evidence summary with the
local GitHub submission evidence. It does not introduce a new authority; it
reuses the existing status commands so the end-of-month handoff can be checked
from one local command.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from typing import Any, Callable

from autarkic_systems.github_submission import (
    DEFAULT_REMOTE_REF_MAX_AGE_SECONDS,
    Clock,
    GitHubSubmissionStatus,
    GitRunner,
    build_github_submission_status,
    format_github_submission_status,
    github_submission_status_payload,
)
from autarkic_systems.project_status import (
    build_project_status_report,
    format_project_status_summary,
)
from autarkic_systems.vertical_demo import (
    build_vertical_demo_digest,
    format_vertical_demo_digest,
)


ProjectBuilder = Callable[[], dict[str, Any]]
VerticalDemoBuilder = Callable[[], dict[str, Any]]
SubmissionBuilder = Callable[[], GitHubSubmissionStatus]


@dataclass(frozen=True)
class HandoffStatus:
    """Combined project and GitHub submission status."""

    project_status: dict[str, Any]
    vertical_demo: dict[str, Any]
    github_submission: GitHubSubmissionStatus
    project_summary: str
    vertical_demo_summary: str

    @property
    def accepted(self) -> bool:
        """Return whether both project evidence and fork submission are green."""

        return (
            bool(self.project_status["accepted"])
            and bool(self.vertical_demo["accepted"])
            and self.github_submission.accepted
        )

    @property
    def handoff_state(self) -> str:
        """Return the compact handoff-state label."""

        if self.accepted:
            return "ready"
        return "not-ready"


def build_handoff_status(
    project_builder: ProjectBuilder = build_project_status_report,
    vertical_demo_builder: VerticalDemoBuilder = build_vertical_demo_digest,
    submission_builder: SubmissionBuilder = build_github_submission_status,
) -> HandoffStatus:
    """Build a handoff report from project and submission status builders."""

    project_status = project_builder()
    vertical_demo = vertical_demo_builder()
    return HandoffStatus(
        project_status=project_status,
        vertical_demo=vertical_demo,
        github_submission=submission_builder(),
        project_summary=format_project_status_summary(project_status),
        vertical_demo_summary=format_vertical_demo_digest(vertical_demo),
    )


def handoff_status_payload(report: HandoffStatus) -> dict[str, Any]:
    """Return a JSON-ready handoff status payload."""

    return {
        "accepted": report.accepted,
        "handoff_state": report.handoff_state,
        "project_summary": report.project_summary,
        "vertical_demo_summary": report.vertical_demo_summary,
        "project_status": report.project_status,
        "vertical_demo": report.vertical_demo,
        "github_submission": github_submission_status_payload(
            report.github_submission
        ),
    }


def format_handoff_status(report: HandoffStatus) -> str:
    """Format the combined handoff report for operators."""

    return "\n".join([
        f"Autarkic Systems handoff: {report.handoff_state}",
        "",
        "Project status:",
        report.project_summary,
        "",
        "Vertical demo:",
        report.vertical_demo_summary,
        "",
        "GitHub submission:",
        format_github_submission_status(report.github_submission),
    ])


def run_handoff_cli(
    argv: list[str] | None = None,
    project_builder: ProjectBuilder = build_project_status_report,
    vertical_demo_builder: VerticalDemoBuilder = build_vertical_demo_digest,
    submission_builder: SubmissionBuilder | None = None,
    submission_runner: GitRunner | None = None,
    clock: Clock = time.time,
) -> int:
    """Run the AS handoff status CLI."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.handoff",
        description="Render the combined AS project and GitHub submission status.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the handoff report.",
    )
    parser.add_argument(
        "--refresh-remotes",
        action="store_true",
        help="Fetch fork/main and origin/main before reporting handoff status.",
    )
    parser.add_argument(
        "--max-ref-age-seconds",
        type=int,
        default=DEFAULT_REMOTE_REF_MAX_AGE_SECONDS,
        help="Maximum age for treating the local fork/main ref as fresh.",
    )
    args = parser.parse_args(argv)
    if submission_builder is None:
        submission_builder = lambda: build_github_submission_status(
            runner=submission_runner,
            clock=clock,
            remote_ref_max_age_seconds=args.max_ref_age_seconds,
            refresh_remotes=args.refresh_remotes,
        )

    report = build_handoff_status(
        project_builder=project_builder,
        vertical_demo_builder=vertical_demo_builder,
        submission_builder=submission_builder,
    )
    if args.format == "json":
        print(json.dumps(handoff_status_payload(report), sort_keys=True))
    else:
        print(format_handoff_status(report))
    return 0 if report.accepted else 1


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess tests.
    raise SystemExit(run_handoff_cli())
