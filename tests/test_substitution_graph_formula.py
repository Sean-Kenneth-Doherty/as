import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import substitution_graph_formula
from autarkic_systems.substitution_graph_formula import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    load_substitution_graph_formula_candidates,
    validate_substitution_graph_formula_candidates,
)


CANDIDATES = Path("claims/substitution_graph_formula_candidates.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")
FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
CODEBOOK = Path("language/formal_codebook.json")
GRAPH_TARGETS = Path("claims/substitution_graph_targets.json")
SUBSTITUTION_WITNESSES = Path("claims/substitution_representability_targets.json")


class SubstitutionGraphFormulaTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_substitution_graph_formula_candidates(CANDIDATES)

    def test_checked_in_manifest_names_formula_schema(self):
        candidate = self.manifest.candidates[0]

        self.assertEqual(self.manifest.schema_version, 1)
        self.assertEqual(
            self.manifest.candidate_set_id,
            "as-substitution-graph-formula-candidates-v1",
        )
        self.assertEqual(self.manifest.formal_language_path, str(FORMAL_LANGUAGE))
        self.assertEqual(self.manifest.codebook_path, str(CODEBOOK))
        self.assertEqual(self.manifest.substitution_graph_targets_path, str(GRAPH_TARGETS))
        self.assertEqual(
            self.manifest.substitution_representability_targets_path,
            str(SUBSTITUTION_WITNESSES),
        )
        self.assertEqual(
            REQUIRED_FUTURE_WORK,
            (
                "formula-correctness-proof",
                "substitution-representability-proof",
                "diagonal-lemma-proof",
                "fixed-point-equation-proof",
                "self-consistency-theorem",
            ),
        )
        self.assertEqual(
            REQUIRED_NON_CLAIMS,
            (
                "no formula correctness proof",
                "no substitution representability proof",
                "no diagonal lemma proof",
                "no fixed-point equation proof",
                "no self-consistency theorem",
            ),
        )
        self.assertEqual(
            candidate.candidate_id,
            "AS-SUBSTITUTION-GRAPH-DELTA0-SCHEMA",
        )
        self.assertEqual(
            candidate.target_id,
            "AS-SUBSTITUTION-GRAPH-DELTA0-TARGET",
        )
        self.assertEqual(
            candidate.witness_id,
            "AS-SUBSTITUTION-REPRESENTABILITY-DIAGONAL-SEED-WITNESS",
        )
        self.assertEqual(candidate.relation_name, "subst_code_graph")
        self.assertEqual(candidate.formula_class, "delta0")
        self.assertEqual(candidate.status, "formula-schema-not-proved")
        self.assertEqual(
            candidate.formula_node,
            {
                "kind": "equals",
                "left": {
                    "kind": "substitution_code",
                    "left": {"kind": "variable", "name": "x"},
                    "right": {"kind": "variable", "name": "y"},
                },
                "right": {"kind": "variable", "name": "z"},
            },
        )
        self.assertEqual(candidate.expected_formula_code, (21, 18, 11, 1, 11, 2, 11, 3))
        self.assertEqual(candidate.expected_formula_free_variables, ("x", "y", "z"))
        self.assertEqual(candidate.expected_witness_instance_code_length, 4815)
        self.assertEqual(
            candidate.expected_witness_instance_code_prefix,
            (
                21,
                18,
                17,
                13,
                13,
                13,
                13,
                13,
                13,
                13,
                13,
                13,
                13,
                13,
                13,
                13,
                13,
                13,
                13,
                13,
                13,
                13,
                13,
                13,
            ),
        )
        self.assertEqual(candidate.expected_witness_instance_free_variables, ())

    def test_checked_in_manifest_validates_formula_schema(self):
        report = validate_substitution_graph_formula_candidates(
            self.manifest,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.candidate_count, 1)
        self.assertTrue(
            any(
                result.subject == "candidates"
                and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_formula_schema_and_witness_instance(self):
        report = validate_substitution_graph_formula_candidates(
            self.manifest,
            WILLARD_MAP,
        )

        payload = substitution_graph_formula.substitution_graph_formula_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["candidate_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["candidates"][0]["observed_formula_code"], [21, 18, 11, 1, 11, 2, 11, 3])
        self.assertEqual(payload["candidates"][0]["observed_witness_instance_code_length"], 4815)
        self.assertEqual(payload["candidates"][0]["observed_witness_instance_free_variables"], [])

    def test_text_report_exposes_formula_schema_boundary(self):
        report = validate_substitution_graph_formula_candidates(
            self.manifest,
            WILLARD_MAP,
        )

        text = substitution_graph_formula.format_substitution_graph_formula_report(report)

        self.assertIn("Substitution graph formula candidates: accepted", text)
        self.assertIn("AS-SUBSTITUTION-GRAPH-DELTA0-SCHEMA", text)
        self.assertIn("Formula code length: 8", text)
        self.assertIn("Witness instance code length: 4815", text)
        self.assertIn("Status: formula-schema-not-proved", text)
        self.assertNotIn("FAIL", text)

    def test_unknown_graph_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.json"
            data = json.loads(CANDIDATES.read_text(encoding="utf-8"))
            data["candidates"][0]["target_id"] = "UNKNOWN-GRAPH-TARGET"
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_substitution_graph_formula_candidates(path)

            report = validate_substitution_graph_formula_candidates(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-formula-target", report.failed_subjects)
        self.assertTrue(
            any("unknown substitution graph target: UNKNOWN-GRAPH-TARGET" in result.detail for result in report.results)
        )

    def test_stale_formula_code_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.json"
            data = json.loads(CANDIDATES.read_text(encoding="utf-8"))
            data["candidates"][0]["expected_formula_code"] = [21, 11, 1, 11, 2]
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_substitution_graph_formula_candidates(path)

            report = validate_substitution_graph_formula_candidates(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-formula-schema", report.failed_subjects)
        self.assertTrue(
            any("formula code mismatch" in result.detail for result in report.results)
        )

    def test_stale_witness_instance_length_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.json"
            data = json.loads(CANDIDATES.read_text(encoding="utf-8"))
            data["candidates"][0]["expected_witness_instance_code_length"] = 296
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_substitution_graph_formula_candidates(path)

            report = validate_substitution_graph_formula_candidates(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-formula-witness-instance", report.failed_subjects)
        self.assertTrue(
            any("witness instance code length mismatch" in result.detail for result in report.results)
        )

    def test_proved_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.json"
            data = json.loads(CANDIDATES.read_text(encoding="utf-8"))
            data["candidates"][0]["status"] = "formula-correctness-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_substitution_graph_formula_candidates(path)

            report = validate_substitution_graph_formula_candidates(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-formula-status", report.failed_subjects)
        self.assertTrue(
            any("proved formula correctness is not supported" in result.detail for result in report.results)
        )

    def test_formula_without_substitution_code_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.json"
            data = json.loads(CANDIDATES.read_text(encoding="utf-8"))
            data["candidates"][0]["formula_node"] = {
                "kind": "equals",
                "left": {"kind": "variable", "name": "x"},
                "right": {"kind": "variable", "name": "z"},
            }
            data["candidates"][0]["expected_formula_code"] = [21, 11, 1, 11, 3]
            data["candidates"][0]["expected_formula_free_variables"] = ["x", "z"]
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_substitution_graph_formula_candidates(path)

            report = validate_substitution_graph_formula_candidates(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-formula-schema", report.failed_subjects)
        self.assertTrue(
            any("formula must be substitution_code(x,y) = z" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_candidates(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = substitution_graph_formula.run_substitution_graph_formula_cli(
                ["--candidates", str(CANDIDATES), "--willard-map", str(WILLARD_MAP)]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Substitution graph formula candidates: accepted", output)

    def test_cli_returns_json_for_checked_in_candidates(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = substitution_graph_formula.run_substitution_graph_formula_cli(
                [
                    "--candidates",
                    str(CANDIDATES),
                    "--willard-map",
                    str(WILLARD_MAP),
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["candidates"][0]["observed_witness_instance_code_length"], 4815)

    def test_module_execution_runs_substitution_graph_formula_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.substitution_graph_formula"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Substitution graph formula candidates: accepted", completed.stdout)

    def test_module_execution_runs_json_substitution_graph_formula_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_formula",
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
        self.assertEqual(payload["candidate_count"], 1)


if __name__ == "__main__":
    unittest.main()
