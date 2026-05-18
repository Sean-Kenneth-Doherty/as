import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import deduction_apparatus
from autarkic_systems.deduction_apparatus import (
    REQUIRED_CERTIFICATE_SURFACES,
    REQUIRED_WILLARD_ANCHORS,
    load_deduction_apparatus_targets,
    validate_deduction_apparatus_targets,
)


TARGETS = Path("claims/deduction_apparatus_targets.json")
FORMAL_CODEBOOK = Path("language/formal_codebook.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")
TRANSITION_CERTIFICATES = Path("claims/proof_certificates.json")


class DeductionApparatusTargetTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_deduction_apparatus_targets(TARGETS)

    def test_checked_in_manifest_selects_predicate_result_apparatus(self):
        target = self.manifest.targets[0]

        self.assertEqual(self.manifest.schema_version, 1)
        self.assertEqual(
            self.manifest.target_set_id,
            "as-deduction-apparatus-target-v1",
        )
        self.assertEqual(self.manifest.formal_codebook_path, str(FORMAL_CODEBOOK))
        self.assertEqual(
            REQUIRED_WILLARD_ANCHORS,
            (
                "W2011-D3.4-GENERIC-CONFIGURATION",
                "W2016-D3.2-HILBERT-STYLE",
                "W2016-D3.4-SELF-JUSTIFYING-CONFIGURATION",
                "W2020-D3.2-SELF-JUSTIFYING-GENAC",
                "W2020-SEC4-TAB-XTAB-TAB1",
                "W2020-T4.4-T4.5-LEM-BOUNDARY",
            ),
        )
        self.assertEqual(
            REQUIRED_CERTIFICATE_SURFACES,
            ("transition", "transition-chain", "network-sequence"),
        )
        self.assertEqual(
            target.target_id,
            "AS-DEDUCTION-APPARATUS-PREDICATE-RESULT",
        )
        self.assertEqual(
            target.apparatus_id,
            "as-local-predicate-result-proof-certificate-checker",
        )
        self.assertEqual(target.family, "as-local-certificate-checker")
        self.assertEqual(target.rule, "predicate-result")
        self.assertEqual(target.status, "target-selected-not-self-justifying")
        self.assertIn("hilbert-style", target.excluded_apparatuses)
        self.assertIn("semantic-tableau", target.excluded_apparatuses)
        self.assertIn("no theorem prover", target.non_claims)

    def test_checked_in_manifest_validates_current_certificate_surfaces(self):
        report = validate_deduction_apparatus_targets(
            self.manifest,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.total_step_count, 52)
        self.assertEqual(
            report.combined_rule_counts,
            {"manifest-example": 0, "predicate-result": 52},
        )
        self.assertTrue(
            any(
                result.subject == "certificate_surfaces"
                and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_apparatus_target_and_rule_counts(self):
        report = validate_deduction_apparatus_targets(
            self.manifest,
            WILLARD_MAP,
        )

        payload = deduction_apparatus.deduction_apparatus_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["target_set_id"], "as-deduction-apparatus-target-v1")
        self.assertEqual(payload["target_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["total_step_count"], 52)
        self.assertEqual(payload["combined_rule_counts"]["predicate-result"], 52)
        self.assertEqual(payload["combined_rule_counts"]["manifest-example"], 0)
        self.assertEqual(
            payload["targets"][0]["apparatus_id"],
            "as-local-predicate-result-proof-certificate-checker",
        )

    def test_text_report_exposes_apparatus_target(self):
        report = validate_deduction_apparatus_targets(
            self.manifest,
            WILLARD_MAP,
        )

        text = deduction_apparatus.format_deduction_apparatus_report(report)

        self.assertIn("Deduction apparatus targets: accepted", text)
        self.assertIn("AS-DEDUCTION-APPARATUS-PREDICATE-RESULT", text)
        self.assertIn("Rule counts: predicate-result=52, manifest-example=0", text)
        self.assertNotIn("FAIL", text)

    def test_unknown_willard_anchor_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            targets_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["willard_anchor_ids"].append("W2099-UNKNOWN")
            targets_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_deduction_apparatus_targets(targets_path)

            report = validate_deduction_apparatus_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("deduction-apparatus-willard-anchor", report.failed_subjects)
        self.assertTrue(
            any("unknown Willard anchor IDs: W2099-UNKNOWN" in result.detail for result in report.results)
        )

    def test_missing_certificate_surface_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            targets_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["certificate_surfaces"] = [
                surface
                for surface in data["certificate_surfaces"]
                if surface["surface_id"] != "network-sequence"
            ]
            targets_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_deduction_apparatus_targets(targets_path)

            report = validate_deduction_apparatus_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("deduction-apparatus-surface", report.failed_subjects)
        self.assertTrue(
            any("missing certificate surfaces: network-sequence" in result.detail for result in report.results)
        )

    def test_non_predicate_result_rule_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            targets_path = Path(tmp) / "targets.json"
            certificates_path = Path(tmp) / "certificates.json"
            target_data = json.loads(TARGETS.read_text(encoding="utf-8"))
            certificate_data = json.loads(
                TRANSITION_CERTIFICATES.read_text(encoding="utf-8")
            )
            certificate_data["certificates"][0]["steps"][0]["rule"] = "manifest-example"
            certificates_path.write_text(
                json.dumps(certificate_data),
                encoding="utf-8",
            )
            target_data["certificate_surfaces"][0]["certificates_path"] = str(
                certificates_path
            )
            targets_path.write_text(json.dumps(target_data), encoding="utf-8")
            manifest = load_deduction_apparatus_targets(targets_path)

            report = validate_deduction_apparatus_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("deduction-apparatus-proof-rule", report.failed_subjects)
        self.assertTrue(
            any("non-predicate-result rules: manifest-example" in result.detail for result in report.results)
        )

    def test_self_justifying_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            targets_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["status"] = "self-justifying-proved"
            targets_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_deduction_apparatus_targets(targets_path)

            report = validate_deduction_apparatus_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("deduction-apparatus-status", report.failed_subjects)
        self.assertTrue(
            any("self-justifying status is not supported" in result.detail for result in report.results)
        )

    def test_hilbert_family_overclaim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            targets_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["family"] = "hilbert-style"
            targets_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_deduction_apparatus_targets(targets_path)

            report = validate_deduction_apparatus_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("deduction-apparatus-family", report.failed_subjects)
        self.assertTrue(
            any("Hilbert/tableau apparatus overclaim" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_targets(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = deduction_apparatus.run_deduction_apparatus_cli(
                ["--targets", str(TARGETS), "--willard-map", str(WILLARD_MAP)]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Deduction apparatus targets: accepted", output)

    def test_cli_returns_json_for_checked_in_targets(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = deduction_apparatus.run_deduction_apparatus_cli(
                [
                    "--targets",
                    str(TARGETS),
                    "--willard-map",
                    str(WILLARD_MAP),
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["total_step_count"], 52)

    def test_module_execution_runs_deduction_apparatus_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.deduction_apparatus"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Deduction apparatus targets: accepted", completed.stdout)

    def test_module_execution_runs_json_deduction_apparatus_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.deduction_apparatus",
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
        self.assertEqual(payload["target_set_id"], "as-deduction-apparatus-target-v1")


if __name__ == "__main__":
    unittest.main()
