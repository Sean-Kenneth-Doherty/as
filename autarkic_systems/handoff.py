"""End-of-month handoff status for AS.

The handoff report composes the current project evidence summary, vertical
demo digest, suite-selection boundary, and local GitHub submission evidence.
It does not introduce a new proof authority; it reuses the existing status
commands so the end-of-month handoff can be checked from one local command.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
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
from autarkic_systems.test_suite_selection import (
    DEFAULT_MANIFEST_PATH,
    DEFAULT_TESTS_ROOT,
    SuiteManifestError,
    build_suite_index_payload,
    build_suite_plan,
    discover_test_modules,
    load_suite_manifest,
)
from autarkic_systems.vertical_demo import (
    build_vertical_demo_digest,
    format_vertical_demo_digest,
)


ProjectBuilder = Callable[[], dict[str, Any]]
VerticalDemoBuilder = Callable[..., dict[str, Any]]
SubmissionBuilder = Callable[[], GitHubSubmissionStatus]
SuiteSelectionBuilder = Callable[[], dict[str, Any]]
SUITE_SELECTION_INDEX_COMMAND = (
    "python -m autarkic_systems.test_suite_selection "
    "--list-suites --format json"
)


@dataclass(frozen=True)
class HandoffStatus:
    """Combined project, demo, suite-selection, and GitHub submission status."""

    project_status: dict[str, Any]
    vertical_demo: dict[str, Any]
    github_submission: GitHubSubmissionStatus
    suite_selection: dict[str, Any]
    project_summary: str
    vertical_demo_summary: str

    @property
    def accepted(self) -> bool:
        """Return whether every handoff evidence boundary is accepted."""

        return (
            bool(self.project_status["accepted"])
            and bool(self.vertical_demo["accepted"])
            and bool(self.suite_selection.get("accepted"))
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
    suite_selection_builder: SuiteSelectionBuilder = (
        lambda: build_handoff_suite_selection()
    ),
) -> HandoffStatus:
    """Build a handoff report from the injected evidence builders."""

    project_status = project_builder()
    vertical_demo = vertical_demo_builder(project_status=project_status)
    suite_selection = suite_selection_builder()
    return HandoffStatus(
        project_status=project_status,
        vertical_demo=vertical_demo,
        github_submission=submission_builder(),
        suite_selection=suite_selection,
        project_summary=format_project_status_summary(project_status),
        vertical_demo_summary=format_vertical_demo_digest(vertical_demo),
    )


def build_handoff_suite_selection(
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    tests_root: str | Path = DEFAULT_TESTS_ROOT,
) -> dict[str, Any]:
    """Build fail-closed suite-selection evidence without running unittest.

    The selector already owns manifest parsing, live discovery, partition
    checks, and command metadata. Handoff only serializes that checked plan so
    recipients can see which verification boundary framed the report.
    """

    try:
        manifest = load_suite_manifest(manifest_path)
        discovered_modules = discover_test_modules(tests_root)
        plan = build_suite_plan(manifest, discovered_modules)
    except SuiteManifestError as error:
        return {
            "accepted": False,
            "command": SUITE_SELECTION_INDEX_COMMAND,
            "selected_suite_commands": {},
            "error": str(error),
        }

    payload = dict(build_suite_index_payload(plan))
    selectable_suites = payload["selectable_suites"]
    return {
        "accepted": True,
        "command": SUITE_SELECTION_INDEX_COMMAND,
        "selected_suite_commands": {
            suite_name: _selected_suite_command(suite_name)
            for suite_name in selectable_suites
        },
        **payload,
    }


def handoff_status_payload(report: HandoffStatus) -> dict[str, Any]:
    """Return a JSON-ready handoff status payload."""

    return {
        "accepted": report.accepted,
        "handoff_state": report.handoff_state,
        "project_summary": report.project_summary,
        "vertical_demo_summary": report.vertical_demo_summary,
        "project_status": report.project_status,
        "vertical_demo": report.vertical_demo,
        "suite_selection": report.suite_selection,
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
        format_suite_selection_status(report.suite_selection),
        "",
        "GitHub submission:",
        format_github_submission_status(report.github_submission),
    ])


def format_suite_selection_status(suite_selection: dict[str, Any]) -> str:
    """Format suite-selection evidence for the handoff text report."""

    lines = [
        "Suite selection:",
        f"Suite index: {suite_selection.get('command', SUITE_SELECTION_INDEX_COMMAND)}",
    ]
    if not suite_selection.get("accepted"):
        error = suite_selection.get("error", "unknown suite-selection error")
        lines.append(f"Status: rejected ({error})")
        return "\n".join(lines)

    suite_commands = suite_selection.get("selected_suite_commands", {})
    for suite_name in suite_selection["selectable_suites"]:
        suite = suite_selection["suites"][suite_name]
        command = suite_commands.get(suite_name, _selected_suite_command(suite_name))
        lines.append(f"- {suite_name}: {suite['module_count']} modules; {command}")
    return "\n".join(lines)


def _selected_suite_command(suite_name: str) -> str:
    """Return the stable selector command for one named unittest suite."""

    return f"python -m autarkic_systems.test_suite_selection --suite {suite_name}"


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
