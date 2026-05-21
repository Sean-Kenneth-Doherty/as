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
SUBSTITUTION_GRAPH_CORRECTNESS_TARGETS = Path(
    "claims/substitution_graph_correctness_targets.json"
)
SUBSTITUTION_GRAPH_CORRECTNESS_CASES = Path(
    "claims/substitution_graph_correctness_cases.json"
)
FIXED_POINT_EQUATION_CANDIDATES = Path("claims/fixed_point_equation_candidates.json")
FIXED_POINT_EQUATION_BRIDGE = Path("claims/fixed_point_equation_bridge_targets.json")
FIXED_POINT_CONSTRUCTION_CASES = Path("claims/fixed_point_construction_cases.json")
FIXED_POINT_CONSTRUCTION_FRONTIER_STATUS = Path(
    "claims/fixed_point_construction_frontier_status.json"
)
FIXED_POINT_OBSTRUCTIONS = Path("claims/fixed_point_obstructions.json")
FORMAL_CONFIDENCE_FRONTIER_SUBJECT = (
    "AS-FORMAL-CONFIDENCE-TARGET-001."
    "fixed_point_construction_frontier_status"
)
FORMAL_CONFIDENCE_VALIDATION_SUMMARY = {
    "accepted_validation_count": 19,
    "failed_validation_count": 0,
    "accepted_frontier_subjects": [
        FORMAL_CONFIDENCE_FRONTIER_SUBJECT,
    ],
    "accepted_frontier_labels": [
        "fixed_point_construction_frontier_status",
    ],
}


class FormalConfidenceTargetTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_formal_confidence_targets(TARGETS)

    def test_default_formal_confidence_validation_reuses_cached_report_and_tracks_temp_manifest(self):
        validate_formal_confidence_targets.cache_clear()
        first_manifest = load_formal_confidence_targets(TARGETS)
        second_manifest = load_formal_confidence_targets(TARGETS)

        first_report = validate_formal_confidence_targets(
            first_manifest,
            WILLARD_MAP,
        )
        after_first = validate_formal_confidence_targets.cache_info()
        second_report = validate_formal_confidence_targets(
            second_manifest,
            WILLARD_MAP,
        )
        after_second = validate_formal_confidence_targets.cache_info()

        self.assertTrue(first_report.accepted, first_report.results)
        self.assertIs(first_report, second_report)
        self.assertEqual(after_first.misses, 1)
        self.assertEqual(after_first.hits, 0)
        self.assertEqual(after_second.misses, 1)
        self.assertEqual(after_second.hits, 1)

        target = first_manifest.targets[0]
        self.assertIn("fixed_point_construction_frontier_status", target.configuration)
        self.assertEqual(
            dict(target.configuration)["fixed_point_construction_frontier_status"],
            str(FIXED_POINT_CONSTRUCTION_FRONTIER_STATUS),
        )

        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["configuration"][
                "fixed_point_construction_frontier_status"
            ] = "claims/missing_fixed_point_construction_frontier_status.json"
            target_path.write_text(json.dumps(data), encoding="utf-8")
            modified_manifest = load_formal_confidence_targets(target_path)

            modified_report = validate_formal_confidence_targets(
                modified_manifest,
                WILLARD_MAP,
            )
            after_modified = validate_formal_confidence_targets.cache_info()

        self.assertIsNot(first_report, modified_report)
        self.assertFalse(modified_report.accepted)
        self.assertIn(
            "target-fixed-point-construction-frontier-status",
            modified_report.failed_subjects,
        )
        self.assertEqual(after_modified.misses, 2)
        self.assertEqual(after_modified.hits, 1)

        final_report = validate_formal_confidence_targets(
            load_formal_confidence_targets(TARGETS),
            WILLARD_MAP,
        )
        after_final = validate_formal_confidence_targets.cache_info()

        self.assertIs(first_report, final_report)
        self.assertEqual(after_final.misses, 2)
        self.assertEqual(after_final.hits, 2)

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
                "substitution_graph_correctness",
                "substitution_graph_correctness_cases",
                "fixed_point_equation_candidate",
                "fixed_point_equation_bridge",
                "fixed_point_construction_cases",
                "fixed_point_construction_frontier_status",
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
            target.configuration["substitution_graph_correctness"],
            str(SUBSTITUTION_GRAPH_CORRECTNESS_TARGETS),
        )
        self.assertEqual(
            target.configuration["substitution_graph_correctness_cases"],
            str(SUBSTITUTION_GRAPH_CORRECTNESS_CASES),
        )
        self.assertEqual(
            target.configuration["fixed_point_equation_candidate"],
            str(FIXED_POINT_EQUATION_CANDIDATES),
        )
        self.assertEqual(
            target.configuration["fixed_point_equation_bridge"],
            str(FIXED_POINT_EQUATION_BRIDGE),
        )
        self.assertEqual(
            target.configuration["fixed_point_construction_cases"],
            str(FIXED_POINT_CONSTRUCTION_CASES),
        )
        self.assertEqual(
            target.configuration["fixed_point_construction_frontier_status"],
            str(FIXED_POINT_CONSTRUCTION_FRONTIER_STATUS),
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
                result.subject == "AS-FORMAL-CONFIDENCE-TARGET-001.substitution_graph_correctness"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "AS-FORMAL-CONFIDENCE-TARGET-001.substitution_graph_correctness_cases"
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
                result.subject == "AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_equation_bridge"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_cases"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == (
                    "AS-FORMAL-CONFIDENCE-TARGET-001."
                    "fixed_point_construction_frontier_status"
                )
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
                result["subject"].endswith(".substitution_graph_correctness")
                and result["accepted"]
                for result in payload["results"]
            )
        )
        self.assertTrue(
            any(
                result["subject"].endswith(".substitution_graph_correctness_cases")
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
                result["subject"].endswith(".fixed_point_equation_bridge")
                and result["accepted"]
                for result in payload["results"]
            )
        )
        self.assertTrue(
            any(
                result["subject"].endswith(".fixed_point_construction_cases")
                and result["accepted"]
                for result in payload["results"]
            )
        )
        self.assertTrue(
            any(
                result["subject"].endswith(
                    ".fixed_point_construction_frontier_status"
                )
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

    def test_json_payload_exposes_validation_summary(self):
        report = validate_formal_confidence_targets(self.manifest, WILLARD_MAP)

        payload = formal_confidence.formal_confidence_report_payload(report)

        self.assertEqual(
            payload["validation_summary"],
            FORMAL_CONFIDENCE_VALIDATION_SUMMARY,
        )
        self.assertEqual(payload["validation_summary"]["accepted_validation_count"], 19)
        self.assertEqual(payload["validation_summary"]["failed_validation_count"], 0)
        self.assertEqual(
            payload["validation_summary"]["accepted_frontier_subjects"],
            [FORMAL_CONFIDENCE_FRONTIER_SUBJECT],
        )
        self.assertEqual(
            payload["validation_summary"]["accepted_frontier_labels"],
            ["fixed_point_construction_frontier_status"],
        )
        self.assertEqual(len(payload["results"]), 19)
        self.assertTrue(all(result["accepted"] for result in payload["results"]))

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
        self.assertIn("substitution graph correctness target accepted", text)
        self.assertIn("substitution graph correctness cases accepted", text)
        self.assertIn("fixed-point equation candidate accepted", text)
        self.assertIn("fixed-point equation bridge accepted", text)
        self.assertIn("fixed-point construction cases accepted", text)
        self.assertIn("fixed-point construction frontier status accepted", text)
        self.assertIn("fixed-point obstruction accepted", text)
        self.assertNotIn("FAIL", text)

    def test_text_report_exposes_validation_summary(self):
        report = validate_formal_confidence_targets(self.manifest, WILLARD_MAP)

        text = formal_confidence.format_formal_confidence_report(report)

        self.assertIn(
            (
                "Validation summary: 19 accepted, 0 failed; "
                "fixed_point_construction_frontier_status accepted"
            ),
            text,
        )

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

    def test_missing_fixed_point_equation_bridge_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["configuration"]["fixed_point_equation_bridge"] = (
                "claims/missing_fixed_point_equation_bridge_targets.json"
            )
            target_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_formal_confidence_targets(target_path)

            report = validate_formal_confidence_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("target-fixed-point-equation-bridge", report.failed_subjects)
        self.assertTrue(
            any("fixed-point equation bridge rejected" in result.detail for result in report.results)
        )

    def test_missing_fixed_point_construction_cases_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["configuration"]["fixed_point_construction_cases"] = (
                "claims/missing_fixed_point_construction_cases.json"
            )
            target_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_formal_confidence_targets(target_path)

            report = validate_formal_confidence_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("target-fixed-point-construction-cases", report.failed_subjects)
        self.assertTrue(
            any("fixed-point construction cases rejected" in result.detail for result in report.results)
        )

    def test_missing_fixed_point_construction_frontier_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["configuration"][
                "fixed_point_construction_frontier_status"
            ] = "claims/missing_fixed_point_construction_frontier_status.json"
            target_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_formal_confidence_targets(target_path)

            report = validate_formal_confidence_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn(
            "target-fixed-point-construction-frontier-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                "fixed-point construction frontier status rejected" in result.detail
                for result in report.results
            )
        )

    def test_promoted_fixed_point_construction_frontier_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            status_path = Path(tmp) / "frontier-status.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            status_data = json.loads(
                FIXED_POINT_CONSTRUCTION_FRONTIER_STATUS.read_text(
                    encoding="utf-8"
                )
            )
            status_data["frontier_status"] = "fixed-point-equation-proved"
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            data["targets"][0]["configuration"][
                "fixed_point_construction_frontier_status"
            ] = str(status_path)
            target_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_formal_confidence_targets(target_path)

            report = validate_formal_confidence_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn(
            "target-fixed-point-construction-frontier-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                "fixed-point construction frontier status rejected" in result.detail
                for result in report.results
            )
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

    def test_missing_substitution_graph_correctness_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["configuration"]["substitution_graph_correctness"] = (
                "claims/missing_substitution_graph_correctness_targets.json"
            )
            target_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_formal_confidence_targets(target_path)

            report = validate_formal_confidence_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("target-substitution-graph-correctness", report.failed_subjects)
        self.assertTrue(
            any("substitution graph correctness target rejected" in result.detail for result in report.results)
        )

    def test_missing_substitution_graph_correctness_cases_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["configuration"]["substitution_graph_correctness_cases"] = (
                "claims/missing_substitution_graph_correctness_cases.json"
            )
            target_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_formal_confidence_targets(target_path)

            report = validate_formal_confidence_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn(
            "target-substitution-graph-correctness-cases",
            report.failed_subjects,
        )
        self.assertTrue(
            any("substitution graph correctness cases rejected" in result.detail for result in report.results)
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
