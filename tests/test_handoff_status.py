import contextlib
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path

from autarkic_systems.github_submission import (
    DEFAULT_TRACKING_ISSUE_URL,
    GitHubSubmissionStatus,
)
from autarkic_systems.handoff import (
    build_handoff_status,
    format_handoff_status,
    handoff_status_payload,
    run_handoff_cli,
)


class FakeGitRunner:
    def __init__(self, outputs):
        self.outputs = outputs
        self.commands = []

    def __call__(self, args):
        command = tuple(args)
        self.commands.append(command)
        return self.outputs[command]


PROJECT_REPORT = {
    "accepted": True,
    "transition_evidence": {"bundle_count": 11},
    "chain_evidence": {"bundle_count": 2},
    "sequence_evidence": {"bundle_count": 1},
    "transition_claims": {"claim_count": 16, "matched_count": 40},
    "chain_claims": {"claim_count": 2, "certificate_count": 2},
    "sequence_claims": {"claim_count": 1, "certificate_count": 1},
    "proof_rule_audit": {
        "combined": {
            "rule_counts": {
                "predicate-result": 52,
                "manifest-example": 0,
            }
        }
    },
    "frontier": {
        "blocked_commands": ["standard-signal"],
        "safe_next_slice": "",
    },
}


VERTICAL_DEMO_DIGEST = {
    "accepted": True,
    "demonstration": "post-handoff signal routing through checked evidence",
    "evidence_counts": {
        "transition_bundles": 11,
        "chain_bundles": 2,
        "sequence_bundles": 1,
    },
    "claim_counts": {
        "transition_claims": 16,
        "transition_matched_examples": 40,
        "chain_claims": 2,
        "sequence_claims": 1,
    },
    "proof_rules": {
        "predicate-result": 52,
        "manifest-example": 0,
    },
    "blocked_commands": ["standard-signal"],
    "safe_next_slice": "",
    "registries": {
        "transition": "evidence/manifest.json",
        "chain": "evidence/chains/manifest.json",
        "sequence": "evidence/sequences/manifest.json",
    },
    "sequence_evidence_bundle": {
        "bundle_id": "post-handoff-signal-sequence-evidence-bundle",
        "path": "evidence/sequences/post_handoff_signal_bundle.json",
        "sequence_claim_id": "UC-SEQUENCE-POST-HANDOFF-SIGNAL-ROUTED",
        "expected_status": "post-handoff-signal-routed",
    },
    "boundary": "no standard-signal command-token execution change without new source evidence",
}


