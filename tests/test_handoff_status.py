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


FORMAL_CONFIDENCE_RESULTS = [
    {
        "subject": "AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_frontier_status",
        "accepted": True,
        "detail": "fixed-point construction frontier status accepted",
    },
    *[
        {
            "subject": f"formal-confidence-validation-{index}",
            "accepted": True,
            "detail": "validation accepted",
        }
        for index in range(18)
    ],
]
FORMAL_CONFIDENCE_VALIDATION_SUMMARY = {
    "accepted_validation_count": 19,
    "failed_validation_count": 0,
    "accepted_frontier_subjects": [
        "AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_frontier_status",
    ],
    "accepted_frontier_labels": [
        "fixed_point_construction_frontier_status",
    ],
}


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
    "formal_confidence": {
        "target_count": 1,
        "status_counts": {"blocked": 1},
        "results": FORMAL_CONFIDENCE_RESULTS,
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
    "formal_confidence_validation": FORMAL_CONFIDENCE_VALIDATION_SUMMARY,
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
    "evidence_trail": [
        {
            "role": "sequence-claim-manifest",
            "path": "claims/network_sequence_claims.json",
            "exists": True,
        },
        {
            "role": "sequence-proof-certificates",
            "path": "claims/network_sequence_proof_certificates.json",
            "exists": True,
        },
        {
            "role": "sequence-language",
            "path": "language/network_sequence_claim_language.json",
            "exists": True,
        },
        {
            "role": "sequence-claim-validator",
            "path": "autarkic_systems/network_sequence_claims.py",
            "exists": True,
        },
        {
            "role": "sequence-witness",
            "path": "autarkic_systems/network_sequence.py",
            "exists": True,
        },
        {
            "role": "sequence-trace",
            "path": "schematics/sequences/post_handoff_signal_sequence_trace.json",
            "exists": True,
        },
        {
            "role": "sequence-svg",
            "path": "schematics/sequences/post_handoff_signal_sequence_trace.svg",
            "exists": True,
        },
        {
            "role": "chain-bundle",
            "path": "evidence/chains/neighbor_delivery_chain_bundle.json",
            "exists": True,
        },
    ],
    "missing_evidence_paths": [],
    "validation_subjects": [
        "schema",
        "sequence-claim-example",
        "sequence-proof-certificate",
        "sequence-language",
        "sequence-witness",
        "sequence-trace",
        "sequence-svg",
        "underlying-chain-bundles",
        "source-statuses",
        "boundary",
    ],
    "reproduction_commands": [
        {
            "label": "vertical-demo",
            "command": "python -m autarkic_systems.vertical_demo",
        },
        {
            "label": "sequence-demo-json",
            "command": "python -m autarkic_systems.network_sequence_demo --format json",
        },
        {
            "label": "project-status-summary",
            "command": "python -m autarkic_systems.project_status --format summary",
        },
        {
            "label": "handoff-refresh",
            "command": "python -m autarkic_systems.handoff --refresh-remotes",
        },
    ],
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
    (
        "reflog",
        "show",
        "--date=unix",
        "-1",
        "--format=%cd",
        "refs/remotes/origin/main",
    ): "1779110120",
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
    origin_main_ref_freshness={
        "state": "fresh",
        "checked_ref": "refs/remotes/origin/main",
        "updated_at_unix": 1779110120,
        "age_seconds": 180,
        "max_age_seconds": 86400,
    },
    head_behind_origin_main_by=0,
    head_ahead_origin_main_by=191,
    tracking_issue_url=DEFAULT_TRACKING_ISSUE_URL,
)

SOURCE_SUBMISSION_REPORT = GitHubSubmissionStatus(
    branch="main",
    head_commit="04158fc29229d091f616734725be3c8f54198200",
    head_short="04158fc",
    origin_url="https://github.com/jpt4/as.git",
    fork_url="https://github.com/Sean-Kenneth-Doherty/as.git",
    origin_main_commit="04158fc29229d091f616734725be3c8f54198200",
    origin_main_short="04158fc",
    fork_main_commit="df6de62ca82d88fd2b8aee0a1c25d7dfdaa8a67d",
    fork_main_short="df6de62",
    fork_main_ref_freshness={
        "state": "fresh",
        "checked_ref": "refs/remotes/fork/main",
        "updated_at_unix": 1779110000,
        "age_seconds": 300,
        "max_age_seconds": 86400,
    },
    origin_main_ref_freshness={
        "state": "fresh",
        "checked_ref": "refs/remotes/origin/main",
        "updated_at_unix": 1779110120,
        "age_seconds": 180,
        "max_age_seconds": 86400,
    },
    head_behind_origin_main_by=0,
    head_ahead_origin_main_by=0,
    tracking_issue_url=DEFAULT_TRACKING_ISSUE_URL,
)


def build_project_report():
    return PROJECT_REPORT


