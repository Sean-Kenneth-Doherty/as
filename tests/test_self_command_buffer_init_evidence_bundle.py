import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.evidence_bundle import (
    load_evidence_bundle_registry,
    load_transition_evidence_bundle,
    validate_evidence_bundle_registry,
    validate_transition_evidence_bundle,
)


BUNDLE = Path("evidence/self_command_buffer_init_bundle.json")
REGISTRY = Path("evidence/manifest.json")
BUNDLE_ID = "self-command-buffer-init-evidence-bundle"
CLAIM_ID = "UC-STEM-COMMAND-BUFFER-SELF-INIT"
EXAMPLE = "self command buffer processor left init"
STATUS = "stem-command-buffer-self-processed"


class SelfCommandBufferInitEvidenceBundleTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_transition_evidence_bundle(BUNDLE)

    def test_bundle_names_the_existing_self_command_buffer_init_transition(self):
        self.assertEqual(self.bundle.schema_version, 1)
        self.assertEqual(self.bundle.bundle_id, BUNDLE_ID)
        self.assertEqual(self.bundle.claim_id, CLAIM_ID)
        self.assertEqual(
            self.bundle.predicate,
            "stem_command_buffer_executes_self_init",
        )
        self.assertEqual(self.bundle.positive_example, EXAMPLE)
        self.assertEqual(self.bundle.transition_function, "step_stem_cell")
        self.assertEqual(self.bundle.expected_status, STATUS)

    def test_bundle_records_self_command_buffer_artifact_paths(self):
        self.assertEqual(self.bundle.claim_manifest_path, Path("claims/transition_claims.json"))
        self.assertEqual(
            self.bundle.proof_certificate_path,
            Path("claims/proof_certificates.json"),
        )
        self.assertEqual(
            self.bundle.schematic_trace_path,
            Path("schematics/self_command_buffer_init_trace.json"),
        )
        self.assertEqual(
            self.bundle.schematic_svg_path,
            Path("schematics/self_command_buffer_init_trace.svg"),
        )
        self.assertEqual(
            self.bundle.hardware_witness_map_path,
            Path("sources/prc_hardware_witness_map.json"),
        )
        self.assertEqual(
            self.bundle.source_status_paths,
            (
                Path("sources/stem_command_execution_source_status.json"),
                Path("sources/recipient_non_init_command_source_status.json"),
                Path("sources/standard_signal_command_semantics_status.json"),
                Path("sources/write_buffer_command_semantics_status.json"),
            ),
        )

    def test_bundle_validates_claim_proof_trace_svg_and_statuses(self):
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

    def test_registry_includes_self_command_buffer_init_bundle(self):
        registry = load_evidence_bundle_registry(REGISTRY)
        entries = {entry.bundle_id: entry for entry in registry.bundles}

        self.assertEqual(len(entries), 7)
        self.assertIn("self-mailbox-init-evidence-bundle", entries)
        self.assertIn("self-mailbox-unsupported-evidence-bundle", entries)
        self.assertIn(BUNDLE_ID, entries)
        self.assertEqual(entries[BUNDLE_ID].path, BUNDLE)
        self.assertEqual(entries[BUNDLE_ID].claim_id, CLAIM_ID)
        self.assertEqual(entries[BUNDLE_ID].expected_status, STATUS)

        results = validate_evidence_bundle_registry(registry)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_drifted_claim_id_is_rejected(self):
        drifted = replace(
            self.bundle,
            claim_id="UC-STEM-SELF-MAILBOX-INIT-COMMAND",
        )

        results = validate_transition_evidence_bundle(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "claim-example"
                and "predicate mismatch" in result.detail
                for result in results
            ),
            results,
        )


if __name__ == "__main__":
    unittest.main()
