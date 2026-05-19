import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import substitution_graph_diagonal_witness_composition
from autarkic_systems.substitution_graph_diagonal_witness_composition import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SOURCE_KINDS,
    load_substitution_graph_diagonal_witness_composition,
    validate_substitution_graph_diagonal_witness_composition,
)


COMPOSITION = Path("claims/substitution_graph_diagonal_witness_composition.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")
FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
CODEBOOK = Path("language/formal_codebook.json")
CORRECTNESS_TARGETS = Path("claims/substitution_graph_correctness_targets.json")
FORMULA_CANDIDATES = Path("claims/substitution_graph_formula_candidates.json")
FORMULA_SCHEMA_RELATION = Path(
    "claims/substitution_graph_formula_schema_relation.json"
)
SUBSTITUTION_WITNESSES = Path("claims/substitution_representability_targets.json")
DIAGONAL_CONSTRUCTIONS = Path("claims/diagonal_construction_targets.json")
FIXED_POINT_TARGETS = Path("claims/fixed_point_targets.json")


class SubstitutionGraphDiagonalWitnessCompositionTests(unittest.TestCase):
    def setUp(self):
        self.composition = load_substitution_graph_diagonal_witness_composition(
            COMPOSITION
        )

    def test_checked_in_manifest_names_composition_domain(self):
        self.assertEqual(self.composition.schema_version, 1)
        self.assertEqual(
            self.composition.composition_set_id,
            "as-substitution-graph-diagonal-witness-composition-v1",
        )
        self.assertEqual(self.composition.formal_language_path, str(FORMAL_LANGUAGE))
        self.assertEqual(self.composition.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.composition.correctness_targets_path,
            str(CORRECTNESS_TARGETS),
        )
        self.assertEqual(
            self.composition.formula_candidates_path,
            str(FORMULA_CANDIDATES),
        )
        self.assertEqual(
            self.composition.formula_schema_relation_path,
            str(FORMULA_SCHEMA_RELATION),
        )
        self.assertEqual(
            self.composition.substitution_representability_targets_path,
            str(SUBSTITUTION_WITNESSES),
        )
        self.assertEqual(
            self.composition.diagonal_construction_targets_path,
            str(DIAGONAL_CONSTRUCTIONS),
        )
        self.assertEqual(
            self.composition.fixed_point_targets_path,
            str(FIXED_POINT_TARGETS),
        )
        self.assertEqual(self.composition.expected_composition_count, 1)
        self.assertEqual(REQUIRED_SOURCE_KINDS, ("diagonal-witness",))
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

    def test_checked_in_manifest_validates_composition_domain(self):
        report = validate_substitution_graph_diagonal_witness_composition(
            self.composition,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.composition_count, 1)
        self.assertEqual(report.source_kind_counts["diagonal-witness"], 1)
        self.assertTrue(
            any(
                result.subject == "compositions"
                and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_composition_point(self):
        report = validate_substitution_graph_diagonal_witness_composition(
            self.composition,
            WILLARD_MAP,
        )

        payload = (
            substitution_graph_diagonal_witness_composition
            .substitution_graph_diagonal_witness_composition_report_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["composition_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["source_kind_counts"]["diagonal-witness"], 1)
        composition = payload["compositions"][0]
        self.assertEqual(
            composition["composition_id"],
            "AS-SUBST-GRAPH-DIAGONAL-WITNESS-COMPOSITION",
        )
        self.assertTrue(composition["observed_target_chain_aligned"])
        self.assertTrue(composition["observed_self_application_inputs_match"])
        self.assertTrue(composition["observed_output_codes_match"])
        self.assertTrue(composition["observed_schema_relation_witness_present"])
        self.assertTrue(composition["observed_schema_relation_witness_accepted"])

    def test_text_report_exposes_composition_boundary(self):
        report = validate_substitution_graph_diagonal_witness_composition(
            self.composition,
            WILLARD_MAP,
        )

        text = (
            substitution_graph_diagonal_witness_composition
            .format_substitution_graph_diagonal_witness_composition_report(report)
        )

        self.assertIn("Substitution graph diagonal witness composition: accepted", text)
        self.assertIn("Compositions: 1", text)
        self.assertIn("diagonal-witness=1", text)
        self.assertIn("Composition failures: none", text)
        self.assertNotIn("FAIL", text)

    def test_stale_composition_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "composition.json"
            data = json.loads(COMPOSITION.read_text(encoding="utf-8"))
            data["expected_composition_count"] = 2
            path.write_text(json.dumps(data), encoding="utf-8")
            composition = load_substitution_graph_diagonal_witness_composition(path)

            report = validate_substitution_graph_diagonal_witness_composition(
                composition,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-diagonal-witness-composition-count",
            report.failed_subjects,
        )
        self.assertTrue(
            any("composition count mismatch" in result.detail for result in report.results)
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "composition.json"
            data = json.loads(COMPOSITION.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            composition = load_substitution_graph_diagonal_witness_composition(path)

            report = validate_substitution_graph_diagonal_witness_composition(
                composition,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-diagonal-witness-composition-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_composition_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_diagonal_witness_composition
                .run_substitution_graph_diagonal_witness_composition_cli(
                    [
                        "--composition",
                        str(COMPOSITION),
                        "--willard-map",
                        str(WILLARD_MAP),
                    ]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn(
            "Substitution graph diagonal witness composition: accepted",
            output,
        )

    def test_cli_returns_json_for_checked_in_composition_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_diagonal_witness_composition
                .run_substitution_graph_diagonal_witness_composition_cli(
                    [
                        "--composition",
                        str(COMPOSITION),
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
        self.assertEqual(payload["composition_count"], 1)

    def test_module_execution_runs_composition_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_diagonal_witness_composition",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Substitution graph diagonal witness composition: accepted",
            completed.stdout,
        )

    def test_module_execution_runs_json_composition_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_diagonal_witness_composition",
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
        self.assertEqual(payload["composition_count"], 1)


if __name__ == "__main__":
    unittest.main()