def build_submission_report():
    return SUBMISSION_REPORT


def build_source_submission_report():
    return SOURCE_SUBMISSION_REPORT


def build_vertical_demo_digest(project_status=None):
    return VERTICAL_DEMO_DIGEST


def rejected_suite_selection():
    return {
        "accepted": False,
        "command": (
            "python -m autarkic_systems.test_suite_selection "
            "--list-suites --format json"
        ),
        "selected_suite_commands": {},
        "error": "suite manifest not found",
    }


class HandoffStatusTests(unittest.TestCase):
    def test_handoff_reuses_project_status_for_vertical_demo(self):
        calls = {"project_status": 0, "vertical_demo_project_status": None}

        def counted_project_report():
            calls["project_status"] += 1
            return PROJECT_REPORT

        def vertical_demo_from_handoff_project_status(*, project_status):
            calls["vertical_demo_project_status"] = project_status
            return VERTICAL_DEMO_DIGEST

        report = build_handoff_status(
            project_builder=counted_project_report,
            vertical_demo_builder=vertical_demo_from_handoff_project_status,
            submission_builder=build_submission_report,
        )
        payload = handoff_status_payload(report)

        self.assertEqual(calls["project_status"], 1)
        self.assertIs(calls["vertical_demo_project_status"], PROJECT_REPORT)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["project_status"], PROJECT_REPORT)
        self.assertEqual(payload["vertical_demo"], VERTICAL_DEMO_DIGEST)
        self.assertIn("Autarkic Systems summary: accepted", report.project_summary)
        self.assertIn(
            "Autarkic Systems vertical demo: accepted",
            report.vertical_demo_summary,
        )

    def test_handoff_accepts_source_origin_submission(self):
        report = build_handoff_status(
            project_builder=build_project_report,
            vertical_demo_builder=build_vertical_demo_digest,
            submission_builder=build_source_submission_report,
        )
        payload = handoff_status_payload(report)
        text = format_handoff_status(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["handoff_state"], "ready")
        self.assertEqual(
            payload["github_submission"]["submission_state"],
            "submitted-to-origin",
        )
        self.assertIn("GitHub submission status: submitted-to-origin", text)
        self.assertIn("origin/main: matches HEAD (04158fc)", text)

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
        self.assertEqual(
            payload["vertical_demo"]["reproduction_commands"][-1]["command"],
            "python -m autarkic_systems.handoff --refresh-remotes",
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
        self.assertIn(
            "Formal confidence: 1 target; blocked=1",
            payload["project_summary"],
        )
        self.assertIn(
            "Formal confidence validation: 19 accepted, 0 failed; "
            "fixed_point_construction_frontier_status accepted",
            payload["project_summary"],
        )
        self.assertEqual(payload["project_status"], PROJECT_REPORT)
        self.assertEqual(payload["github_submission"]["submission_state"], "submitted-to-fork")
        self.assertEqual(payload["github_submission"]["head"]["short"], "04158fc")
        self.assertEqual(
            payload["github_submission"]["head"]["fork_commit_url"],
            "https://github.com/Sean-Kenneth-Doherty/as/commit/"
            "04158fc29229d091f616734725be3c8f54198200",
        )
        self.assertEqual(
            payload["github_submission"]["fork_main"]["web_url"],
            "https://github.com/Sean-Kenneth-Doherty/as/tree/main",
        )
        self.assertEqual(
            payload["github_submission"]["fork_main"]["compare_url"],
            "https://github.com/Sean-Kenneth-Doherty/as/compare/"
            "1a2fc06b75f5d33aee6655956c2a56df07a7bfb0..."
            "04158fc29229d091f616734725be3c8f54198200",
        )
        self.assertEqual(
            payload["github_submission"]["origin_main"]["web_url"],
            "https://github.com/jpt4/as/tree/main",
        )
        self.assertEqual(
            payload["github_submission"]["fork_main"]["remote_ref_freshness"]["state"],
            "fresh",
        )
        self.assertEqual(
            payload["github_submission"]["origin_main"]["remote_ref_freshness"]["state"],
            "fresh",
        )

    def test_handoff_payload_includes_suite_selection_evidence(self):
        report = build_handoff_status(
            project_builder=build_project_report,
            vertical_demo_builder=build_vertical_demo_digest,
            submission_builder=build_submission_report,
        )

        payload = handoff_status_payload(report)
        suite_selection = payload["suite_selection"]
        suites = suite_selection["suites"]

        self.assertTrue(payload["accepted"])
        self.assertTrue(suite_selection["accepted"])
        self.assertEqual(
            suite_selection["command"],
            "python -m autarkic_systems.test_suite_selection "
            "--list-suites --format json",
        )
        self.assertEqual(
            suite_selection["selectable_suites"],
            ["fast", "extended-fixed-point", "all"],
        )
        self.assertEqual(
            set(suites),
            {"fast", "extended-fixed-point", "all"},
        )
        self.assertGreater(suites["fast"]["module_count"], 0)
        self.assertGreater(suites["extended-fixed-point"]["module_count"], 0)
        self.assertEqual(
            suites["all"]["module_count"],
            suites["fast"]["module_count"]
            + suites["extended-fixed-point"]["module_count"],
        )
        for suite_name in suite_selection["selectable_suites"]:
            self.assertEqual(suites[suite_name]["suite"], suite_name)
            self.assertEqual(
                suite_selection["selected_suite_commands"][suite_name],
                f"python -m autarkic_systems.test_suite_selection --suite {suite_name}",
            )
            self.assertEqual(
                suites[suite_name]["command"]["argv"][:3],
                ["python", "-m", "unittest"],
            )
            self.assertEqual(
                suites[suite_name]["command"]["module_count"],
                suites[suite_name]["module_count"],
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
        self.assertIn("Reproduce:", text)
        self.assertIn(
            "- handoff-refresh: python -m autarkic_systems.handoff --refresh-remotes",
            text,
        )
        self.assertIn("GitHub submission:", text)
        self.assertIn("GitHub submission status: submitted-to-fork", text)
        self.assertIn(
            "Fork commit: https://github.com/Sean-Kenneth-Doherty/as/commit/"
            "04158fc29229d091f616734725be3c8f54198200",
            text,
        )
        self.assertIn(
            "Fork main: https://github.com/Sean-Kenneth-Doherty/as/tree/main",
            text,
        )
        self.assertIn(
            "Fork compare: https://github.com/Sean-Kenneth-Doherty/as/compare/"
            "1a2fc06b75f5d33aee6655956c2a56df07a7bfb0..."
            "04158fc29229d091f616734725be3c8f54198200",
            text,
        )
        self.assertIn("fork/main: matches HEAD (04158fc)", text)
        self.assertIn("fork/main freshness: fresh (300s old, max 86400s)", text)
        self.assertIn("origin/main: HEAD ahead by 191 commits", text)
        self.assertIn("origin/main freshness: fresh (180s old, max 86400s)", text)
        self.assertIn("Origin main: https://github.com/jpt4/as/tree/main", text)

    def test_handoff_text_renders_suite_selection_section(self):
        report = build_handoff_status(
            project_builder=build_project_report,
            vertical_demo_builder=build_vertical_demo_digest,
            submission_builder=build_submission_report,
        )

        text = format_handoff_status(report)

        self.assertIn("Suite selection:", text)
        self.assertIn(
            "Suite index: python -m autarkic_systems.test_suite_selection "
            "--list-suites --format json",
            text,
        )
        self.assertRegex(
            text,
            r"- fast: \d+ modules; "
            r"python -m autarkic_systems\.test_suite_selection --suite fast",
        )
        self.assertRegex(
            text,
            r"- extended-fixed-point: \d+ modules; "
            r"python -m autarkic_systems\.test_suite_selection "
            r"--suite extended-fixed-point",
        )
        self.assertRegex(
            text,
            r"- all: \d+ modules; "
            r"python -m autarkic_systems\.test_suite_selection --suite all",
        )
        self.assertLess(
            text.index("Vertical demo:"),
            text.index("Suite selection:"),
        )
        self.assertLess(
            text.index("Suite selection:"),
            text.index("GitHub submission:"),
        )

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
            origin_main_ref_freshness=SUBMISSION_REPORT.origin_main_ref_freshness,
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
            vertical_demo_builder=lambda project_status=None: rejected_demo,
            submission_builder=build_submission_report,
        )

        self.assertFalse(report.accepted)
        self.assertEqual(report.handoff_state, "not-ready")
        self.assertIn(
            "Autarkic Systems vertical demo: rejected",
            format_handoff_status(report),
        )

    def test_handoff_rejects_when_suite_selection_rejects(self):
        report = build_handoff_status(
            project_builder=build_project_report,
            vertical_demo_builder=build_vertical_demo_digest,
            submission_builder=build_submission_report,
            suite_selection_builder=rejected_suite_selection,
        )

        payload = handoff_status_payload(report)
        text = format_handoff_status(report)

        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["handoff_state"], "not-ready")
        self.assertFalse(payload["suite_selection"]["accepted"])
        self.assertEqual(payload["suite_selection"]["error"], "suite manifest not found")
        self.assertIn("Autarkic Systems handoff: not-ready", text)
        self.assertIn("Suite selection:", text)
        self.assertIn("Status: rejected (suite manifest not found)", text)

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
        self.assertTrue(payload["suite_selection"]["accepted"])

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
        self.assertIn("Suite selection:", completed.stdout)
        self.assertIn("GitHub submission:", completed.stdout)


if __name__ == "__main__":
    unittest.main()
