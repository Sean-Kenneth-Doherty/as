import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import substitution_graph_correctness_cases
from autarkic_systems.substitution_graph_correctness_cases import (
    REQUIRED_CASE_KINDS,
    REQUIRED_DEPENDENCIES_BY_KIND,
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    load_substitution_graph_correctness_cases,
    validate_substitution_graph_correctness_cases,
)


CASES = Path("claims/substitution_graph_correctness_cases.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")
FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
CODEBOOK = Path("language/formal_codebook.json")
CORRECTNESS_TARGETS = Path("claims/substitution_graph_correctness_targets.json")
FORMAL_SUBSTITUTION_EXAMPLES = Path("language/formal_substitution_examples.json")
QUOTATION_TERM_EXAMPLES = Path("language/formal_quotation_term_examples.json")
FORMULA_CANDIDATES = Path("claims/substitution_graph_formula_candidates.json")
SUBSTITUTION_REPRESENTABILITY_TARGETS = Path(
    "claims/substitution_representability_targets.json"
)
CODEBOOK_ROUNDTRIP = Path("claims/substitution_graph_codebook_roundtrip.json")
QUOTATION_TERM_CLOSURE = Path(
    "claims/substitution_graph_quotation_term_closure.json"
)
META_SUBSTITUTION_SEMANTICS = Path(
    "claims/substitution_graph_meta_substitution_semantics.json"
)
FORMULA_SCHEMA_RELATION = Path(
    "claims/substitution_graph_formula_schema_relation.json"
)
DIAGONAL_WITNESS_COMPOSITION = Path(
    "claims/substitution_graph_diagonal_witness_composition.json"
)


