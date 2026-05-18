import contextlib
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path

from autarkic_systems.github_submission import (
    DEFAULT_TRACKING_ISSUE_URL,
    build_github_submission_status,
    format_github_submission_status,
    github_submission_status_payload,
    run_github_submission_cli,
)


class FakeGitRunner:
    def __init__(self, outputs):
        self.outputs = outputs
        self.commands = []

    def __call__(self, args):
        command = tuple(args)
        self.commands.append(command)
        return self.outputs[command]


GIT_OUTPUTS = {
    ("branch", "--show-current"): "main",
    ("rev-parse", "HEAD"): "be59d209ae3fe4deb8271c9ffd4aac83bd591e5f",
    ("rev-parse", "--short", "HEAD"): "be59d20",
    ("rev-parse", "fork/main"): "be59d209ae3fe4deb8271c9ffd4aac83bd591e5f",
    ("rev-parse", "--short", "fork/main"): "be59d20",
    ("rev-parse", "origin/main"): "9c82f89b7f3e6c911ef3c2f2b5d12a716d22c091",
    ("rev-parse", "--short", "origin/main"): "9c82f89",
    ("rev-list", "--left-right", "--count", "origin/main...HEAD"): "0\t190",
    ("remote", "get-url", "origin"): "https://github.com/jpt4/as.git",
    ("remote", "get-url", "fork"): "https://github.com/Sean-Kenneth-Doherty/as.git",
    (
        "reflog",
        "show",
        "--date=unix",
        "-1",
        "--format=%cd",
        "refs/remotes/fork/main",
    ): "1779110000",
}


class GitHubSubmissionStatusTests(unittest.TestCase):
    def test_status_payload_reports_fork_submission_and_origin_divergence(self):
        runner = FakeGitRunner(GIT_OUTPUTS)

        report = build_github_submission_status(
            runner=runner,
            clock=lambda: 1779110300,
        )
        payload = github_submission_status_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["submission_state"], "submitted-to-fork")
        self.assertEqual(payload["branch"], "main")
        self.assertEqual(
            payload["head"]["commit"],
            "be59d209ae3fe4deb8271c9ffd4aac83bd591e5f",
        )
        self.assertEqual(payload["head"]["short"], "be59d20")
        self.assertEqual(payload["remotes"]["origin"], "https://github.com/jpt4/as.git")
        self.assertEqual(
            payload["remotes"]["fork"],
            "https://github.com/Sean-Kenneth-Doherty/as.git",
        )
        self.assertTrue(payload["fork_main"]["matches_head"])
        self.assertEqual(payload["fork_main"]["short"], "be59d20")
        self.assertFalse(payload["origin_main"]["matches_head"])
        self.assertEqual(payload["origin_main"]["head_ahead_by"], 190)
        self.assertEqual(payload["origin_main"]["head_behind_by"], 0)
        self.assertEqual(
            payload["fork_main"]["remote_ref_freshness"],
            {
                "state": "fresh",
                "checked_ref": "refs/remotes/fork/main",
                "updated_at_unix": 1779110000,
                "age_seconds": 300,
                "max_age_seconds": 86400,
            },
        )
        self.assertEqual(payload["tracking_issue"]["url"], DEFAULT_TRACKING_ISSUE_URL)
        self.assertIn(("rev-parse", "fork/main"), runner.commands)
        self.assertIn(
            (
                "reflog",
                "show",
                "--date=unix",
                "-1",
                "--format=%cd",
                "refs/remotes/fork/main",
            ),
            runner.commands,
        )

    def test_text_status_reports_operator_submission_summary(self):
        report = build_github_submission_status(
            runner=FakeGitRunner(GIT_OUTPUTS),
            clock=lambda: 1779110300,
        )

        text = format_github_submission_status(report)

        self.assertIn("GitHub submission status: submitted-to-fork", text)
        self.assertIn("Branch: main", text)
        self.assertIn("HEAD: be59d20", text)
        self.assertIn("fork/main: matches HEAD (be59d20)", text)
        self.assertIn("fork/main freshness: fresh (300s old, max 86400s)", text)
        self.assertIn("origin/main: HEAD ahead by 190 commits, behind by 0 commits", text)
        self.assertIn("Origin: https://github.com/jpt4/as.git", text)
        self.assertIn("Fork: https://github.com/Sean-Kenneth-Doherty/as.git", text)
        self.assertIn(f"Tracking issue: {DEFAULT_TRACKING_ISSUE_URL}", text)

    def test_status_reports_stale_fork_main_ref_freshness(self):
        report = build_github_submission_status(
            runner=FakeGitRunner(GIT_OUTPUTS),
            clock=lambda: 1779200001,
        )

        payload = github_submission_status_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(
            payload["fork_main"]["remote_ref_freshness"]["state"],
            "stale",
        )
        self.assertEqual(
            payload["fork_main"]["remote_ref_freshness"]["age_seconds"],
            90001,
        )
        self.assertIn(
            "fork/main freshness: stale (90001s old, max 86400s)",
            format_github_submission_status(report),
        )

    def test_status_rejects_when_fork_main_does_not_match_head(self):
        outputs = dict(GIT_OUTPUTS)
        outputs[("rev-parse", "fork/main")] = "df6de62ca82d88fd2b8aee0a1c25d7dfdaa8a67d"
        outputs[("rev-parse", "--short", "fork/main")] = "df6de62"

        report = build_github_submission_status(runner=FakeGitRunner(outputs))

        self.assertFalse(report.accepted)
        self.assertEqual(report.submission_state, "not-submitted-to-fork")
        self.assertFalse(report.fork_main_matches_head)
        self.assertIn("not submitted to fork HEAD", format_github_submission_status(report))

    def test_json_cli_reports_submission_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_github_submission_cli(
                ["--format", "json"],
                runner=FakeGitRunner(GIT_OUTPUTS),
                clock=lambda: 1779110300,
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["submission_state"], "submitted-to-fork")
        self.assertEqual(payload["origin_main"]["head_ahead_by"], 190)

    def test_module_execution_runs_live_text_status(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.github_submission"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertIn(completed.returncode, {0, 1}, completed.stderr)
        self.assertIn("GitHub submission status:", completed.stdout)
        self.assertIn("fork/main:", completed.stdout)


if __name__ == "__main__":
    unittest.main()
