import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems.project_status import (
    build_project_status_report,
    format_project_status_report,
    run_project_status_cli,
)


TRANSITION_REGISTRY = Path("evidence/manifest.json")
CHAIN_REGISTRY = Path("evidence/chains/manifest.json")
RECIPIENT_STATUS = Path("sources/recipient_non_init_command_source_status.json")
STANDARD_SIGNAL_STATUS = Path("sources/standard_signal_command_semantics_status.json")
WRITE_BUFFER_STATUS = Path("sources/write_buffer_command_semantics_status.json")
BLOCKED_COMMANDS = ["standard-signal", "write-buf-zero", "write-buf-one"]
SAFE_NEXT_SLICE = "revisit-standard-signal-or-write-buffer-command-semantics"


class ProjectStatusReportTests(unittest.TestCase):
    def test_status_payload_summarizes_evidence_registries_and_frontier(self):
        report = build_project_status_report()

        self.assertTrue(report["accepted"])
        self.assertEqual(
            report["transition_evidence"]["registry_id"],
            "transition-evidence-bundle-registry",
        )
        self.assertTrue(report["transition_evidence"]["accepted"])
        self.assertEqual(report["transition_evidence"]["bundle_count"], 8)
        self.assertEqual(
            report["chain_evidence"]["registry_id"],
            "transition-chain-evidence-bundle-registry",
        )
        self.assertTrue(report["chain_evidence"]["accepted"])
        self.assertEqual(report["chain_evidence"]["bundle_count"], 2)
        self.assertEqual(report["frontier"]["blocked_commands"], BLOCKED_COMMANDS)
        self.assertEqual(report["frontier"]["safe_next_slice"], SAFE_NEXT_SLICE)
        self.assertEqual(report["frontier"]["missing_source_statuses"], [])
        self.assertEqual(
            [item["path"] for item in report["frontier"]["source_statuses"]],
            [
                str(RECIPIENT_STATUS),
                str(STANDARD_SIGNAL_STATUS),
                str(WRITE_BUFFER_STATUS),
            ],
        )

    def test_text_status_names_green_evidence_and_blocked_commands(self):
        report = build_project_status_report()

        text = format_project_status_report(report)

        self.assertIn("Autarkic Systems project status: accepted", text)
        self.assertIn("Transition evidence: accepted (8 bundles)", text)
        self.assertIn("Chain evidence: accepted (2 bundles)", text)
        self.assertIn(
            "Blocked commands: standard-signal, write-buf-zero, write-buf-one",
            text,
        )
        self.assertIn(
            "Safe next slice: revisit-standard-signal-or-write-buffer-command-semantics",
            text,
        )
        self.assertIn("Missing source-status files: none", text)

    def test_json_cli_reports_project_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_project_status_cli(["--format", "json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["transition_evidence"]["bundle_count"], 8)
        self.assertEqual(payload["chain_evidence"]["bundle_count"], 2)
        self.assertEqual(payload["frontier"]["blocked_commands"], BLOCKED_COMMANDS)

    def test_missing_source_status_is_structured_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_status = Path(tmp) / "missing_status.json"

            report = build_project_status_report(
                source_status_paths=[missing_status],
            )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["frontier"]["blocked_commands"], [])
        self.assertEqual(
            report["frontier"]["missing_source_statuses"],
            [str(missing_status)],
        )
        self.assertEqual(report["frontier"]["source_statuses"], [])

    def test_missing_transition_registry_is_structured_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_registry = Path(tmp) / "missing_transition_manifest.json"

            report = build_project_status_report(
                transition_registry_path=missing_registry,
            )

        self.assertFalse(report["accepted"])
        self.assertFalse(report["transition_evidence"]["accepted"])
        self.assertEqual(report["transition_evidence"]["registry_id"], "")
        self.assertEqual(report["transition_evidence"]["path"], str(missing_registry))
        self.assertEqual(report["transition_evidence"]["bundle_count"], 0)
        self.assertEqual(
            report["transition_evidence"]["failed_subjects"],
            ["registry-file"],
        )
        self.assertIn(
            str(missing_registry),
            report["transition_evidence"]["results"][0]["detail"],
        )
        self.assertTrue(report["chain_evidence"]["accepted"])

    def test_missing_chain_registry_is_structured_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_registry = Path(tmp) / "missing_chain_manifest.json"

            report = build_project_status_report(
                chain_registry_path=missing_registry,
            )

        self.assertFalse(report["accepted"])
        self.assertTrue(report["transition_evidence"]["accepted"])
        self.assertFalse(report["chain_evidence"]["accepted"])
        self.assertEqual(report["chain_evidence"]["registry_id"], "")
        self.assertEqual(report["chain_evidence"]["path"], str(missing_registry))
        self.assertEqual(report["chain_evidence"]["bundle_count"], 0)
        self.assertEqual(
            report["chain_evidence"]["failed_subjects"],
            ["registry-file"],
        )

    def test_json_cli_reports_missing_registry_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_registry = Path(tmp) / "missing_transition_manifest.json"
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = run_project_status_cli(
                    [
                        "--transition-registry",
                        str(missing_registry),
                        "--format",
                        "json",
                    ]
                )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1, payload)
        self.assertFalse(payload["accepted"])
        self.assertEqual(
            payload["transition_evidence"]["failed_subjects"],
            ["registry-file"],
        )
        self.assertEqual(
            payload["transition_evidence"]["path"],
            str(missing_registry),
        )

    def test_invalid_transition_registry_is_structured_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_registry = Path(tmp) / "invalid_transition_manifest.json"
            invalid_registry.write_text("{not-json", encoding="utf-8")

            report = build_project_status_report(
                transition_registry_path=invalid_registry,
            )

        self.assertFalse(report["accepted"])
        self.assertFalse(report["transition_evidence"]["accepted"])
        self.assertEqual(report["transition_evidence"]["path"], str(invalid_registry))
        self.assertEqual(report["transition_evidence"]["bundle_count"], 0)
        self.assertEqual(
            report["transition_evidence"]["failed_subjects"],
            ["registry-json"],
        )

    def test_invalid_chain_registry_is_structured_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_registry = Path(tmp) / "invalid_chain_manifest.json"
            invalid_registry.write_text("{}", encoding="utf-8")

            report = build_project_status_report(
                chain_registry_path=invalid_registry,
            )

        self.assertFalse(report["accepted"])
        self.assertTrue(report["transition_evidence"]["accepted"])
        self.assertFalse(report["chain_evidence"]["accepted"])
        self.assertEqual(report["chain_evidence"]["path"], str(invalid_registry))
        self.assertEqual(report["chain_evidence"]["bundle_count"], 0)
        self.assertEqual(
            report["chain_evidence"]["failed_subjects"],
            ["registry-json"],
        )

    def test_text_status_names_missing_registry_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_registry = Path(tmp) / "missing_chain_manifest.json"

            report = build_project_status_report(
                chain_registry_path=missing_registry,
            )

        text = format_project_status_report(report)
        self.assertIn("Autarkic Systems project status: rejected", text)
        self.assertIn("Chain evidence: rejected (0 bundles)", text)
        self.assertIn(f"Missing registry files: {missing_registry}", text)

    def test_text_status_names_invalid_registry_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            invalid_registry = Path(tmp) / "invalid_chain_manifest.json"
            invalid_registry.write_text("{}", encoding="utf-8")

            report = build_project_status_report(
                chain_registry_path=invalid_registry,
            )

        text = format_project_status_report(report)
        self.assertIn("Autarkic Systems project status: rejected", text)
        self.assertIn("Chain evidence: rejected (0 bundles)", text)
        self.assertIn(f"Invalid registry files: {invalid_registry}", text)

    def test_module_execution_runs_text_status_report(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.project_status"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Autarkic Systems project status: accepted", completed.stdout)
        self.assertIn("Transition evidence: accepted (8 bundles)", completed.stdout)
        self.assertIn("Chain evidence: accepted (2 bundles)", completed.stdout)


if __name__ == "__main__":
    unittest.main()
