import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.evidence_bundle import (
    load_transition_evidence_bundle,
    validate_transition_evidence_bundle,
)


BUNDLE = Path("evidence/recipient_init_command_message_bundle.json")
CLAIM_ID = "UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED"
EXAMPLE = "fixed upstream wire right init processed"
STATUS = "recipient-init-command-message-processed"


class RecipientInitTransitionEvidenceBundleTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_transition_evidence_bundle(BUNDLE)

    def test_bundle_names_the_existing_recipient_init_transition(self):
        self.assertEqual(self.bundle.schema_version, 1)
        self.assertEqual(
            self.bundle.bundle_id,
            "recipient-init-command-message-transition-evidence-bundle",
        )
        self.assertEqual(self.bundle.claim_id, CLAIM_ID)
        self.assertEqual(
            self.bundle.predicate,
            "recipient_init_command_message_processed",
        )
        self.assertEqual(self.bundle.positive_example, EXAMPLE)
        self.assertEqual(self.bundle.transition_function, "step_fixed_cell")
        self.assertEqual(self.bundle.expected_status, STATUS)

    def test_bundle_records_all_cross_layer_artifact_paths(self):
        self.assertEqual(self.bundle.claim_manifest_path, Path("claims/transition_claims.json"))
        self.assertEqual(
            self.bundle.proof_certificate_path,
            Path("claims/proof_certificates.json"),
        )
        self.assertEqual(
            self.bundle.schematic_trace_path,
            Path("schematics/recipient_init_command_message_trace.json"),
        )
        self.assertEqual(
            self.bundle.schematic_svg_path,
            Path("schematics/recipient_init_command_message_trace.svg"),
        )
        self.assertEqual(
            self.bundle.hardware_witness_map_path,
            Path("sources/prc_hardware_witness_map.json"),
        )
        self.assertEqual(
            self.bundle.source_status_paths,
            (
                Path("sources/recipient_command_consumption_source_status.json"),
                Path("sources/recipient_non_init_command_source_status.json"),
                Path("sources/standard_signal_command_semantics_status.json"),
                Path("sources/write_buffer_command_semantics_status.json"),
            ),
        )

    def test_bundle_validates_claim_proof_trace_svg_and_source_statuses(self):
        results = validate_transition_evidence_bundle(self.bundle)

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)
        self.assertEqual(
            {result.subject for result in results},
            {
                "schema",
                "claim-example",
                "proof-certificate",
                "schematic-trace",
                "schematic-svg",
                "source-statuses",
                "boundary",
            },
        )

    def test_drifted_claim_id_is_rejected(self):
        drifted = replace(self.bundle, claim_id="UC-UNKNOWN")

        results = validate_transition_evidence_bundle(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "claim-example"
                and "missing claim" in result.detail
                for result in results
            ),
            results,
        )

    def test_missing_svg_path_is_rejected(self):
        drifted = replace(
            self.bundle,
            schematic_svg_path=Path("schematics/missing-recipient-init.svg"),
        )

        results = validate_transition_evidence_bundle(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "schematic-svg"
                and "missing SVG" in result.detail
                for result in results
            ),
            results,
        )


if __name__ == "__main__":
    unittest.main()
