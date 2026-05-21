import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems.command_runtime_frontier import (
    COMMAND_RUNTIME_FRONTIER_SCHEMA_VERSION,
    build_command_runtime_frontier_report,
    format_command_runtime_frontier_report,
    run_command_runtime_frontier_cli,
)


IMPLEMENTED_COMMANDS = ["write-buf-zero", "write-buf-one"]
PRESERVED_UNSUPPORTED_COMMANDS = ["standard-signal"]
EVIDENCE_BY_CASE = {
    "recipient-write-buffer-zero": "evidence/recipient_write_buffer_command_message_bundle.json",
    "recipient-write-buffer-one": "evidence/recipient_write_buffer_command_message_bundle.json",
    "self-mailbox-write-buffer-one": "evidence/self_mailbox_write_buffer_bundle.json",
    "self-command-buffer-write-buffer-one": "evidence/self_command_buffer_write_buffer_bundle.json",
    "recipient-standard-signal": "evidence/recipient_non_init_command_rejection_bundle.json",
    "self-mailbox-standard-signal": "evidence/self_mailbox_unsupported_bundle.json",
    "self-command-buffer-standard-signal": "evidence/command_buffer_unsupported_bundle.json",
}
EXPECTED_STATUS_BY_CASE = {
    "recipient-write-buffer-zero": "recipient-write-buffer-command-message-appended",
    "recipient-write-buffer-one": "recipient-write-buffer-command-message-appended",
    "self-mailbox-write-buffer-one": "self-mailbox-write-buffer-appended",
    "self-command-buffer-write-buffer-one": "stem-command-buffer-self-write-buffer-appended",
    "recipient-standard-signal": "rejected-input",
    "self-mailbox-standard-signal": "self-mailbox-unsupported",
    "self-command-buffer-standard-signal": "stem-buffer-appended",
}


class CommandRuntimeFrontierTests(unittest.TestCase):
    def test_default_report_accepts_source_status_and_runtime_cases(self):
        report = build_command_runtime_frontier_report()

        self.assertEqual(report["schema_version"], COMMAND_RUNTIME_FRONTIER_SCHEMA_VERSION)
        self.assertTrue(report["accepted"])
        self.assertTrue(report["source_status"]["accepted"])
        self.assertEqual(
            report["source_status"]["closure_summary"]["implemented_commands"],
            IMPLEMENTED_COMMANDS,
        )
        self.assertEqual(
            report["source_status"]["closure_summary"][
                "preserved_unsupported_commands"
            ],
            PRESERVED_UNSUPPORTED_COMMANDS,
        )
        self.assertFalse(
            report["source_status"]["closure_summary"]["execution_change_allowed"]
        )

        cases = {case["case_id"]: case for case in report["runtime_cases"]}
        self.assertEqual(set(cases), set(EXPECTED_STATUS_BY_CASE))
        for case_id, expected_status in EXPECTED_STATUS_BY_CASE.items():
            with self.subTest(case_id=case_id):
                case = cases[case_id]
                self.assertTrue(case["accepted"])
                self.assertEqual(case["expected_status"], expected_status)
                self.assertEqual(case["observed_status"], expected_status)
                self.assertEqual(case["evidence_bundle"], EVIDENCE_BY_CASE[case_id])

    def test_write_buffer_cases_expose_runtime_state_changes(self):
        report = build_command_runtime_frontier_report()
        cases = {case["case_id"]: case for case in report["runtime_cases"]}

        self.assertEqual(cases["recipient-write-buffer-zero"]["after"]["buffer"], [1, 0])
        self.assertEqual(cases["recipient-write-buffer-one"]["after"]["buffer"], [1, 0, 1])
        self.assertEqual(
            cases["self-mailbox-write-buffer-one"]["after"]["buffer"],
            [0, 1],
        )
        self.assertEqual(
            cases["self-command-buffer-write-buffer-one"]["after"]["buffer"],
            [1],
        )
        self.assertEqual(cases["recipient-write-buffer-zero"]["after"]["input"], ["_", "_", "_"])
        self.assertEqual(cases["self-mailbox-write-buffer-one"]["after"]["self_mailbox"], "_")

    def test_standard_signal_cases_remain_non_executing_boundaries(self):
        report = build_command_runtime_frontier_report()
        cases = {case["case_id"]: case for case in report["runtime_cases"]}

        self.assertEqual(cases["recipient-standard-signal"]["observed_status"], "rejected-input")
        self.assertEqual(cases["recipient-standard-signal"]["after"]["input"], ["_", "_", "_"])
        self.assertEqual(
            cases["self-mailbox-standard-signal"]["observed_status"],
            "self-mailbox-unsupported",
        )
        self.assertEqual(
            cases["self-mailbox-standard-signal"]["after"]["self_mailbox"],
            "standard-signal",
        )
        self.assertEqual(
            cases["self-command-buffer-standard-signal"]["observed_status"],
            "stem-buffer-appended",
        )
        self.assertEqual(
            cases["self-command-buffer-standard-signal"]["after"]["buffer"],
            [0, 0, 0, 0, 0],
        )

    def test_text_report_renders_source_closure_and_runtime_cases(self):
        report = build_command_runtime_frontier_report()

        text = format_command_runtime_frontier_report(report)

        self.assertIn("Command runtime frontier: accepted", text)
        self.assertIn("Source-status frontier: accepted", text)
        self.assertIn("Implemented commands: write-buf-zero, write-buf-one", text)
        self.assertIn("Preserved unsupported commands: standard-signal", text)
        self.assertIn(
            "recipient-write-buffer-zero: accepted; "
            "recipient-write-buffer-command-message-appended",
            text,
        )
        self.assertIn(
            "self-command-buffer-standard-signal: accepted; stem-buffer-appended",
            text,
        )

    def test_report_rejects_when_source_status_frontier_rejects(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing-source-status.json"

            report = build_command_runtime_frontier_report([missing])

        self.assertFalse(report["accepted"])
        self.assertFalse(report["source_status"]["accepted"])
        self.assertEqual(report["runtime_cases"], [])
        self.assertEqual(report["evidence_bundles"], [])
        self.assertEqual(
            report["source_status"]["closure_summary"]["safe_next_slice_state"],
            "unknown",
        )

    def test_json_cli_reports_runtime_frontier(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_command_runtime_frontier_cli(["--format", "json"])

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["accepted"])
        self.assertEqual(len(payload["runtime_cases"]), 7)
        self.assertEqual(
            payload["source_status"]["closure_summary"]["implemented_commands"],
            IMPLEMENTED_COMMANDS,
        )

    def test_module_execution_reports_runtime_frontier(self):
        import subprocess
        import sys

        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.command_runtime_frontier"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Command runtime frontier: accepted", completed.stdout)


if __name__ == "__main__":
    unittest.main()
