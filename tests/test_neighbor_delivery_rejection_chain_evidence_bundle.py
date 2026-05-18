import json
import subprocess
import sys
import unittest
from pathlib import Path

from autarkic_systems.chain_evidence_bundle import (
    chain_evidence_bundle_report_payload,
    load_transition_chain_evidence_bundle,
    validate_transition_chain_evidence_bundle,
)


BUNDLE = Path("evidence/chains/neighbor_delivery_rejection_chain_bundle.json")
BUNDLE_ID = "neighbor-delivery-recipient-rejection-chain-evidence-bundle"
CLAIM_ID = "UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-REJECTED"
EXAMPLE = "neighbor c write buffer delivery rejected by recipient"
STATUS = "recipient-not-consumed"


class NeighborDeliveryRejectionChainEvidenceBundleTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_transition_chain_evidence_bundle(BUNDLE)

    def test_bundle_names_the_rejection_chain_claim(self):
        self.assertEqual(self.bundle.schema_version, 1)
        self.assertEqual(self.bundle.bundle_id, BUNDLE_ID)
        self.assertEqual(self.bundle.chain_claim_id, CLAIM_ID)
        self.assertEqual(
            self.bundle.predicate,
            "neighbor_delivery_rejected_by_recipient",
        )
        self.assertEqual(self.bundle.positive_example, EXAMPLE)
        self.assertEqual(
            self.bundle.transition_chain_function,
            "execute_neighbor_delivery_recipient_chain",
        )
        self.assertEqual(self.bundle.expected_status, STATUS)

    def test_bundle_records_rejection_artifact_paths(self):
        self.assertEqual(
            self.bundle.chain_trace_path,
            Path("schematics/chains/neighbor_delivery_rejection_chain_trace.json"),
        )
        self.assertEqual(
            self.bundle.chain_svg_path,
            Path("schematics/chains/neighbor_delivery_rejection_chain_trace.svg"),
        )
        self.assertEqual(
            self.bundle.transition_bundle_paths,
            (
                Path("evidence/neighbor_command_buffer_delivery_bundle.json"),
                Path("evidence/recipient_non_init_command_rejection_bundle.json"),
            ),
        )
        self.assertIn(
            Path("sources/recipient_non_init_command_source_status.json"),
            self.bundle.source_status_paths,
        )

    def test_bundle_validates_rejection_chain_evidence_surface(self):
        results = validate_transition_chain_evidence_bundle(self.bundle)

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)
        self.assertEqual(
            {result.subject for result in results},
            {
                "schema",
                "chain-claim-example",
                "chain-proof-certificate",
                "chain-language",
                "chain-trace",
                "chain-svg",
                "underlying-transition-bundles",
                "source-statuses",
                "boundary",
            },
        )

    def test_json_payload_records_successful_rejection_bundle_validation(self):
        results = validate_transition_chain_evidence_bundle(self.bundle)

        payload = chain_evidence_bundle_report_payload(self.bundle, results)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["bundle_id"], BUNDLE_ID)
        self.assertEqual(payload["chain_claim_id"], CLAIM_ID)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["result_count"], 9)

    def test_module_execution_runs_json_rejection_bundle_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.chain_evidence_bundle",
                "--bundle",
                str(BUNDLE),
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
        self.assertEqual(payload["chain_claim_id"], CLAIM_ID)
        self.assertEqual(payload["failed_subjects"], [])


if __name__ == "__main__":
    unittest.main()