class SubstitutionGraphCorrectnessCaseTests(unittest.TestCase):
    def setUp(self):
        self.cases = load_substitution_graph_correctness_cases(CASES)

    def test_checked_in_manifest_names_correctness_cases(self):
        first, second, third, fourth, fifth = self.cases.cases

        self.assertEqual(self.cases.schema_version, 1)
        self.assertEqual(
            self.cases.case_set_id,
            "as-substitution-graph-correctness-cases-v1",
        )
        self.assertEqual(self.cases.formal_language_path, str(FORMAL_LANGUAGE))
        self.assertEqual(self.cases.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.cases.correctness_targets_path,
            str(CORRECTNESS_TARGETS),
        )
        self.assertEqual(
            self.cases.formal_substitution_examples_path,
            str(FORMAL_SUBSTITUTION_EXAMPLES),
        )
        self.assertEqual(
            self.cases.quotation_term_examples_path,
            str(QUOTATION_TERM_EXAMPLES),
        )
        self.assertEqual(
            self.cases.formula_candidates_path,
            str(FORMULA_CANDIDATES),
        )
        self.assertEqual(
            self.cases.substitution_representability_targets_path,
            str(SUBSTITUTION_REPRESENTABILITY_TARGETS),
        )
        self.assertEqual(
            self.cases.codebook_roundtrip_path,
            str(CODEBOOK_ROUNDTRIP),
        )
        self.assertEqual(
            self.cases.quotation_term_closure_path,
            str(QUOTATION_TERM_CLOSURE),
        )
        self.assertEqual(
            self.cases.meta_substitution_semantics_path,
            str(META_SUBSTITUTION_SEMANTICS),
        )
        self.assertEqual(
            self.cases.formula_schema_relation_path,
            str(FORMULA_SCHEMA_RELATION),
        )
        self.assertEqual(
            self.cases.diagonal_witness_composition_path,
            str(DIAGONAL_WITNESS_COMPOSITION),
        )
        self.assertEqual(
            REQUIRED_CASE_KINDS,
            (
                "codebook-roundtrip",
                "quotation-term-closure",
                "meta-substitution-semantics",
                "formula-schema-relation",
                "diagonal-witness-composition",
            ),
        )
        self.assertEqual(
            REQUIRED_DEPENDENCIES_BY_KIND["codebook-roundtrip"],
            ("correctness_target", "codebook", "codebook_roundtrip"),
        )
        self.assertEqual(
            REQUIRED_DEPENDENCIES_BY_KIND["quotation-term-closure"],
            (
                "correctness_target",
                "codebook",
                "quotation_term",
                "quotation_term_closure",
            ),
        )
        self.assertEqual(
            REQUIRED_DEPENDENCIES_BY_KIND["meta-substitution-semantics"],
            (
                "correctness_target",
                "formal_substitution",
                "meta_substitution_semantics",
            ),
        )
        self.assertEqual(
            REQUIRED_DEPENDENCIES_BY_KIND["formula-schema-relation"],
            (
                "correctness_target",
                "formula_candidate",
                "formula_schema_relation",
            ),
        )
        self.assertEqual(
            REQUIRED_DEPENDENCIES_BY_KIND["diagonal-witness-composition"],
            (
                "correctness_target",
                "substitution_representability",
                "diagonal_witness_composition",
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
        self.assertEqual(
            first.case_id,
            "AS-SUBST-GRAPH-CORRECTNESS-CODEBOOK-ROUNDTRIP",
        )
        self.assertEqual(first.case_kind, "codebook-roundtrip")
        self.assertEqual(first.status, "proof-case-open")
        self.assertEqual(
            first.correctness_target_id,
            "AS-SUBSTITUTION-GRAPH-CORRECTNESS-TARGET",
        )
        self.assertEqual(
            first.required_dependency_subjects,
            ("correctness_target", "codebook", "codebook_roundtrip"),
        )
        self.assertEqual(second.case_kind, "quotation-term-closure")
        self.assertEqual(
            second.required_dependency_subjects,
            (
                "correctness_target",
                "codebook",
                "quotation_term",
                "quotation_term_closure",
            ),
        )
        self.assertEqual(third.case_kind, "meta-substitution-semantics")
        self.assertEqual(
            third.required_dependency_subjects,
            (
                "correctness_target",
                "formal_substitution",
                "meta_substitution_semantics",
            ),
        )
        self.assertEqual(fourth.case_kind, "formula-schema-relation")
        self.assertEqual(
            fourth.required_dependency_subjects,
            (
                "correctness_target",
                "formula_candidate",
                "formula_schema_relation",
            ),
        )
        self.assertEqual(fifth.case_kind, "diagonal-witness-composition")
        self.assertEqual(
            fifth.required_dependency_subjects,
            (
                "correctness_target",
                "substitution_representability",
                "diagonal_witness_composition",
            ),
        )

    def test_checked_in_manifest_validates_correctness_cases(self):
        report = validate_substitution_graph_correctness_cases(
            self.cases,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.case_count, 5)
        self.assertTrue(
            any(
                result.subject == "codebook_roundtrip"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "quotation_term_closure"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "meta_substitution_semantics"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "formula_schema_relation"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "diagonal_witness_composition"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "cases"
                and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_case_dependencies(self):
        report = validate_substitution_graph_correctness_cases(
            self.cases,
            WILLARD_MAP,
        )

        payload = substitution_graph_correctness_cases.substitution_graph_correctness_cases_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["case_count"], 5)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertTrue(payload["cases"][0]["observed_all_required_dependencies_present"])
        self.assertEqual(payload["cases"][0]["observed_dependency_count"], 3)
        self.assertEqual(payload["cases"][1]["observed_dependency_count"], 4)
        self.assertEqual(payload["cases"][2]["observed_dependency_count"], 3)
        self.assertEqual(payload["cases"][3]["observed_dependency_count"], 3)
        self.assertEqual(payload["cases"][4]["observed_dependency_count"], 3)
        self.assertIn(
            "formula-correctness-proof",
            payload["cases"][0]["required_future_work"],
        )

    def test_text_report_exposes_case_boundary(self):
        report = validate_substitution_graph_correctness_cases(
            self.cases,
            WILLARD_MAP,
        )

        text = substitution_graph_correctness_cases.format_substitution_graph_correctness_cases_report(report)

        self.assertIn("Substitution graph correctness cases: accepted", text)
        self.assertIn("Cases: 5", text)
        self.assertIn("AS-SUBST-GRAPH-CORRECTNESS-CODEBOOK-ROUNDTRIP", text)
        self.assertIn("Case kind: codebook-roundtrip", text)
        self.assertIn(
            "Dependencies: correctness_target, codebook, codebook_roundtrip",
            text,
        )
        self.assertIn(
            "Dependencies: correctness_target, codebook, quotation_term, quotation_term_closure",
            text,
        )
        self.assertIn(
            "Dependencies: correctness_target, formal_substitution, meta_substitution_semantics",
            text,
        )
        self.assertIn(
            "Dependencies: correctness_target, formula_candidate, formula_schema_relation",
            text,
        )
        self.assertIn(
            "Dependencies: correctness_target, substitution_representability, diagonal_witness_composition",
            text,
        )
        self.assertIn("Future work:", text)
        self.assertNotIn("FAIL", text)

    def test_unknown_correctness_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.json"
            data = json.loads(CASES.read_text(encoding="utf-8"))
            data["cases"][0]["correctness_target_id"] = "AS-UNKNOWN-CORRECTNESS-TARGET"
            path.write_text(json.dumps(data), encoding="utf-8")
            cases = load_substitution_graph_correctness_cases(path)

            report = validate_substitution_graph_correctness_cases(cases, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-correctness-case-target", report.failed_subjects)
        self.assertTrue(
            any("unknown correctness target" in result.detail for result in report.results)
        )

    def test_missing_required_case_dependency_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.json"
            data = json.loads(CASES.read_text(encoding="utf-8"))
            data["cases"][0]["required_dependency_subjects"] = ["correctness_target"]
            path.write_text(json.dumps(data), encoding="utf-8")
            cases = load_substitution_graph_correctness_cases(path)

            report = validate_substitution_graph_correctness_cases(cases, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-correctness-case-dependency", report.failed_subjects)
        self.assertTrue(
            any("missing required dependencies" in result.detail for result in report.results)
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.json"
            data = json.loads(CASES.read_text(encoding="utf-8"))
            data["cases"][0]["non_claims"] = data["cases"][0]["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            cases = load_substitution_graph_correctness_cases(path)

            report = validate_substitution_graph_correctness_cases(cases, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-correctness-case-non-claim", report.failed_subjects)
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_proved_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.json"
            data = json.loads(CASES.read_text(encoding="utf-8"))
            data["cases"][0]["status"] = "formula-correctness-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            cases = load_substitution_graph_correctness_cases(path)

            report = validate_substitution_graph_correctness_cases(cases, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-correctness-case-status", report.failed_subjects)
        self.assertTrue(
            any("proved correctness cases are not supported" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_cases(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = substitution_graph_correctness_cases.run_substitution_graph_correctness_cases_cli(
                ["--cases", str(CASES), "--willard-map", str(WILLARD_MAP)]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Substitution graph correctness cases: accepted", output)

    def test_cli_returns_json_for_checked_in_cases(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = substitution_graph_correctness_cases.run_substitution_graph_correctness_cases_cli(
                [
                    "--cases",
                    str(CASES),
                    "--willard-map",
                    str(WILLARD_MAP),
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["case_count"], 5)

    def test_module_execution_runs_correctness_case_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.substitution_graph_correctness_cases"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Substitution graph correctness cases: accepted", completed.stdout)

    def test_module_execution_runs_json_correctness_case_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_correctness_cases",
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
        self.assertEqual(payload["case_count"], 5)
