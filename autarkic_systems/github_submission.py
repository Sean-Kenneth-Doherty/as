"""Local GitHub submission status for the AS workspace.

This command reports git evidence for the current submission path without
contacting GitHub APIs. It is a handoff aid: the source remote is the preferred
submission target when origin/main matches HEAD, with fork/main preserved as a
fallback path when upstream direct pushes are permission-blocked.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse


DEFAULT_TRACKING_ISSUE_URL = "https://github.com/jpt4/as/issues/1"
DEFAULT_REMOTE_REF_MAX_AGE_SECONDS = 86_400
FORK_MAIN_REMOTE_REF = "refs/remotes/fork/main"
ORIGIN_MAIN_REMOTE_REF = "refs/remotes/origin/main"
REMOTE_REFRESH_TARGETS = (
    ("fork", "main:refs/remotes/fork/main", "fork/main"),
    ("origin", "main:refs/remotes/origin/main", "origin/main"),
)


GitRunner = Callable[[list[str]], str]
Clock = Callable[[], float]


@dataclass(frozen=True)
class GitHubSubmissionStatus:
    """Local git evidence for the current GitHub submission state."""

    branch: str
    head_commit: str
    head_short: str
    origin_url: str
    fork_url: str
    origin_main_commit: str
    origin_main_short: str
    fork_main_commit: str
    fork_main_short: str
    fork_main_ref_freshness: dict[str, Any]
    origin_main_ref_freshness: dict[str, Any]
    head_behind_origin_main_by: int
    head_ahead_origin_main_by: int
    tracking_issue_url: str
    remote_refresh: dict[str, Any] = field(
        default_factory=lambda: {
            "requested": False,
            "accepted": True,
            "results": [],
        }
    )

    @property
    def fork_main_matches_head(self) -> bool:
        """Return whether fork/main points at the current HEAD."""

        return self.fork_main_commit == self.head_commit

    @property
    def fork_commit_url(self) -> str:
        """Return the GitHub web URL for the submitted fork commit."""

        return f"{_github_remote_web_url(self.fork_url)}/commit/{self.head_commit}"

    @property
    def fork_main_url(self) -> str:
        """Return the GitHub web URL for fork main."""

        return f"{_github_remote_web_url(self.fork_url)}/tree/main"

    @property
    def fork_compare_url(self) -> str:
        """Return the GitHub web URL comparing origin main to submitted HEAD."""

        return (
            f"{_github_remote_web_url(self.fork_url)}/compare/"
            f"{self.origin_main_commit}...{self.head_commit}"
        )

    @property
    def origin_main_url(self) -> str:
        """Return the GitHub web URL for origin main."""

        return f"{_github_remote_web_url(self.origin_url)}/tree/main"

    @property
    def origin_main_matches_head(self) -> bool:
        """Return whether origin/main points at the current HEAD."""

        return self.origin_main_commit == self.head_commit

    @property
    def accepted(self) -> bool:
        """Return whether the current HEAD is visible on an accepted main ref."""

        return (
            self.origin_main_matches_head or self.fork_main_matches_head
        ) and bool(self.remote_refresh["accepted"])

    @property
    def submission_state(self) -> str:
        """Return the compact submission-state label."""

        if self.remote_refresh["requested"] and not self.remote_refresh["accepted"]:
            return "refresh-failed"
        if self.origin_main_matches_head:
            return "submitted-to-origin"
        if self.fork_main_matches_head:
            return "submitted-to-fork"
        return "not-submitted-to-fork"


def build_github_submission_status(
    runner: GitRunner | None = None,
    tracking_issue_url: str = DEFAULT_TRACKING_ISSUE_URL,
    clock: Clock = time.time,
    remote_ref_max_age_seconds: int = DEFAULT_REMOTE_REF_MAX_AGE_SECONDS,
    refresh_remotes: bool = False,
) -> GitHubSubmissionStatus:
    """Build a local GitHub submission report from git commands."""

    git = runner or _run_git
    remote_refresh = (
        _refresh_remote_refs(git) if refresh_remotes else _remote_refresh_not_requested()
    )
    origin_divergence = _parse_divergence(
        git(["rev-list", "--left-right", "--count", "origin/main...HEAD"])
    )
    fork_main_freshness = _remote_ref_freshness(
        git,
        ref=FORK_MAIN_REMOTE_REF,
        clock=clock,
        max_age_seconds=remote_ref_max_age_seconds,
    )
    origin_main_freshness = _remote_ref_freshness(
        git,
        ref=ORIGIN_MAIN_REMOTE_REF,
        clock=clock,
        max_age_seconds=remote_ref_max_age_seconds,
    )
    return GitHubSubmissionStatus(
        branch=git(["branch", "--show-current"]),
        head_commit=git(["rev-parse", "HEAD"]),
        head_short=git(["rev-parse", "--short", "HEAD"]),
        origin_url=git(["remote", "get-url", "origin"]),
        fork_url=git(["remote", "get-url", "fork"]),
        origin_main_commit=git(["rev-parse", "origin/main"]),
        origin_main_short=git(["rev-parse", "--short", "origin/main"]),
        fork_main_commit=git(["rev-parse", "fork/main"]),
        fork_main_short=git(["rev-parse", "--short", "fork/main"]),
        fork_main_ref_freshness=fork_main_freshness,
        origin_main_ref_freshness=origin_main_freshness,
        head_behind_origin_main_by=origin_divergence[0],
        head_ahead_origin_main_by=origin_divergence[1],
        tracking_issue_url=tracking_issue_url,
        remote_refresh=remote_refresh,
    )


def github_submission_status_payload(
    report: GitHubSubmissionStatus,
) -> dict[str, Any]:
    """Return a JSON-ready submission status payload."""

    return {
        "accepted": report.accepted,
        "submission_state": report.submission_state,
        "remote_refresh": report.remote_refresh,
        "branch": report.branch,
        "head": {
            "commit": report.head_commit,
            "short": report.head_short,
            "fork_commit_url": report.fork_commit_url,
        },
        "remotes": {
            "origin": report.origin_url,
            "fork": report.fork_url,
        },
        "fork_main": {
            "commit": report.fork_main_commit,
            "short": report.fork_main_short,
            "matches_head": report.fork_main_matches_head,
            "web_url": report.fork_main_url,
            "compare_url": report.fork_compare_url,
            "remote_ref_freshness": report.fork_main_ref_freshness,
        },
        "origin_main": {
            "commit": report.origin_main_commit,
            "short": report.origin_main_short,
            "matches_head": report.origin_main_matches_head,
            "web_url": report.origin_main_url,
            "head_behind_by": report.head_behind_origin_main_by,
            "head_ahead_by": report.head_ahead_origin_main_by,
            "remote_ref_freshness": report.origin_main_ref_freshness,
        },
        "tracking_issue": {
            "url": report.tracking_issue_url,
        },
    }


def format_github_submission_status(report: GitHubSubmissionStatus) -> str:
    """Format the local GitHub submission status for operators."""

    fork_line = (
        f"matches HEAD ({report.fork_main_short})"
        if report.fork_main_matches_head
        else f"not submitted to fork HEAD ({report.fork_main_short})"
    )
    origin_line = (
        f"origin/main: matches HEAD ({report.origin_main_short})"
        if report.origin_main_matches_head
        else (
            "origin/main: HEAD ahead by "
            f"{report.head_ahead_origin_main_by} commits, behind by "
            f"{report.head_behind_origin_main_by} commits"
        )
    )
    lines = [
        f"GitHub submission status: {report.submission_state}",
    ]
    refresh_line = _format_remote_refresh(report.remote_refresh)
    if refresh_line:
        lines.append(refresh_line)
    lines.extend([
        f"Branch: {report.branch}",
        f"HEAD: {report.head_short}",
        f"Fork commit: {report.fork_commit_url}",
        f"Fork main: {report.fork_main_url}",
        f"Fork compare: {report.fork_compare_url}",
        f"fork/main: {fork_line}",
        _format_remote_ref_freshness(
            "fork/main",
            report.fork_main_ref_freshness,
        ),
        origin_line,
        _format_remote_ref_freshness(
            "origin/main",
            report.origin_main_ref_freshness,
        ),
        f"Origin main: {report.origin_main_url}",
        f"Origin: {report.origin_url}",
        f"Fork: {report.fork_url}",
        f"Tracking issue: {report.tracking_issue_url}",
    ])
    return "\n".join(lines)


def run_github_submission_cli(
    argv: list[str] | None = None,
    runner: GitRunner | None = None,
    clock: Clock = time.time,
) -> int:
    """Run the GitHub submission status CLI."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.github_submission",
        description="Report local git evidence for AS GitHub submission status.",
    )
    parser.add_argument(
        "--tracking-issue",
        default=DEFAULT_TRACKING_ISSUE_URL,
        help="Tracking issue URL for upstream submission notes.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the submission status report.",
    )
    parser.add_argument(
        "--max-ref-age-seconds",
        type=int,
        default=DEFAULT_REMOTE_REF_MAX_AGE_SECONDS,
        help="Maximum age for treating the local fork/main ref as fresh.",
    )
    parser.add_argument(
        "--refresh-remotes",
        action="store_true",
        help="Fetch fork/main and origin/main before reporting local status.",
    )
    args = parser.parse_args(argv)

    report = build_github_submission_status(
        runner=runner,
        tracking_issue_url=args.tracking_issue,
        clock=clock,
        remote_ref_max_age_seconds=args.max_ref_age_seconds,
        refresh_remotes=args.refresh_remotes,
    )
    if args.format == "json":
        print(json.dumps(github_submission_status_payload(report), sort_keys=True))
    else:
        print(format_github_submission_status(report))
    return 0 if report.accepted else 1


