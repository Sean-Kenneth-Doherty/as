import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems.source_status import (
    SOURCE_STATUS_SCHEMA_VERSION,
    build_source_status_frontier_report,
    format_source_status_frontier_report,
    run_source_status_frontier_cli,
)


RECIPIENT_STATUS = Path("sources/recipient_non_init_command_source_status.json")
STANDARD_SIGNAL_STATUS = Path("sources/standard_signal_command_semantics_status.json")
WRITE_BUFFER_STATUS = Path("sources/write_buffer_command_semantics_status.json")
SAFE_NEXT_SLICE = "revisit-standard-signal-or-write-buffer-command-semantics"
BLOCKED_COMMANDS = ["standard-signal", "write-buf-zero", "write-buf-one"]


class SourceStatusFrontierCliTests(unittest.TestCase):
    def test_default_report_accepts_checked_in_source_status_frontier(self):
        report = build_source_status_frontier_report()

        self.assertEqual(report["schema_version"], SOURCE_STATUS_SCHEMA_VERSION)
        self.assertTrue(report["accepted"])
        frontier = report["frontier"]
        self.assertEqual(frontier["blocked_commands"], BLOCKED_COMMANDS)
        self.assertEqual(frontier["failed_subjects"], [])
        self.assertEqual(frontier["safe_next_slice"], SAFE_NEXT_SLICE)
        self.assertEqual(
            [source_status["path"] for source_status in frontier["source_statuses"]],
            [
                str(RECIPIENT_STATUS),
                str(STANDARD_SIGNAL_STATUS),
                str(WRITE_BUFFER_STATUS),
            ],
        )

    def test_text_report_renders_source_frontier_details(self):
        report = build_source_status_frontier_report()

        text = format_source_status_frontier_report(report)

        self.assertIn("AS source-status frontier: accepted", text)
        self.assertIn(
            "Blocked commands: standard-signal, write-buf-zero, write-buf-one",
            text,
        )
        self.assertIn("Resolution questions:", text)
        self.assertIn("Resolution question evidence:", text)
        self.assertIn("Resolved resolution questions:", text)
        self.assertIn(
            "recipient-surface: "
            "reject-recipient-standard-signal-command-message-as-non-init "
            "(sources/recipient_non_init_command_source_status.json)",
            text,
        )
        self.assertIn(
            "command-token-vs-binary-input: "
            "do-not-replay-ordinary-binary-input-standard-signal "
            "(sources/standard_signal_command_semantics_status.json)",
            text,
        )
        self.assertIn(
            "self-target-surface: "
            "preserve-self-target-standard-signal-as-unsupported "
            "(sources/standard_signal_command_semantics_status.json)",
            text,
        )
        self.assertIn(
            "recipient-surface: "
            "reject-recipient-write-buffer-command-message-as-non-init "
            "(sources/recipient_non_init_command_source_status.json)",
            text,
        )
        self.assertIn(
            "self-target-surface: "
            "preserve-self-target-write-buffer-as-unsupported "
            "(sources/write_buffer_command_semantics_status.json)",
            text,
        )
        self.assertNotIn("recipient-vs-stem-surface", text)
        self.assertIn(f"Safe next slice: {SAFE_NEXT_SLICE}", text)
        self.assertIn("Missing source-status files: none", text)
        self.assertIn("Invalid source-status files: none", text)

    def test_report_rejects_missing_source_status_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing-source-status.json"

            report = build_source_status_frontier_report([missing])

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["failed_subjects"], ["source-status-file"])
        self.assertEqual(
            report["frontier"]["missing_source_statuses"],
            [str(missing)],
        )

    def test_report_rejects_schema_invalid_source_status_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid = Path(tmp) / "invalid-source-status.json"
            invalid.write_text(
                json.dumps(
                    {
                        "decision": "drifted-source-status",
                        "safe_next_slice": "repair-source-status",
                    }
                ),
                encoding="utf-8",
            )

            report = build_source_status_frontier_report([invalid])

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["failed_subjects"], ["source-status-schema"])
        self.assertEqual(
            report["frontier"]["invalid_source_statuses"][0]["path"],
            str(invalid),
        )
        self.assertIn(
            "command fields must include at least one command token",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_report_rejects_unmatched_resolution_question_evidence_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid = Path(tmp) / "unmatched-evidence-id.json"
            invalid.write_text(
                json.dumps(
                    {
                        "decision": "do-not-implement-command-yet",
                        "safe_next_slice": "revisit-command-source-evidence",
                        "command": "standard-signal",
                        "as_boundary": "Keep this command blocked here.",
                        "required_resolution_questions": [
                            {
                                "question_id": "recipient-surface",
                                "summary": "Decide the recipient surface.",
                            }
                        ],
                        "resolution_question_evidence": [
                            {
                                "question_id": "recipent-surface",
                                "evidence": "Typo should not attach evidence.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = build_source_status_frontier_report([invalid])

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["failed_subjects"], ["source-status-schema"])
        self.assertIn(
            "match required_resolution_questions",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_report_rejects_missing_resolution_question_evidence_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid = Path(tmp) / "missing-evidence-coverage.json"
            invalid.write_text(
                json.dumps(
                    {
                        "decision": "do-not-implement-command-yet",
                        "safe_next_slice": "revisit-command-source-evidence",
                        "command": "standard-signal",
                        "as_boundary": "Keep this command blocked here.",
                        "required_resolution_questions": [
                            {
                                "question_id": "recipient-surface",
                                "summary": "Decide the recipient surface.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = build_source_status_frontier_report([invalid])

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["failed_subjects"], ["source-status-schema"])
        self.assertIn(
            "cover required_resolution_questions",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_report_rejects_overlapping_unresolved_and_resolved_question_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid = Path(tmp) / "overlapping-question-id.json"
            invalid.write_text(
                json.dumps(
                    {
                        "decision": "do-not-implement-command-yet",
                        "safe_next_slice": "revisit-command-source-evidence",
                        "command": "standard-signal",
                        "as_boundary": "Keep this command blocked here.",
                        "required_resolution_questions": [
                            {
                                "question_id": "recipient-surface",
                                "summary": "Decide the recipient surface.",
                            }
                        ],
                        "resolution_question_evidence": [
                            {
                                "question_id": "recipient-surface",
                                "evidence": "Evidence keeps unresolved shape valid.",
                            }
                        ],
                        "resolved_resolution_questions": [
                            {
                                "question_id": "recipient-surface",
                                "decision": "resolved",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = build_source_status_frontier_report([invalid])

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["failed_subjects"], ["source-status-schema"])
        self.assertIn(
            "cannot be both unresolved and resolved",
            report["frontier"]["invalid_source_statuses"][0]["error"],
        )

    def test_cli_returns_zero_for_checked_in_source_status_frontier(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_source_status_frontier_cli([])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("AS source-status frontier: accepted", output)
        self.assertIn("Resolution question evidence:", output)

    def test_cli_returns_json_for_checked_in_source_status_frontier(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_source_status_frontier_cli(["--format", "json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertEqual(payload["schema_version"], SOURCE_STATUS_SCHEMA_VERSION)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier"]["blocked_commands"], BLOCKED_COMMANDS)

    def test_cli_returns_one_for_missing_source_status_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing-source-status.json"
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = run_source_status_frontier_cli(
                    ["--source-status", str(missing)]
                )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1, output)
        self.assertIn("AS source-status frontier: rejected", output)
        self.assertIn("Missing source-status files:", output)

    def test_module_execution_runs_source_status_frontier_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.source_status"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("AS source-status frontier: accepted", completed.stdout)
        self.assertIn("Resolution question evidence:", completed.stdout)

    def test_module_execution_runs_json_source_status_frontier_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.source_status",
                "--format",
                "json",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier"]["safe_next_slice"], SAFE_NEXT_SLICE)


if __name__ == "__main__":
    unittest.main()
