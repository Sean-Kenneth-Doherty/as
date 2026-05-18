import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_equation
from autarkic_systems.fixed_point_equation import (
    REQUIRED_WILLARD_ANCHORS,
    build_candidate_code,
    load_fixed_point_equation_candidates,
    validate_fixed_point_equation_candidates,
)


CANDIDATES = Path("claims/fixed_point_equation_candidates.json")
FIXED_POINT_TARGETS = Path("claims/fixed_point_targets.json")
QUOTATION_TERM = Path("language/formal_quotation_term_examples.json")
CODEBOOK = Path("language/formal_codebook.json")
LANGUAGE = Path("language/formal_arithmetic_language.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointEquationCandidateTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_fixed_point_equation_candidates(CANDIDATES)

    def test_checked_in_manifest_names_candidate_surface(self):
        candidate = self.manifest.candidates[0]

        self.assertEqual(self.manifest.schema_version, 1)
        self.assertEqual(
            self.manifest.candidate_set_id,
            "as-fixed-point-equation-candidate-v1",
        )
        self.assertEqual(self.manifest.fixed_point_targets_path, str(FIXED_POINT_TARGETS))
        self.assertEqual(self.manifest.quotation_term_examples_path, str(QUOTATION_TERM))
        self.assertEqual(self.manifest.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.manifest.candidate_kind,
            "naive-quotation-substitution-candidate",
        )
        self.assertEqual(
            REQUIRED_WILLARD_ANCHORS,
            (
                "W2011-D3.4-GENERIC-CONFIGURATION",
                "W2011-D5.7-SELFCONSK",
                "W2020-D3.2-SELF-JUSTIFYING-GENAC",
            ),
        )
        self.assertEqual(candidate.target_id, "AS-FIXED-POINT-SELFCONS1-TARGET")
        self.assertEqual(
            candidate.quotation_term_example_id,
            "fixed-point-instance-quotation-term",
        )
        self.assertEqual(candidate.status, "candidate-not-fixed")
        self.assertEqual(candidate.expected_original_code, (41, 1, 22, 11, 1, 13, 12))
        self.assertEqual(candidate.expected_candidate_code_length, 121)
        self.assertEqual(candidate.expected_candidate_code_prefix, (41, 1, 22, 11, 1, 17))
        self.assertIn("diagonal-construction", candidate.required_future_work)

    def test_build_candidate_code_substitutes_quotation_term(self):
        code = build_candidate_code(
            target_id="AS-FIXED-POINT-SELFCONS1-TARGET",
            quotation_term_example_id="fixed-point-instance-quotation-term",
            fixed_point_targets_path=FIXED_POINT_TARGETS,
            quotation_term_examples_path=QUOTATION_TERM,
            codebook_path=CODEBOOK,
        )

        self.assertEqual(len(code), 121)
        self.assertEqual(code[:6], (41, 1, 22, 11, 1, 17))
        self.assertNotEqual(code, (41, 1, 22, 11, 1, 13, 12))

    def test_checked_in_manifest_validates_candidate_mismatch(self):
        report = validate_fixed_point_equation_candidates(
            self.manifest,
            LANGUAGE,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.candidate_count, 1)

    def test_json_payload_exposes_candidate_surface(self):
        report = validate_fixed_point_equation_candidates(
            self.manifest,
            LANGUAGE,
            WILLARD_MAP,
        )

        payload = fixed_point_equation.fixed_point_equation_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(
            payload["candidate_set_id"],
            "as-fixed-point-equation-candidate-v1",
        )
        self.assertEqual(payload["candidate_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["candidates"][0]["status"], "candidate-not-fixed")
        self.assertFalse(payload["candidates"][0]["candidate_is_fixed"])

    def test_text_report_exposes_candidate_surface(self):
        report = validate_fixed_point_equation_candidates(
            self.manifest,
            LANGUAGE,
            WILLARD_MAP,
        )

        text = fixed_point_equation.format_fixed_point_equation_report(report)

        self.assertIn("Fixed-point equation candidates: accepted", text)
        self.assertIn("AS-FIXED-POINT-SELFCONS1-NAIVE-QUOTE-CANDIDATE", text)
        self.assertIn("Status: candidate-not-fixed", text)
        self.assertNotIn("FAIL", text)

    def test_unknown_target_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.json"
            data = json.loads(CANDIDATES.read_text(encoding="utf-8"))
            data["candidates"][0]["target_id"] = "UNKNOWN-TARGET"
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_equation_candidates(path)

            report = validate_fixed_point_equation_candidates(
                manifest,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-equation-candidate", report.failed_subjects)
        self.assertTrue(
            any("unknown fixed-point target: UNKNOWN-TARGET" in result.detail for result in report.results)
        )

    def test_unknown_quotation_example_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.json"
            data = json.loads(CANDIDATES.read_text(encoding="utf-8"))
            data["candidates"][0]["quotation_term_example_id"] = "missing-example"
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_equation_candidates(path)

            report = validate_fixed_point_equation_candidates(
                manifest,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-equation-candidate", report.failed_subjects)
        self.assertTrue(
            any("unknown quotation term example: missing-example" in result.detail for result in report.results)
        )

    def test_proved_equation_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.json"
            data = json.loads(CANDIDATES.read_text(encoding="utf-8"))
            data["candidates"][0]["status"] = "fixed-point-equation-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_equation_candidates(path)

            report = validate_fixed_point_equation_candidates(
                manifest,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-equation-status", report.failed_subjects)
        self.assertTrue(
            any("proved fixed-point equations are not supported" in result.detail for result in report.results)
        )

    def test_stale_candidate_length_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.json"
            data = json.loads(CANDIDATES.read_text(encoding="utf-8"))
            data["candidates"][0]["expected_candidate_code_length"] = 7
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_equation_candidates(path)

            report = validate_fixed_point_equation_candidates(
                manifest,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-equation-candidate", report.failed_subjects)
        self.assertTrue(
            any("candidate code length mismatch" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_candidates(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = fixed_point_equation.run_fixed_point_equation_cli(
                [
                    "--candidates",
                    str(CANDIDATES),
                    "--language",
                    str(LANGUAGE),
                    "--willard-map",
                    str(WILLARD_MAP),
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Fixed-point equation candidates: accepted", output)

    def test_cli_returns_json_for_checked_in_candidates(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = fixed_point_equation.run_fixed_point_equation_cli(
                [
                    "--candidates",
                    str(CANDIDATES),
                    "--language",
                    str(LANGUAGE),
                    "--willard-map",
                    str(WILLARD_MAP),
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["candidate_count"], 1)

    def test_module_execution_runs_candidate_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.fixed_point_equation"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Fixed-point equation candidates: accepted", completed.stdout)

    def test_module_execution_runs_json_candidate_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_equation",
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
            payload["candidate_set_id"],
            "as-fixed-point-equation-candidate-v1",
        )


if __name__ == "__main__":
    unittest.main()
