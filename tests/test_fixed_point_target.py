import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point
from autarkic_systems.fixed_point import (
    REQUIRED_WILLARD_ANCHORS,
    load_fixed_point_targets,
    validate_fixed_point_targets,
)


TARGETS = Path("claims/fixed_point_targets.json")
CODEBOOK = Path("language/formal_codebook.json")
SUBSTITUTION = Path("language/formal_substitution_examples.json")
QUOTATION = Path("language/formal_quotation_examples.json")
QUOTATION_SEQUENCE = Path("language/formal_quotation_sequence_examples.json")
CONSISTENCY = Path("claims/consistency_level_targets.json")
DEDUCTION = Path("claims/deduction_apparatus_targets.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointTargetTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_fixed_point_targets(TARGETS)

    def test_checked_in_manifest_selects_fixed_point_target(self):
        target = self.manifest.targets[0]

        self.assertEqual(self.manifest.schema_version, 1)
        self.assertEqual(self.manifest.target_set_id, "as-fixed-point-target-v1")
        self.assertEqual(self.manifest.codebook_path, str(CODEBOOK))
        self.assertEqual(self.manifest.substitution_examples_path, str(SUBSTITUTION))
        self.assertEqual(self.manifest.quotation_examples_path, str(QUOTATION))
        self.assertEqual(self.manifest.quotation_sequence_examples_path, str(QUOTATION_SEQUENCE))
        self.assertEqual(self.manifest.consistency_level_targets_path, str(CONSISTENCY))
        self.assertEqual(self.manifest.deduction_apparatus_targets_path, str(DEDUCTION))
        self.assertEqual(
            REQUIRED_WILLARD_ANCHORS,
            (
                "W2011-D3.4-GENERIC-CONFIGURATION",
                "W2011-D5.6-LEVEL-K-CONSISTENCY",
                "W2011-D5.7-SELFCONSK",
                "W2020-D3.2-SELF-JUSTIFYING-GENAC",
            ),
        )
        self.assertEqual(target.target_id, "AS-FIXED-POINT-SELFCONS1-TARGET")
        self.assertEqual(target.template_variable, "n")
        self.assertEqual(target.sentence_class, "pi1")
        self.assertEqual(target.status, "target-selected-not-constructed")
        self.assertIn("quotation-term-construction", target.required_future_work)
        self.assertNotIn("quotation-sequence-construction", target.required_future_work)
        self.assertIn("no diagonal lemma proof", target.non_claims)

    def test_checked_in_manifest_validates_dependencies_and_substitution(self):
        report = validate_fixed_point_targets(self.manifest, WILLARD_MAP)

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.target_count, 1)
        self.assertTrue(
            any(
                result.subject == "targets"
                and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_fixed_point_target(self):
        report = validate_fixed_point_targets(self.manifest, WILLARD_MAP)

        payload = fixed_point.fixed_point_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["target_set_id"], "as-fixed-point-target-v1")
        self.assertEqual(payload["target_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(
            payload["targets"][0]["target_id"],
            "AS-FIXED-POINT-SELFCONS1-TARGET",
        )
        self.assertEqual(payload["targets"][0]["template_variable"], "n")
        self.assertEqual(payload["targets"][0]["status"], "target-selected-not-constructed")
        self.assertEqual(payload["targets"][0]["expected_instance_code"], [41, 1, 22, 11, 1, 13, 12])

    def test_text_report_exposes_fixed_point_target(self):
        report = validate_fixed_point_targets(self.manifest, WILLARD_MAP)

        text = fixed_point.format_fixed_point_report(report)

        self.assertIn("Fixed-point targets: accepted", text)
        self.assertIn("AS-FIXED-POINT-SELFCONS1-TARGET", text)
        self.assertIn("Status: target-selected-not-constructed", text)
        self.assertIn("Template variable: n", text)
        self.assertNotIn("FAIL", text)

    def test_unknown_willard_anchor_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            targets_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["willard_anchor_ids"].append("W2099-UNKNOWN")
            targets_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_targets(targets_path)

            report = validate_fixed_point_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-willard-anchor", report.failed_subjects)
        self.assertTrue(
            any("unknown Willard anchor IDs: W2099-UNKNOWN" in result.detail for result in report.results)
        )

    def test_template_missing_target_variable_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            targets_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["template_node"] = {
                "kind": "pi1",
                "variable": "x",
                "body": {
                    "kind": "less_than",
                    "left": {"kind": "variable", "name": "x"},
                    "right": {"kind": "successor", "term": {"kind": "zero"}},
                },
            }
            targets_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_targets(targets_path)

            report = validate_fixed_point_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-template-variable", report.failed_subjects)
        self.assertTrue(
            any("template variable n is not free" in result.detail for result in report.results)
        )

    def test_expected_instance_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            targets_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["expected_instance_code"] = [99]
            targets_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_targets(targets_path)

            report = validate_fixed_point_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-instance", report.failed_subjects)
        self.assertTrue(
            any("expected instance code mismatch" in result.detail for result in report.results)
        )

    def test_proved_fixed_point_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            targets_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["status"] = "fixed-point-proved"
            targets_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_targets(targets_path)

            report = validate_fixed_point_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-status", report.failed_subjects)
        self.assertTrue(
            any("proved fixed points are not supported" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_targets(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = fixed_point.run_fixed_point_cli(
                ["--targets", str(TARGETS), "--willard-map", str(WILLARD_MAP)]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Fixed-point targets: accepted", output)

    def test_cli_returns_json_for_checked_in_targets(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = fixed_point.run_fixed_point_cli(
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
        self.assertEqual(payload["target_set_id"], "as-fixed-point-target-v1")

    def test_module_execution_runs_fixed_point_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.fixed_point"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Fixed-point targets: accepted", completed.stdout)

    def test_module_execution_runs_json_fixed_point_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point",
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
        self.assertEqual(payload["targets"][0]["template_variable"], "n")


if __name__ == "__main__":
    unittest.main()
