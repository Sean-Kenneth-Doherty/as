import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_bridge_equality_evaluation
from autarkic_systems.fixed_point_bridge_equality_evaluation import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SOURCE_KINDS,
    load_fixed_point_bridge_equality_evaluation,
    validate_fixed_point_bridge_equality_evaluation,
)


EVALUATION = Path("claims/fixed_point_bridge_equality_evaluation.json")
CONSTRUCTION_CASES = Path("claims/fixed_point_construction_cases.json")
FIXED_POINT_TARGETS = Path("claims/fixed_point_targets.json")
FIXED_POINT_EQUATION_BRIDGE = Path("claims/fixed_point_equation_bridge_targets.json")
SUBSTITUTION_REPRESENTABILITY = Path("claims/substitution_representability_targets.json")
BRIDGE_EQUALITY_ALIGNMENT = Path("claims/fixed_point_bridge_equality_alignment.json")
CODEBOOK = Path("language/formal_codebook.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointBridgeEqualityEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.evaluation = load_fixed_point_bridge_equality_evaluation(EVALUATION)

    def test_checked_in_manifest_names_bridge_equality_evaluation_domain(self):
        self.assertEqual(self.evaluation.schema_version, 1)
        self.assertEqual(
            self.evaluation.evaluation_set_id,
            "as-fixed-point-bridge-equality-evaluation-v1",
        )
        self.assertEqual(
            self.evaluation.fixed_point_construction_cases_path,
            str(CONSTRUCTION_CASES),
        )
        self.assertEqual(
            self.evaluation.fixed_point_targets_path,
            str(FIXED_POINT_TARGETS),
        )
        self.assertEqual(
            self.evaluation.fixed_point_equation_bridge_targets_path,
            str(FIXED_POINT_EQUATION_BRIDGE),
        )
        self.assertEqual(
            self.evaluation.substitution_representability_targets_path,
            str(SUBSTITUTION_REPRESENTABILITY),
        )
        self.assertEqual(
            self.evaluation.bridge_equality_alignment_path,
            str(BRIDGE_EQUALITY_ALIGNMENT),
        )
        self.assertEqual(self.evaluation.codebook_path, str(CODEBOOK))
        self.assertEqual(self.evaluation.expected_evaluation_count, 1)
        self.assertEqual(self.evaluation.expected_formula_code_length, 10)
        self.assertEqual(self.evaluation.expected_argument_code_length, 10)
        self.assertEqual(self.evaluation.expected_output_code_length, 296)
        self.assertEqual(self.evaluation.expected_bridge_equation_code_length, 4815)
        self.assertEqual(REQUIRED_SOURCE_KINDS, ("bridge-equality-evaluation",))
        self.assertEqual(
            REQUIRED_FUTURE_WORK,
            (
                "bridge-equality-proof",
                "fixed-point-equation-proof",
                "self-consistency-theorem",
            ),
        )
        self.assertEqual(
            REQUIRED_NON_CLAIMS,
            (
                "no bridge equality proof",
                "no fixed-point equation proof",
                "no arithmetized proof predicate",
                "no self-consistency theorem",
            ),
        )

    def test_checked_in_manifest_validates_bridge_equality_evaluation_domain(self):
        report = validate_fixed_point_bridge_equality_evaluation(
            self.evaluation,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.evaluation_count, 1)
        self.assertEqual(report.source_kind_counts["bridge-equality-evaluation"], 1)

    def test_json_payload_exposes_bridge_equality_evaluation(self):
        report = validate_fixed_point_bridge_equality_evaluation(
            self.evaluation,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_bridge_equality_evaluation
            .fixed_point_bridge_equality_evaluation_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["evaluation_count"], 1)
        self.assertEqual(
            payload["source_kind_counts"]["bridge-equality-evaluation"],
            1,
        )
        self.assertEqual(payload["failed_subjects"], [])
        evaluation = payload["evaluations"][0]
        self.assertEqual(
            evaluation["evaluation_id"],
            "AS-FIXED-POINT-BRIDGE-EQUALITY-EVALUATION",
        )
        self.assertEqual(evaluation["observed_formula_code_length"], 10)
        self.assertEqual(evaluation["observed_argument_code_length"], 10)
        self.assertEqual(evaluation["observed_output_code_length"], 296)
        self.assertEqual(evaluation["observed_bridge_equation_code_length"], 4815)
        self.assertTrue(evaluation["observed_construction_case_is_open"])
        self.assertTrue(evaluation["observed_construction_case_requires_evaluation"])
        self.assertTrue(evaluation["observed_left_term_is_substitution_code"])
        self.assertTrue(evaluation["observed_left_formula_decodes_to_seed"])
        self.assertTrue(evaluation["observed_self_application_argument_matches_seed"])
        self.assertTrue(evaluation["observed_evaluated_output_matches_witness"])
        self.assertTrue(evaluation["observed_evaluated_output_matches_right_quote"])
        self.assertTrue(evaluation["observed_bridge_equality_alignment_accepted"])
        self.assertTrue(evaluation["observed_route_ids_match"])
        self.assertTrue(evaluation["observed_all_dependencies_accepted"])

    def test_text_report_exposes_bridge_equality_evaluation_boundary(self):
        report = validate_fixed_point_bridge_equality_evaluation(
            self.evaluation,
            WILLARD_MAP,
        )

        text = (
            fixed_point_bridge_equality_evaluation
            .format_fixed_point_bridge_equality_evaluation_report(report)
        )

        self.assertIn("Fixed-point bridge equality evaluation: accepted", text)
        self.assertIn("Bridge-equality evaluations: 1", text)
        self.assertIn("bridge-equality-evaluation=1", text)
        self.assertIn("Formula code length: 10", text)
        self.assertIn("Argument code length: 10", text)
        self.assertIn("Output code length: 296", text)
        self.assertIn("Right quoted code length: 296", text)
        self.assertIn("Bridge equation code length: 4815", text)
        self.assertIn("construction_case_open=True", text)
        self.assertIn("requires_evaluation=True", text)
        self.assertIn("left_term_substitution_code=True", text)
        self.assertIn("left_formula_decodes_to_seed=True", text)
        self.assertIn("self_application_argument_matches_seed=True", text)
        self.assertIn("output_matches_witness=True", text)
        self.assertIn("output_matches_right_quote=True", text)
        self.assertIn("alignment_accepted=True", text)
        self.assertIn("route_ids_match=True", text)
        self.assertIn("dependencies_accepted=True", text)
        self.assertIn("Evaluation failures: none", text)
        self.assertNotIn("FAIL", text)

    def test_stale_evaluation_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evaluation.json"
            data = json.loads(EVALUATION.read_text(encoding="utf-8"))
            data["expected_evaluation_count"] = 2
            path.write_text(json.dumps(data), encoding="utf-8")
            evaluation = load_fixed_point_bridge_equality_evaluation(path)

            report = validate_fixed_point_bridge_equality_evaluation(
                evaluation,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-bridge-equality-evaluation-count",
            report.failed_subjects,
        )
        self.assertTrue(
            any("evaluation count mismatch" in result.detail for result in report.results)
        )

    def test_stale_output_length_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evaluation.json"
            data = json.loads(EVALUATION.read_text(encoding="utf-8"))
            data["expected_output_code_length"] = 297
            path.write_text(json.dumps(data), encoding="utf-8")
            evaluation = load_fixed_point_bridge_equality_evaluation(path)

            report = validate_fixed_point_bridge_equality_evaluation(
                evaluation,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-bridge-equality-evaluation-output-length",
            report.failed_subjects,
        )
        self.assertTrue(
            any("output length mismatch" in result.detail for result in report.results)
        )

    def test_stale_bridge_equation_length_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evaluation.json"
            data = json.loads(EVALUATION.read_text(encoding="utf-8"))
            data["expected_bridge_equation_code_length"] = 4816
            path.write_text(json.dumps(data), encoding="utf-8")
            evaluation = load_fixed_point_bridge_equality_evaluation(path)

            report = validate_fixed_point_bridge_equality_evaluation(
                evaluation,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-bridge-equality-evaluation-bridge-length",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                "bridge equation length mismatch" in result.detail
                for result in report.results
            )
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evaluation.json"
            data = json.loads(EVALUATION.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            evaluation = load_fixed_point_bridge_equality_evaluation(path)

            report = validate_fixed_point_bridge_equality_evaluation(
                evaluation,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-bridge-equality-evaluation-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_missing_dependency_path_is_rejected_not_raised(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evaluation.json"
            data = json.loads(EVALUATION.read_text(encoding="utf-8"))
            data["fixed_point_targets_path"] = str(Path(tmp) / "missing.json")
            path.write_text(json.dumps(data), encoding="utf-8")
            evaluation = load_fixed_point_bridge_equality_evaluation(path)

            report = validate_fixed_point_bridge_equality_evaluation(
                evaluation,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("fixed_point", report.failed_subjects)
        self.assertIn(
            "fixed-point-bridge-equality-evaluation-derivation",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                result.subject == "fixed_point"
                and not result.accepted
                and "fixed-point-target-load" in result.detail
                for result in report.results
            )
        )

    def test_cli_returns_zero_for_checked_in_evaluation_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_bridge_equality_evaluation
                .run_fixed_point_bridge_equality_evaluation_cli(
                    [
                        "--evaluation",
                        str(EVALUATION),
                        "--willard-map",
                        str(WILLARD_MAP),
                    ]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Fixed-point bridge equality evaluation: accepted", output)

    def test_cli_returns_json_for_checked_in_evaluation_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_bridge_equality_evaluation
                .run_fixed_point_bridge_equality_evaluation_cli(
                    [
                        "--evaluation",
                        str(EVALUATION),
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
        self.assertEqual(payload["evaluation_count"], 1)

    def test_module_execution_runs_evaluation_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_bridge_equality_evaluation",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Fixed-point bridge equality evaluation: accepted",
            completed.stdout,
        )

    def test_module_execution_runs_json_evaluation_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_bridge_equality_evaluation",
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
            payload["evaluation_set_id"],
            "as-fixed-point-bridge-equality-evaluation-v1",
        )


if __name__ == "__main__":
    unittest.main()