GIT_OUTPUTS = {
    ("fetch", "fork", "main:refs/remotes/fork/main"): "",
    ("fetch", "origin", "main:refs/remotes/origin/main"): "",
    ("branch", "--show-current"): "main",
    ("rev-parse", "HEAD"): "04158fc29229d091f616734725be3c8f54198200",
    ("rev-parse", "--short", "HEAD"): "04158fc",
    ("rev-parse", "fork/main"): "04158fc29229d091f616734725be3c8f54198200",
    ("rev-parse", "--short", "fork/main"): "04158fc",
    ("rev-parse", "origin/main"): "1a2fc06b75f5d33aee6655956c2a56df07a7bfb0",
    ("rev-parse", "--short", "origin/main"): "1a2fc06",
    ("rev-list", "--left-right", "--count", "origin/main...HEAD"): "0\t191",
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


SUBMISSION_REPORT = GitHubSubmissionStatus(
    branch="main",
    head_commit="04158fc29229d091f616734725be3c8f54198200",
    head_short="04158fc",
    origin_url="https://github.com/jpt4/as.git",
    fork_url="https://github.com/Sean-Kenneth-Doherty/as.git",
    origin_main_commit="1a2fc06b75f5d33aee6655956c2a56df07a7bfb0",
    origin_main_short="1a2fc06",
    fork_main_commit="04158fc29229d091f616734725be3c8f54198200",
    fork_main_short="04158fc",
    fork_main_ref_freshness={
        "state": "fresh",
        "checked_ref": "refs/remotes/fork/main",
        "updated_at_unix": 1779110000,
        "age_seconds": 300,
        "max_age_seconds": 86400,
    },
    head_behind_origin_main_by=0,
    head_ahead_origin_main_by=191,
    tracking_issue_url=DEFAULT_TRACKING_ISSUE_URL,
)


def build_project_report():
    return PROJECT_REPORT


def build_submission_report():
    return SUBMISSION_REPORT


def build_vertical_demo_digest():
    return VERTICAL_DEMO_DIGEST


class HandoffStatusTests(unittest.TestCase):
    def test_handoff_payload_combines_project_and_submission_status(self):
        report = build_handoff_status(
            project_builder=build_project_report,
            vertical_demo_builder=build_vertical_demo_digest,
            submission_builder=build_submission_report,
        )
        payload = handoff_status_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["handoff_state"], "ready")
        self.assertIn("Autarkic Systems summary: accepted", payload["project_summary"])
        self.assertIn(
            "Autarkic Systems vertical demo: accepted",
            payload["vertical_demo_summary"],
        )
        self.assertEqual(payload["vertical_demo"], VERTICAL_DEMO_DIGEST)
        self.assertEqual(
            payload["vertical_demo"]["sequence_evidence_bundle"]["path"],
            "evidence/sequences/post_handoff_signal_bundle.json",
        )
        self.assertIn(
            "Evidence: 11 transition bundles; 2 chain bundles; 1 sequence bundle",
            payload["project_summary"],
        )
        self.assertIn(
            "Claims: 16 transition claims/40 matched examples; "
            "2 chain claims/2 certificates; 1 sequence claim/1 certificate",
            payload["project_summary"],
        )
        self.assertEqual(payload["project_status"], PROJECT_REPORT)
        self.assertEqual(payload["github_submission"]["submission_state"], "submitted-to-fork")
        self.assertEqual(payload["github_submission"]["head"]["short"], "04158fc")
        self.assertEqual(
            payload["github_submission"]["fork_main"]["remote_ref_freshness"]["state"],
            "fresh",
        )

    def test_handoff_text_renders_project_and_submission_sections(self):
        report = build_handoff_status(
            project_builder=build_project_report,
            vertical_demo_builder=build_vertical_demo_digest,
            submission_builder=build_submission_report,
        )

        text = format_handoff_status(report)

        self.assertIn("Autarkic Systems handoff: ready", text)
        self.assertIn("Project status:", text)
        self.assertIn("Autarkic Systems summary: accepted", text)
        self.assertIn("Vertical demo:", text)
        self.assertIn("Autarkic Systems vertical demo: accepted", text)
        self.assertIn(
            "Current demonstration: post-handoff signal routing through checked evidence",
            text,
        )
        self.assertIn("GitHub submission:", text)
        self.assertIn("GitHub submission status: submitted-to-fork", text)
        self.assertIn("fork/main: matches HEAD (04158fc)", text)
        self.assertIn("origin/main: HEAD ahead by 191 commits", text)

    def test_handoff_rejects_when_submission_is_not_on_fork_main(self):
        not_submitted = GitHubSubmissionStatus(
            branch="main",
            head_commit="1111111111111111111111111111111111111111",
            head_short="1111111",
            origin_url=SUBMISSION_REPORT.origin_url,
            fork_url=SUBMISSION_REPORT.fork_url,
            origin_main_commit=SUBMISSION_REPORT.origin_main_commit,
            origin_main_short=SUBMISSION_REPORT.origin_main_short,
            fork_main_commit=SUBMISSION_REPORT.fork_main_commit,
            fork_main_short=SUBMISSION_REPORT.fork_main_short,
            fork_main_ref_freshness=SUBMISSION_REPORT.fork_main_ref_freshness,
            head_behind_origin_main_by=0,
            head_ahead_origin_main_by=192,
            tracking_issue_url=DEFAULT_TRACKING_ISSUE_URL,
        )

        report = build_handoff_status(
            project_builder=build_project_report,
            vertical_demo_builder=build_vertical_demo_digest,
            submission_builder=lambda: not_submitted,
        )

        self.assertFalse(report.accepted)
        self.assertEqual(report.handoff_state, "not-ready")
        self.assertIn("Autarkic Systems handoff: not-ready", format_handoff_status(report))

    def test_handoff_rejects_when_vertical_demo_is_rejected(self):
        rejected_demo = {
            **VERTICAL_DEMO_DIGEST,
            "accepted": False,
        }

        report = build_handoff_status(
            project_builder=build_project_report,
            vertical_demo_builder=lambda: rejected_demo,
            submission_builder=build_submission_report,
        )

        self.assertFalse(report.accepted)
        self.assertEqual(report.handoff_state, "not-ready")
        self.assertIn(
            "Autarkic Systems vertical demo: rejected",
            format_handoff_status(report),
        )

    def test_json_cli_reports_handoff_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_handoff_cli(
                ["--format", "json"],
                project_builder=build_project_report,
                vertical_demo_builder=build_vertical_demo_digest,
                submission_builder=build_submission_report,
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["handoff_state"], "ready")
        self.assertEqual(payload["github_submission"]["head"]["short"], "04158fc")
        self.assertEqual(payload["vertical_demo"], VERTICAL_DEMO_DIGEST)

    def test_refresh_remotes_cli_passes_refresh_to_submission_status(self):
        stdout = io.StringIO()
        runner = FakeGitRunner(GIT_OUTPUTS)

        with contextlib.redirect_stdout(stdout):
            exit_code = run_handoff_cli(
                ["--format", "json", "--refresh-remotes"],
                project_builder=build_project_report,
                vertical_demo_builder=build_vertical_demo_digest,
                submission_runner=runner,
                clock=lambda: 1779110300,
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertEqual(
            runner.commands[:2],
            [
                ("fetch", "fork", "main:refs/remotes/fork/main"),
                ("fetch", "origin", "main:refs/remotes/origin/main"),
            ],
        )
        self.assertTrue(payload["accepted"])
        self.assertTrue(payload["github_submission"]["remote_refresh"]["requested"])
        self.assertTrue(payload["github_submission"]["remote_refresh"]["accepted"])

    def test_module_execution_runs_live_handoff_report(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.handoff"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertIn(completed.returncode, {0, 1}, completed.stderr)
        self.assertIn("Autarkic Systems handoff:", completed.stdout)
        self.assertIn("Project status:", completed.stdout)
        self.assertIn("GitHub submission:", completed.stdout)


if __name__ == "__main__":
    unittest.main()