def _run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=Path.cwd(),
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _parse_divergence(value: str) -> tuple[int, int]:
    parts = value.replace("\t", " ").split()
    if len(parts) != 2:
        raise ValueError(f"malformed git divergence count: {value!r}")
    return int(parts[0]), int(parts[1])


def _github_remote_web_url(remote_url: str) -> str:
    stripped = remote_url.strip()

    scp_prefix = "git@github.com:"
    if stripped.startswith(scp_prefix):
        return _github_web_url_from_path(stripped[len(scp_prefix):])

    parsed = urlparse(stripped)
    if parsed.hostname == "github.com" and parsed.path:
        return _github_web_url_from_path(parsed.path)

    return stripped.removesuffix(".git")


def _github_web_url_from_path(path: str) -> str:
    normalized_path = path.strip("/").removesuffix(".git")
    return f"https://github.com/{normalized_path}"


def _remote_ref_freshness(
    git: GitRunner,
    ref: str,
    clock: Clock,
    max_age_seconds: int,
) -> dict[str, Any]:
    try:
        updated_at = int(
            git(["reflog", "show", "--date=unix", "-1", "--format=%cd", ref])
        )
    except Exception:
        return {
            "state": "unknown",
            "checked_ref": ref,
            "updated_at_unix": None,
            "age_seconds": None,
            "max_age_seconds": max_age_seconds,
        }
    age_seconds = max(0, int(clock()) - updated_at)
    state = "fresh" if age_seconds <= max_age_seconds else "stale"
    return {
        "state": state,
        "checked_ref": ref,
        "updated_at_unix": updated_at,
        "age_seconds": age_seconds,
        "max_age_seconds": max_age_seconds,
    }


