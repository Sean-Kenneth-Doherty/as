import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems.evidence_bundle import (
    format_registry_validation_report,
    load_evidence_bundle_registry,
    run_evidence_bundle_cli,
    validate_evidence_bundle_registry,
)


REGISTRY = Path("evidence/manifest.json")


class EvidenceBundleCliTests(unittest.TestCase):
    def test_report_formats_successful_registry_validation(self):
        registry = load_evidence_bundle_registry(REGISTRY)
        results = validate_evidence_bundle_registry(registry)

        report = format_registry_validation_report(registry, results)

        self.assertIn(
            "Evidence bundle registry: transition-evidence-bundle-registry",
            report,
        )
        self.assertIn("OK registry-schema: registry schema accepted", report)
        self.assertIn("OK registry-bundle-validation: validated 3 bundles", report)
        self.assertIn("OK registry-completeness:", report)
        self.assertNotIn("FAIL", report)

    def test_cli_returns_zero_for_checked_in_registry(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_evidence_bundle_cli(["--registry", str(REGISTRY)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Evidence bundle registry:", output)
        self.assertIn("OK registry-bundle-validation", output)

    def test_cli_returns_one_for_missing_registered_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = Path(tmp) / "manifest.json"
            registry_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "registry_id": "drifted-registry",
                        "reviewed_at": "2026-05-17",
                        "purpose": "Exercise CLI failure reporting.",
                        "bundles": [
                            {
                                "bundle_id": "missing-bundle",
                                "path": "evidence/does-not-exist.json",
                                "claim_id": "UC-UNKNOWN",
                                "expected_status": "missing",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = run_evidence_bundle_cli(
                    ["--registry", str(registry_path)]
                )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1, output)
        self.assertIn("FAIL registry-bundle-paths", output)
        self.assertIn("missing bundle", output)

    def test_module_execution_runs_registry_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.evidence_bundle",
                "--registry",
                str(REGISTRY),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Evidence bundle registry:", completed.stdout)
        self.assertIn("OK registry-bundle-validation", completed.stdout)


if __name__ == "__main__":
    unittest.main()
