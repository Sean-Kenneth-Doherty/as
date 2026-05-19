import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import substitution_graph_formula_schema_relation
from autarkic_systems.substitution_graph_formula_schema_relation import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SOURCE_KINDS,
    load_substitution_graph_formula_schema_relation,
    validate_substitution_graph_formula_schema_relation,
)


RELATION = Path("claims/substitution_graph_formula_schema_relation.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")
FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
CODEBOOK = Path("language/formal_codebook.json")
GRAPH_TARGETS = Path("claims/substitution_graph_targets.json")
FORMULA_CANDIDATES = Path("claims/substitution_graph_formula_candidates.json")
EVALUATION_EXAMPLES = Path("claims/substitution_graph_evaluation_examples.json")
SUBSTITUTION_WITNESSES = Path("claims/substitution_representability_targets.json")


class SubstitutionGraphFormulaSchemaRelationTests(unittest.TestCase):
    def setUp(self):
        self.relation = load_substitution_graph_formula_schema_relation(RELATION)

    def test_checked_in_manifest_names_relation_domain(self):
        self.assertEqual(self.relation.schema_version, 1)
        self.assertEqual(
            self.relation.relation_set_id,
            "as-substitution-graph-formula-schema-relation-v1",
        )
        self.assertEqual(self.relation.formal_language_path, str(FORMAL_LANGUAGE))
        self.assertEqual(self.relation.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.relation.substitution_graph_targets_path,
            str(GRAPH_TARGETS),
        )
        self.assertEqual(
            self.relation.formula_candidates_path,
            str(FORMULA_CANDIDATES),
        )
        self.assertEqual(
            self.relation.evaluation_examples_path,
            str(EVALUATION_EXAMPLES),
        )
        self.assertEqual(
            self.relation.substitution_representability_targets_path,
            str(SUBSTITUTION_WITNESSES),
        )
        self.assertEqual(self.relation.expected_relation_point_count, 4)
        self.assertEqual(
            REQUIRED_SOURCE_KINDS,
            (
                "witness-instance",
                "finite-evaluation",
            ),
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

    def test_checked_in_manifest_validates_relation_domain(self):
        report = validate_substitution_graph_formula_schema_relation(
            self.relation,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.relation_point_count, 4)
        self.assertEqual(report.source_kind_counts["witness-instance"], 1)
        self.assertEqual(report.source_kind_counts["finite-evaluation"], 3)
        self.assertTrue(
            any(
                result.subject == "relation_points"
                and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_relation_points(self):
        report = validate_substitution_graph_formula_schema_relation(
            self.relation,
            WILLARD_MAP,
        )

        payload = (
            substitution_graph_formula_schema_relation
            .substitution_graph_formula_schema_relation_report_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["relation_point_count"], 4)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["source_kind_counts"]["witness-instance"], 1)
        self.assertEqual(payload["source_kind_counts"]["finite-evaluation"], 3)
        self.assertTrue(
            all(point["observed_schema_instance_closed"] for point in payload["relation_points"])
        )
        self.assertTrue(
            all(point["observed_relation_holds"] for point in payload["relation_points"])
        )
        self.assertTrue(
            all(
                point["observed_output_matches_expected_surface"]
                for point in payload["relation_points"]
            )
        )
        self.assertIn(
            "AS-SUBSTITUTION-GRAPH-DELTA0-SCHEMA.witness_relation",
            [point["point_id"] for point in payload["relation_points"]],
        )

    def test_text_report_exposes_relation_boundary(self):
        report = validate_substitution_graph_formula_schema_relation(
            self.relation,
            WILLARD_MAP,
        )

        text = (
            substitution_graph_formula_schema_relation
            .format_substitution_graph_formula_schema_relation_report(report)
        )

        self.assertIn("Substitution graph formula schema relation: accepted", text)
        self.assertIn("Relation points: 4", text)
        self.assertIn("witness-instance=1", text)
        self.assertIn("finite-evaluation=3", text)
        self.assertIn("Relation failures: none", text)
        self.assertNotIn("FAIL", text)

    def test_stale_relation_point_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "relation.json"
            data = json.loads(RELATION.read_text(encoding="utf-8"))
            data["expected_relation_point_count"] = 3
            path.write_text(json.dumps(data), encoding="utf-8")
            relation = load_substitution_graph_formula_schema_relation(path)

            report = validate_substitution_graph_formula_schema_relation(
                relation,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-formula-schema-relation-count",
            report.failed_subjects,
        )
        self.assertTrue(
            any("relation point count mismatch" in result.detail for result in report.results)
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "relation.json"
            data = json.loads(RELATION.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            relation = load_substitution_graph_formula_schema_relation(path)

            report = validate_substitution_graph_formula_schema_relation(
                relation,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-formula-schema-relation-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_relation_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_formula_schema_relation
                .run_substitution_graph_formula_schema_relation_cli(
                    ["--relation", str(RELATION), "--willard-map", str(WILLARD_MAP)]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Substitution graph formula schema relation: accepted", output)

    def test_cli_returns_json_for_checked_in_relation_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_formula_schema_relation
                .run_substitution_graph_formula_schema_relation_cli(
                    [
                        "--relation",
                        str(RELATION),
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
        self.assertEqual(payload["relation_point_count"], 4)

    def test_module_execution_runs_relation_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_formula_schema_relation",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Substitution graph formula schema relation: accepted",
            completed.stdout,
        )

    def test_module_execution_runs_json_relation_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_formula_schema_relation",
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
        self.assertEqual(payload["relation_point_count"], 4)


if __name__ == "__main__":
    unittest.main()
