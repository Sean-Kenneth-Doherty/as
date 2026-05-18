import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import substitution_representability
from autarkic_systems.substitution_representability import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_WILLARD_ANCHORS,
    build_substitution_witness_output_code,
    load_substitution_representability_targets,
    validate_substitution_representability_targets,
)


TARGETS = Path("claims/substitution_representability_targets.json")
DIAGONAL_TARGETS = Path("claims/diagonal_construction_targets.json")
CODEBOOK = Path("language/formal_codebook.json")
LANGUAGE = Path("language/formal_arithmetic_language.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class SubstitutionRepresentabilityTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_substitution_representability_targets(TARGETS)

    def test_checked_in_manifest_names_substitution_witness(self):
        witness = self.manifest.witnesses[0]

        self.assertEqual(self.manifest.schema_version, 1)
        self.assertEqual(
            self.manifest.witness_set_id,
            "as-substitution-representability-witness-v1",
        )
        self.assertEqual(self.manifest.diagonal_construction_targets_path, str(DIAGONAL_TARGETS))
        self.assertEqual(self.manifest.codebook_path, str(CODEBOOK))
        self.assertEqual(
            REQUIRED_WILLARD_ANCHORS,
            (
                "W2011-D3.4-GENERIC-CONFIGURATION",
                "W2011-D5.7-SELFCONSK",
                "W2020-D3.2-SELF-JUSTIFYING-GENAC",
            ),
        )
        self.assertEqual(
            REQUIRED_FUTURE_WORK,
            (
                "delta0-graph-formula",
                "substitution-representability-proof",
                "diagonal-lemma-proof",
                "fixed-point-equation-proof",
                "self-consistency-theorem",
            ),
        )
        self.assertEqual(
            witness.witness_id,
            "AS-SUBSTITUTION-REPRESENTABILITY-DIAGONAL-SEED-WITNESS",
        )
        self.assertEqual(
            witness.construction_id,
            "AS-FIXED-POINT-SELFCONS1-DIAGONAL-SEED",
        )
        self.assertEqual(witness.variable, "n")
        self.assertEqual(witness.status, "representability-witness-not-proof")
        self.assertEqual(witness.expected_formula_code, (41, 1, 22, 11, 1, 18, 11, 4, 11, 4))
        self.assertEqual(witness.expected_argument_code, (41, 1, 22, 11, 1, 18, 11, 4, 11, 4))
        self.assertEqual(witness.expected_output_code_length, 296)
        self.assertEqual(
            witness.expected_output_code_prefix,
            (41, 1, 22, 11, 1, 18, 17, 13, 13, 13, 13, 13),
        )
        self.assertEqual(witness.expected_output_free_variables, ())
        self.assertIn("no substitution representability proof", witness.non_claims)

    def test_build_substitution_witness_output_code_matches_diagonal_instance(self):
        code = build_substitution_witness_output_code(
            witness_id="AS-SUBSTITUTION-REPRESENTABILITY-DIAGONAL-SEED-WITNESS",
            targets_path=TARGETS,
            diagonal_targets_path=DIAGONAL_TARGETS,
            codebook_path=CODEBOOK,
        )

        self.assertEqual(len(code), 296)
        self.assertEqual(code[:12], (41, 1, 22, 11, 1, 18, 17, 13, 13, 13, 13, 13))

    def test_checked_in_manifest_validates_witness(self):
        report = validate_substitution_representability_targets(
            self.manifest,
            LANGUAGE,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.witness_count, 1)
        self.assertTrue(
            any(
                result.subject == "witnesses"
                and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_witness_surface(self):
        report = validate_substitution_representability_targets(
            self.manifest,
            LANGUAGE,
            WILLARD_MAP,
        )

        payload = substitution_representability.substitution_representability_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["witness_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["witnesses"][0]["status"], "representability-witness-not-proof")
        self.assertEqual(payload["witnesses"][0]["observed_formula_code_length"], 10)
        self.assertEqual(payload["witnesses"][0]["observed_output_code_length"], 296)

    def test_text_report_exposes_witness_surface(self):
        report = validate_substitution_representability_targets(
            self.manifest,
            LANGUAGE,
            WILLARD_MAP,
        )

        text = substitution_representability.format_substitution_representability_report(report)

        self.assertIn("Substitution representability witnesses: accepted", text)
        self.assertIn("AS-SUBSTITUTION-REPRESENTABILITY-DIAGONAL-SEED-WITNESS", text)
        self.assertIn("Status: representability-witness-not-proof", text)
        self.assertIn("Output code length: 296", text)
        self.assertNotIn("FAIL", text)

    def test_unknown_diagonal_construction_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "witnesses.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["witnesses"][0]["construction_id"] = "UNKNOWN-CONSTRUCTION"
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_substitution_representability_targets(path)

            report = validate_substitution_representability_targets(
                manifest,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("substitution-representability-witness", report.failed_subjects)
        self.assertTrue(
            any("unknown diagonal construction: UNKNOWN-CONSTRUCTION" in result.detail for result in report.results)
        )

    def test_stale_output_length_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "witnesses.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["witnesses"][0]["expected_output_code_length"] = 10
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_substitution_representability_targets(path)

            report = validate_substitution_representability_targets(
                manifest,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("substitution-representability-output", report.failed_subjects)
        self.assertTrue(
            any("output code length mismatch" in result.detail for result in report.results)
        )

    def test_proved_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "witnesses.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["witnesses"][0]["status"] = "substitution-representability-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_substitution_representability_targets(path)

            report = validate_substitution_representability_targets(
                manifest,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("substitution-representability-status", report.failed_subjects)
        self.assertTrue(
            any("proved substitution representability is not supported" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_witnesses(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = substitution_representability.run_substitution_representability_cli(
                [
                    "--targets",
                    str(TARGETS),
                    "--language",
                    str(LANGUAGE),
                    "--willard-map",
                    str(WILLARD_MAP),
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Substitution representability witnesses: accepted", output)

    def test_cli_returns_json_for_checked_in_witnesses(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = substitution_representability.run_substitution_representability_cli(
                [
                    "--targets",
                    str(TARGETS),
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
        self.assertEqual(payload["witnesses"][0]["observed_output_code_length"], 296)

    def test_module_execution_runs_substitution_representability_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.substitution_representability"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Substitution representability witnesses: accepted", completed.stdout)

    def test_module_execution_runs_json_substitution_representability_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_representability",
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
        self.assertEqual(payload["witness_count"], 1)


if __name__ == "__main__":
    unittest.main()
