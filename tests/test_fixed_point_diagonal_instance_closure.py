import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_diagonal_instance_closure
from autarkic_systems.fixed_point_diagonal_instance_closure import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SOURCE_KINDS,
    load_fixed_point_diagonal_instance_closure,
    validate_fixed_point_diagonal_instance_closure,
)


CLOSURE = Path("claims/fixed_point_diagonal_instance_closure.json")
LANGUAGE = Path("language/formal_arithmetic_language.json")
CODEBOOK = Path("language/formal_codebook.json")
FIXED_POINT_TARGETS = Path("claims/fixed_point_targets.json")
DIAGONAL_CONSTRUCTIONS = Path("claims/diagonal_construction_targets.json")
BRIDGES = Path("claims/fixed_point_equation_bridge_targets.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointDiagonalInstanceClosureTests(unittest.TestCase):
    def setUp(self):
        self.closure = load_fixed_point_diagonal_instance_closure(CLOSURE)

    def test_checked_in_manifest_names_closure_domain(self):
        self.assertEqual(self.closure.schema_version, 1)
        self.assertEqual(
            self.closure.closure_set_id,
            "as-fixed-point-diagonal-instance-closure-v1",
        )
        self.assertEqual(self.closure.formal_language_path, str(LANGUAGE))
        self.assertEqual(self.closure.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.closure.fixed_point_targets_path,
            str(FIXED_POINT_TARGETS),
        )
        self.assertEqual(
            self.closure.diagonal_construction_targets_path,
            str(DIAGONAL_CONSTRUCTIONS),
        )
        self.assertEqual(
            self.closure.fixed_point_equation_bridge_targets_path,
            str(BRIDGES),
        )
        self.assertEqual(self.closure.expected_closure_count, 1)
        self.assertEqual(self.closure.expected_diagonal_instance_code_length, 296)
        self.assertEqual(
            tuple(self.closure.expected_diagonal_instance_code_prefix),
            (41, 1, 22, 11, 1, 18, 17, 13, 13, 13, 13, 13),
        )
        self.assertEqual(REQUIRED_SOURCE_KINDS, ("diagonal-instance",))
        self.assertEqual(
            REQUIRED_FUTURE_WORK,
            (
                "substitution-representability-proof",
                "substitution-graph-correctness-proof",
                "bridge-equality-proof",
                "fixed-point-equation-proof",
                "self-consistency-theorem",
            ),
        )
        self.assertEqual(
            REQUIRED_NON_CLAIMS,
            (
                "no substitution representability proof",
                "no substitution graph correctness proof",
                "no bridge equality proof",
                "no fixed-point equation proof",
                "no arithmetized proof predicate",
                "no self-consistency theorem",
            ),
        )

    def test_checked_in_manifest_validates_closure_domain(self):
        report = validate_fixed_point_diagonal_instance_closure(
            self.closure,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.closure_count, 1)
        self.assertEqual(report.source_kind_counts["diagonal-instance"], 1)

    def test_json_payload_exposes_closure_point(self):
        report = validate_fixed_point_diagonal_instance_closure(
            self.closure,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_diagonal_instance_closure
            .fixed_point_diagonal_instance_closure_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["closure_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["source_kind_counts"]["diagonal-instance"], 1)
        closure = payload["closures"][0]
        self.assertEqual(
            closure["closure_id"],
            "AS-FIXED-POINT-DIAGONAL-INSTANCE-CLOSURE",
        )
        self.assertTrue(closure["observed_diagonal_instance_closed"])
        self.assertTrue(closure["observed_codebook_roundtrip"])
        self.assertTrue(closure["observed_target_skeleton_preserved"])
        self.assertTrue(
            closure["observed_diagonal_slot_is_quoted_seed_substitution"]
        )
        self.assertTrue(closure["observed_bridge_matches_diagonal_instance"])
        self.assertTrue(closure["observed_bridge_target_closed"])

    def test_text_report_exposes_closure_boundary(self):
        report = validate_fixed_point_diagonal_instance_closure(
            self.closure,
            WILLARD_MAP,
        )

        text = (
            fixed_point_diagonal_instance_closure
            .format_fixed_point_diagonal_instance_closure_report(report)
        )

        self.assertIn("Fixed-point diagonal instance closure: accepted", text)
        self.assertIn("Closures: 1", text)
        self.assertIn("diagonal-instance=1", text)
        self.assertIn("Closure failures: none", text)
        self.assertNotIn("FAIL", text)

    def test_stale_closure_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "closure.json"
            data = json.loads(CLOSURE.read_text(encoding="utf-8"))
            data["expected_closure_count"] = 2
            path.write_text(json.dumps(data), encoding="utf-8")
            closure = load_fixed_point_diagonal_instance_closure(path)

            report = validate_fixed_point_diagonal_instance_closure(
                closure,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-diagonal-instance-closure-count",
            report.failed_subjects,
        )
        self.assertTrue(
            any("closure count mismatch" in result.detail for result in report.results)
        )

    def test_stale_diagonal_instance_length_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "closure.json"
            data = json.loads(CLOSURE.read_text(encoding="utf-8"))
            data["expected_diagonal_instance_code_length"] = 297
            path.write_text(json.dumps(data), encoding="utf-8")
            closure = load_fixed_point_diagonal_instance_closure(path)

            report = validate_fixed_point_diagonal_instance_closure(
                closure,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-diagonal-instance-closure-length",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                "diagonal instance length mismatch" in result.detail
                for result in report.results
            )
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "closure.json"
            data = json.loads(CLOSURE.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            closure = load_fixed_point_diagonal_instance_closure(path)

            report = validate_fixed_point_diagonal_instance_closure(
                closure,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-diagonal-instance-closure-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_closure_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_diagonal_instance_closure
                .run_fixed_point_diagonal_instance_closure_cli(
                    [
                        "--closure",
                        str(CLOSURE),
                        "--willard-map",
                        str(WILLARD_MAP),
                    ]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Fixed-point diagonal instance closure: accepted", output)

    def test_cli_returns_json_for_checked_in_closure_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_diagonal_instance_closure
                .run_fixed_point_diagonal_instance_closure_cli(
                    [
                        "--closure",
                        str(CLOSURE),
                        "--willard-map",
                        str(WILLARD_MAP),
                        "--format",
                        "json",
                    ]
                )
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["closure_count"], 1)

    def test_module_execution_runs_closure_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.fixed_point_diagonal_instance_closure"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Fixed-point diagonal instance closure: accepted", completed.stdout)

    def test_module_execution_runs_json_closure_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_diagonal_instance_closure",
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
        self.assertEqual(
            payload["closure_set_id"],
            "as-fixed-point-diagonal-instance-closure-v1",
        )


if __name__ == "__main__":
    unittest.main()