def _format_remote_ref_freshness(label: str, freshness: dict[str, Any]) -> str:
    if freshness["state"] == "unknown":
        return (
            f"{label} freshness: unknown "
            f"(max {freshness['max_age_seconds']}s)"
        )
    return (
        f"{label} freshness: {freshness['state']} "
        f"({freshness['age_seconds']}s old, "
        f"max {freshness['max_age_seconds']}s)"
    )


def _remote_refresh_not_requested() -> dict[str, Any]:
    return {
        "requested": False,
        "accepted": True,
        "results": [],
    }


def _refresh_remote_refs(git: GitRunner) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for remote, refspec, _label in REMOTE_REFRESH_TARGETS:
        try:
            git(["fetch", remote, refspec])
        except Exception as exc:
            results.append({
                "remote": remote,
                "refspec": refspec,
                "accepted": False,
                "detail": f"{type(exc).__name__}: {exc}",
            })
            continue
        results.append({
            "remote": remote,
            "refspec": refspec,
            "accepted": True,
            "detail": f"refreshed {remote} main",
        })
    return {
        "requested": True,
        "accepted": all(result["accepted"] for result in results),
        "results": results,
    }


def _format_remote_refresh(remote_refresh: dict[str, Any]) -> str:
    if not remote_refresh["requested"]:
        return ""
    if remote_refresh["accepted"]:
        labels = [f"{result['remote']}/main" for result in remote_refresh["results"]]
        return f"Remote refresh: accepted ({', '.join(labels)})"
    failed = [
        f"{result['remote']}/main failed"
        for result in remote_refresh["results"]
        if not result["accepted"]
    ]
    return f"Remote refresh: rejected ({', '.join(failed)})"


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess tests.
    raise SystemExit(run_github_submission_cli())
