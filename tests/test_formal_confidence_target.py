import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import formal_confidence
from autarkic_systems.formal_confidence import (
    REQUIRED_CONFIGURATION_FIELDS,
    REQUIRED_WILLARD_ANCHORS,
    load_formal_confidence_targets,
    validate_formal_confidence_targets,
)


TARGETS = Path("claims/formal_confidence_targets.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")
FORMAL_ARITHMETIC_LANGUAGE = Path("language/formal_arithmetic_language.json")
FORMAL_CODEBOOK = Path("language/formal_codebook.json")
FORMAL_SUBSTITUTION_EXAMPLES = Path("language/formal_substitution_examples.json")
CONSISTENCY_LEVEL_TARGETS = Path("claims/consistency_level_targets.json")
DEDUCTION_APPARATUS_TARGETS = Path("claims/deduction_apparatus_targets.json")
FIXED_POINT_TARGETS = Path("claims/fixed_point_targets.json")
DIAGONAL_CONSTRUCTION_TARGETS = Path("claims/diagonal_construction_targets.json")
SUBSTITUTION_REPRESENTABILITY_TARGETS = Path(
    "claims/substitution_representability_targets.json"
)
SUBSTITUTION_GRAPH_TARGETS = Path("claims/substitution_graph_targets.json")
SUBSTITUTION_GRAPH_FORMULA_CANDIDATES = Path(
    "claims/substitution_graph_formula_candidates.json"
)
FIXED_POINT_EQUATION_CANDIDATES = Path("claims/fixed_point_equation_candidates.json")
FIXED_POINT_OBSTRUCTIONS = Path("claims/fixed_point_obstructions.json")


class FormalConfidenceTargetTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_formal_confidence_targets(TARGETS)

    def test_checked_in_target_names_current_formal_confidence_boundary(self):
        target = self.manifest.targets[0]

        self.assertEqual(self.manifest.schema_version, 1)
        self.assertEqual(
            REQUIRED_CONFIGURATION_FIELDS,
            (
                "language",
                "bounded_formula_class",
                "axiom_basis",
                "deduction_method",
                "proof_code_encoding",
                "consistency_notion",
                "consistency_level_target",
                "self_reference",
                "diagonal_construction",
                "substitution_representability",
                "substitution_graph",
                "substitution_graph_formula",
                "fixed_point_equation_candidate",
                "fixed_point_obstruction",
                "substrate_bridge",
            ),
        )
        self.assertEqual(
            REQUIRED_WILLARD_ANCHORS,
            (
                "W2011-D3.4-GENERIC-CONFIGURATION",
                "W2011-D5.6-LEVEL-K-CONSISTENCY",
                "W2011-D5.7-SELFCONSK",
                "W2020-D3.2-SELF-JUSTIFYING-GENAC",
                "W2020-T4.4-T4.5-LEM-BOUNDARY",
            ),
        )
        self.assertEqual(target.target_id, "AS-FORMAL-CONFIDENCE-TARGET-001")
        self.assertEqual(target.status, "blocked")
        self.assertIn(
            "W2011-D3.4-GENERIC-CONFIGURATION",
            target.willard_anchor_ids,
        )
        self.assertIn(
            str(DEDUCTION_APPARATUS_TARGETS),
            target.configuration["deduction_method"],
        )
        self.assertIn(
            str(FORMAL_ARITHMETIC_LANGUAGE),
            target.configuration["language"],
        )
        self.assertEqual(target.configuration["bounded_formula_class"], "delta0")
        self.assertIn(
            str(FORMAL_CODEBOOK),
            target.configuration["proof_code_encoding"],
        )
        self.assertIn(
            str(CONSISTENCY_LEVEL_TARGETS),
            target.configuration["consistency_notion"],
        )
        self.assertEqual(
            target.configuration["consistency_level_target"],
            str(CONSISTENCY_LEVEL_TARGETS),
        )
        self.assertIn(
            str(FIXED_POINT_TARGETS),
            target.configuration["self_reference"],
        )
        self.assertEqual(
            target.configuration["diagonal_construction"],
            str(DIAGONAL_CONSTRUCTION_TARGETS),
        )
        self.assertEqual(
            target.configuration["substitution_representability"],
            str(SUBSTITUTION_REPRESENTABILITY_TARGETS),
        )
        self.assertEqual(
            target.configuration["substitution_graph"],
            str(SUBSTITUTION_GRAPH_TARGETS),
        )
        self.assertEqual(
            target.configuration["substitution_graph_formula"],
            str(SUBSTITUTION_GRAPH_FORMULA_CANDIDATES),
        )
        self.assertEqual(
            target.configuration["fixed_point_equation_candidate"],
            str(FIXED_POINT_EQUATION_CANDIDATES),
        )
        self.assertEqual(
            target.configuration["fixed_point_obstruction"],
            str(FIXED_POINT_OBSTRUCTIONS),
        )
        self.assertNotIn("arithmetic-object-language", target.blocked_by)
        self.assertNotIn("proof-code-encoding", target.blocked_by)
        self.assertNotIn("self-reference-substitution", target.blocked_by)
        self.assertNotIn("consistency-level-selection", target.blocked_by)
        self.assertNotIn("deduction-apparatus-selection", target.blocked_by)
        self.assertNotIn("self-reference-fixed-point", target.blocked_by)
        self.assertIn("fixed-point-construction", target.blocked_by)

    def test_checked_in_target_validates_against_willard_map(self):
        report = validate_formal_confidence_targets(self.manifest, WILLARD_MAP)

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.target_count, 1)
        self.assertEqual(report.failed_subjects, ())
        self.assertTrue(
            any(
                result.subject == "AS-FORMAL-CONFIDENCE-TARGET-001.willard_anchors"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "AS-FORMAL-CONFIDENCE-TARGET-001.consistency_level_target"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "AS-FORMAL-CONFIDENCE-TARGET-001.diagonal_construction"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "AS-FORMAL-CONFIDENCE-TARGET-001.substitution_representability"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "AS-FORMAL-CONFIDENCE-TARGET-001.substitution_graph"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "AS-FORMAL-CONFIDENCE-TARGET-001.substitution_graph_formula"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_equation_candidate"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_obstruction"
                and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_blocked_target_and_results(self):
        report = validate_formal_confidence_targets(self.manifest, WILLARD_MAP)

        payload = formal_confidence.formal_confidence_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["target_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["targets"][0]["status"], "blocked")
        self.assertIn(
            "fixed-point-construction",
            payload["targets"][0]["blocked_by"],
        )
        self.assertNotIn(
            "arithmetic-object-language",
            payload["targets"][0]["blocked_by"],
        )
        self.assertNotIn(
            "proof-code-encoding",
            payload["targets"][0]["blocked_by"],
        )
        self.assertNotIn(
            "self-reference-substitution",
            payload["targets"][0]["blocked_by"],
        )
        self.assertNotIn(
            "consistency-level-selection",
            payload["targets"][0]["blocked_by"],
        )
        self.assertNotIn(
            "deduction-apparatus-selection",
            payload["targets"][0]["blocked_by"],
        )
        self.assertNotIn(
            "self-reference-fixed-point",
            payload["targets"][0]["blocked_by"],
        )
        self.assertTrue(
            any(
                result["subject"].endswith(".configuration")
                and result["accepted"]
                for result in payload["results"]
            )
        )
        self.assertTrue(
            any(
                result["subject"].endswith(".consistency_level_target")
                and result["accepted"]
                for result in payload["results"]
            )
        )
        self.assertTrue(
            any(
                result["subject"].endswith(".diagonal_construction")
                and result["accepted"]
                for result in payload["results"]
            )
        )
        self.assertTrue(
            any(
                result["subject"].endswith(".substitution_representability")
                and result["accepted"]
                for result in payload["results"]
            )
        )
        self.assertTrue(
            any(
                result["subject"].endswith(".substitution_graph")
                and result["accepted"]
                for result in payload["results"]
            )
        )
        self.assertTrue(
            any(
                result["subject"].endswith(".substitution_graph_formula")
                and result["accepted"]
                for result in payload["results"]
            )
        )
        self.assertTrue(
            any(
                result["subject"].endswith(".fixed_point_equation_candidate")
                and result["accepted"]
                for result in payload["results"]
            )
        )
        self.assertTrue(
            any(
                result["subject"].endswith(".fixed_point_obstruction")
                and result["accepted"]
                for result in payload["results"]
            )
        )

    def test_text_report_exposes_blocked_target(self):
        report = validate_formal_confidence_targets(self.manifest, WILLARD_MAP)

        text = formal_confidence.format_formal_confidence_report(report)

        self.assertIn("Formal confidence targets: accepted", text)
        self.assertIn("AS-FORMAL-CONFIDENCE-TARGET-001: blocked", text)
        self.assertIn("Blockers: fixed-point-construction", text)
        self.assertNotIn("arithmetic-object-language", text)
        self.assertNotIn("proof-code-encoding", text)
        self.assertNotIn("self-reference-substitution", text)
        self.assertNotIn("consistency-level-selection", text)
        self.assertNotIn("deduction-apparatus-selection", text)
        self.assertNotIn("self-reference-fixed-point", text)
        self.assertIn("Willard anchors:", text)
        self.assertIn("consistency-level target accepted", text)
        self.assertIn("diagonal construction accepted", text)
        self.assertIn("substitution representability accepted", text)
        self.assertIn("substitution graph target accepted", text)
        self.assertIn("substitution graph formula accepted", text)
        self.assertIn("fixed-point equation candidate accepted", text)
        self.assertIn("fixed-point obstruction accepted", text)
        self.assertNotIn("FAIL", text)

    def test_unknown_willard_anchor_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["willard_anchor_ids"].append("W2099-UNKNOWN")
            target_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_formal_confidence_targets(target_path)

            report = validate_formal_confidence_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("target-willard-anchor", report.failed_subjects)
        self.assertTrue(
            any("unknown Willard anchor IDs: W2099-UNKNOWN" in result.detail for result in report.results)
        )

    def test_missing_configuration_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            del data["targets"][0]["configuration"]["proof_code_encoding"]
            target_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_formal_confidence_targets(target_path)

            report = validate_formal_confidence_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("target-configuration", report.failed_subjects)
        self.assertTrue(
            any("missing configuration fields: proof_code_encoding" in result.detail for result in report.results)
        )

    def test_missing_fixed_point_equation_candidate_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["configuration"]["fixed_point_equation_candidate"] = (
                "claims/missing_fixed_point_equation_candidates.json"
            )
            target_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_formal_confidence_targets(target_path)

            report = validate_formal_confidence_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("target-fixed-point-equation-candidate", report.failed_subjects)
        self.assertTrue(
            any("fixed-point equation candidate rejected" in result.detail for result in report.results)
        )

    def test_missing_fixed_point_obstruction_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["configuration"]["fixed_point_obstruction"] = (
                "claims/missing_fixed_point_obstructions.json"
            )
            target_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_formal_confidence_targets(target_path)

            report = validate_formal_confidence_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("target-fixed-point-obstruction", report.failed_subjects)
        self.assertTrue(
            any("fixed-point obstruction rejected" in result.detail for result in report.results)
        )

    def test_missing_consistency_level_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["configuration"]["consistency_level_target"] = (
                "claims/missing_consistency_level_targets.json"
            )
            target_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_formal_confidence_targets(target_path)

            report = validate_formal_confidence_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("target-consistency-level-target", report.failed_subjects)
        self.assertTrue(
            any("consistency-level target rejected" in result.detail for result in report.results)
        )

    def test_missing_diagonal_construction_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["configuration"]["diagonal_construction"] = (
                "claims/missing_diagonal_construction_targets.json"
            )
            target_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_formal_confidence_targets(target_path)

            report = validate_formal_confidence_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("target-diagonal-construction", report.failed_subjects)
        self.assertTrue(
            any("diagonal construction rejected" in result.detail for result in report.results)
        )

    def test_missing_substitution_representability_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["configuration"]["substitution_representability"] = (
                "claims/missing_substitution_representability_targets.json"
            )
            target_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_formal_confidence_targets(target_path)

            report = validate_formal_confidence_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("target-substitution-representability", report.failed_subjects)
        self.assertTrue(
            any("substitution representability rejected" in result.detail for result in report.results)
        )

    def test_missing_substitution_graph_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["configuration"]["substitution_graph"] = (
                "claims/missing_substitution_graph_targets.json"
            )
            target_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_formal_confidence_targets(target_path)

            report = validate_formal_confidence_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("target-substitution-graph", report.failed_subjects)
        self.assertTrue(
            any("substitution graph target rejected" in result.detail for result in report.results)
        )

    def test_missing_substitution_graph_formula_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["configuration"]["substitution_graph_formula"] = (
                "claims/missing_substitution_graph_formula_candidates.json"
            )
            target_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_formal_confidence_targets(target_path)

            report = validate_formal_confidence_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("target-substitution-graph-formula", report.failed_subjects)
        self.assertTrue(
            any("substitution graph formula rejected" in result.detail for result in report.results)
        )

    def test_blocked_target_without_blockers_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["blocked_by"] = []
            target_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_formal_confidence_targets(target_path)

            report = validate_formal_confidence_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("target-blockers", report.failed_subjects)
        self.assertTrue(
            any("blocked targets must name blockers" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_target(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = formal_confidence.run_formal_confidence_cli(
                ["--targets", str(TARGETS), "--willard-map", str(WILLARD_MAP)]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Formal confidence targets: accepted", output)
        self.assertIn("AS-FORMAL-CONFIDENCE-TARGET-001: blocked", output)

    def test_cli_returns_json_for_checked_in_target(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = formal_confidence.run_formal_confidence_cli(
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
        self.assertEqual(payload["targets"][0]["target_id"], "AS-FORMAL-CONFIDENCE-TARGET-001")

    def test_module_execution_runs_formal_confidence_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.formal_confidence"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Formal confidence targets: accepted", completed.stdout)

    def test_module_execution_runs_json_formal_confidence_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.formal_confidence",
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
        self.assertEqual(payload["target_count"], 1)


if __name__ == "__main__":
    unittest.main()
