import contextlib
import io
import json
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.chain_evidence_bundle import (
    chain_evidence_bundle_report_payload,
    format_chain_evidence_bundle_report,
    load_transition_chain_evidence_bundle,
    run_chain_evidence_bundle_cli,
    validate_transition_chain_evidence_bundle,
)


BUNDLE = Path("evidence/chains/neighbor_delivery_chain_bundle.json")
BUNDLE_ID = "neighbor-delivery-recipient-chain-evidence-bundle"
CLAIM_ID = "UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED"
EXAMPLE = "neighbor b proc left delivery consumed by empty recipient"
STATUS = "neighbor-delivery-consumed"


class NeighborDeliveryChainEvidenceBundleTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_transition_chain_evidence_bundle(BUNDLE)

    def test_bundle_names_the_existing_neighbor_delivery_chain(self):
        self.assertEqual(self.bundle.schema_version, 1)
        self.assertEqual(self.bundle.bundle_id, BUNDLE_ID)
        self.assertEqual(self.bundle.chain_claim_id, CLAIM_ID)
        self.assertEqual(
            self.bundle.predicate,
            "neighbor_delivery_consumed_by_recipient",
        )
        self.assertEqual(self.bundle.positive_example, EXAMPLE)
        self.assertEqual(
            self.bundle.transition_chain_function,
            "execute_neighbor_delivery_recipient_chain",
        )
        self.assertEqual(self.bundle.expected_status, STATUS)

    def test_bundle_records_chain_artifact_paths(self):
        self.assertEqual(
            self.bundle.chain_claim_manifest_path,
            Path("claims/transition_chain_claims.json"),
        )
        self.assertEqual(
            self.bundle.chain_proof_certificate_path,
            Path("claims/transition_chain_proof_certificates.json"),
        )
        self.assertEqual(
            self.bundle.chain_language_path,
            Path("language/transition_chain_claim_language.json"),
        )
        self.assertEqual(
            self.bundle.chain_claim_validator_path,
            Path("autarkic_systems/chain_claims.py"),
        )
        self.assertEqual(
            self.bundle.chain_trace_path,
            Path("schematics/chains/neighbor_delivery_recipient_chain_trace.json"),
        )
        self.assertEqual(
            self.bundle.transition_bundle_paths,
            (
                Path("evidence/neighbor_command_buffer_delivery_bundle.json"),
                Path("evidence/recipient_init_command_message_bundle.json"),
            ),
        )
        self.assertEqual(
            self.bundle.source_status_paths,
            (
                Path("sources/stem_command_execution_source_status.json"),
                Path("sources/recipient_command_consumption_source_status.json"),
                Path("sources/recipient_non_init_command_source_status.json"),
                Path("sources/standard_signal_command_semantics_status.json"),
                Path("sources/write_buffer_command_semantics_status.json"),
            ),
        )

    def test_bundle_validates_chain_claim_language_sources_and_transition_bundles(self):
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
                "underlying-transition-bundles",
                "source-statuses",
                "boundary",
            },
        )

    def test_drifted_chain_status_is_rejected(self):
        drifted = replace(self.bundle, expected_status="recipient-not-consumed")

        results = validate_transition_chain_evidence_bundle(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "chain-claim-example"
                and "status mismatch" in result.detail
                for result in results
            ),
            results,
        )

    def test_report_formats_successful_chain_bundle_validation(self):
        results = validate_transition_chain_evidence_bundle(self.bundle)

        report = format_chain_evidence_bundle_report(self.bundle, results)

        self.assertIn(
            "Transition chain evidence bundle: "
            "neighbor-delivery-recipient-chain-evidence-bundle",
            report,
        )
        self.assertIn("OK chain-claim-example:", report)
        self.assertIn("OK underlying-transition-bundles:", report)
        self.assertNotIn("FAIL", report)

    def test_json_payload_records_successful_chain_bundle_validation(self):
        results = validate_transition_chain_evidence_bundle(self.bundle)

        payload = chain_evidence_bundle_report_payload(self.bundle, results)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["bundle_id"], BUNDLE_ID)
        self.assertEqual(payload["chain_claim_id"], CLAIM_ID)
        self.assertEqual(payload["result_count"], len(results))
        self.assertTrue(
            any(
                result["subject"] == "boundary" and result["accepted"]
                for result in payload["results"]
            )
        )

    def test_cli_returns_zero_for_checked_in_bundle(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_chain_evidence_bundle_cli(["--bundle", str(BUNDLE)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Transition chain evidence bundle:", output)
        self.assertIn("OK chain-language", output)

    def test_module_execution_runs_json_bundle_validation(self):
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


if __name__ == "__main__":
    unittest.main()
