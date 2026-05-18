import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.chain_evidence_bundle import (
    chain_registry_validation_report_payload,
    format_chain_registry_validation_report,
    load_chain_evidence_bundle_registry,
    run_chain_evidence_bundle_cli,
    validate_chain_evidence_bundle_registry,
)


REGISTRY = Path("evidence/chains/manifest.json")
BUNDLE = Path("evidence/chains/neighbor_delivery_chain_bundle.json")
REJECTION_BUNDLE = Path("evidence/chains/neighbor_delivery_rejection_chain_bundle.json")
BUNDLE_ID = "neighbor-delivery-recipient-chain-evidence-bundle"
REJECTION_BUNDLE_ID = "neighbor-delivery-recipient-rejection-chain-evidence-bundle"
CLAIM_ID = "UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED"
REJECTION_CLAIM_ID = "UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-REJECTED"
STATUS = "neighbor-delivery-consumed"
REJECTION_STATUS = "recipient-not-consumed"


class ChainEvidenceBundleRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_chain_evidence_bundle_registry(REGISTRY)

    def test_registry_names_the_chain_evidence_surface(self):
        self.assertEqual(self.registry.schema_version, 1)
        self.assertEqual(
            self.registry.registry_id,
            "transition-chain-evidence-bundle-registry",
        )
        self.assertEqual(self.registry.reviewed_at, "2026-05-17")
        self.assertIn("transition-chain evidence bundles", self.registry.purpose)

    def test_registry_records_neighbor_delivery_chain_bundle(self):
        entries = {entry.bundle_id: entry for entry in self.registry.bundles}
        entry = entries[BUNDLE_ID]
        rejection_entry = entries[REJECTION_BUNDLE_ID]

        self.assertEqual(len(entries), 2)
        self.assertEqual(entry.path, BUNDLE)
        self.assertEqual(entry.chain_claim_id, CLAIM_ID)
        self.assertEqual(entry.expected_status, STATUS)
        self.assertEqual(rejection_entry.path, REJECTION_BUNDLE)
        self.assertEqual(rejection_entry.chain_claim_id, REJECTION_CLAIM_ID)
        self.assertEqual(rejection_entry.expected_status, REJECTION_STATUS)

    def test_registry_validates_registered_chain_bundles(self):
        results = validate_chain_evidence_bundle_registry(self.registry)

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)
        self.assertEqual(
            {result.subject for result in results},
            {
                "registry-schema",
                "registry-entries",
                "registry-bundle-paths",
                "registry-bundle-validation",
                "registry-completeness",
            },
        )

    def test_duplicate_chain_bundle_ids_are_rejected(self):
        entry = self.registry.bundles[0]
        drifted = replace(self.registry, bundles=(entry, entry))

        results = validate_chain_evidence_bundle_registry(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "registry-entries"
                and "duplicate bundle ids" in result.detail
                for result in results
            ),
            results,
        )

    def test_missing_chain_bundle_path_is_rejected(self):
        entry = self.registry.bundles[0]
        drifted_entry = replace(entry, path=Path("evidence/chains/missing_bundle.json"))
        drifted = replace(self.registry, bundles=(drifted_entry,))

        results = validate_chain_evidence_bundle_registry(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "registry-bundle-paths"
                and "missing bundle" in result.detail
                for result in results
            ),
            results,
        )

    def test_unregistered_chain_bundle_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = Path(tmp) / "manifest.json"
            registered_bundle = Path(tmp) / "registered_bundle.json"
            unregistered_bundle = Path(tmp) / "unregistered_bundle.json"

            registered_bundle.write_text(
                BUNDLE.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            unregistered_bundle.write_text(
                BUNDLE.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            registry_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "registry_id": "drifted-chain-registry",
                        "reviewed_at": "2026-05-17",
                        "purpose": "Exercise chain registry completeness.",
                        "bundles": [
                            {
                                "bundle_id": BUNDLE_ID,
                                "path": str(registered_bundle),
                                "chain_claim_id": CLAIM_ID,
                                "expected_status": STATUS,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            registry = load_chain_evidence_bundle_registry(registry_path)
            results = validate_chain_evidence_bundle_registry(registry)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "registry-completeness"
                and "unregistered bundle files" in result.detail
                for result in results
            ),
            results,
        )

    def test_report_formats_successful_registry_validation(self):
        results = validate_chain_evidence_bundle_registry(self.registry)

        report = format_chain_registry_validation_report(self.registry, results)

        self.assertIn(
            "Transition chain evidence registry: "
            "transition-chain-evidence-bundle-registry",
            report,
        )
        self.assertIn("OK registry-schema: registry schema accepted", report)
        self.assertIn("OK registry-bundle-validation: validated 2 bundles", report)
        self.assertNotIn("FAIL", report)

    def test_json_payload_records_successful_registry_validation(self):
        results = validate_chain_evidence_bundle_registry(self.registry)

        payload = chain_registry_validation_report_payload(self.registry, results)

        self.assertTrue(payload["accepted"])
        self.assertEqual(
            payload["registry_id"],
            "transition-chain-evidence-bundle-registry",
        )
        self.assertEqual(payload["bundle_count"], 2)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["result_count"], len(results))
        self.assertEqual(
            payload["bundles"],
            [
                {
                    "bundle_id": BUNDLE_ID,
                    "path": str(BUNDLE),
                    "chain_claim_id": CLAIM_ID,
                    "expected_status": STATUS,
                },
                {
                    "bundle_id": REJECTION_BUNDLE_ID,
                    "path": str(REJECTION_BUNDLE),
                    "chain_claim_id": REJECTION_CLAIM_ID,
                    "expected_status": REJECTION_STATUS,
                }
            ],
        )

    def test_cli_validates_checked_in_registry(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_chain_evidence_bundle_cli(
                ["--registry", str(REGISTRY)]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Transition chain evidence registry:", output)
        self.assertIn("OK registry-completeness", output)

    def test_module_execution_runs_json_registry_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.chain_evidence_bundle",
                "--registry",
                str(REGISTRY),
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
        self.assertEqual(payload["bundle_count"], 2)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["bundles"][0]["bundle_id"], BUNDLE_ID)
        self.assertEqual(payload["bundles"][0]["path"], str(BUNDLE))
        self.assertEqual(payload["bundles"][1]["bundle_id"], REJECTION_BUNDLE_ID)
        self.assertEqual(payload["bundles"][1]["path"], str(REJECTION_BUNDLE))

    def test_json_payload_summarizes_failed_subjects(self):
        entry = self.registry.bundles[0]
        drifted_entry = replace(entry, path=Path("evidence/chains/missing_bundle.json"))
        drifted = replace(self.registry, bundles=(drifted_entry,))
        results = validate_chain_evidence_bundle_registry(drifted)

        payload = chain_registry_validation_report_payload(drifted, results)

        self.assertFalse(payload["accepted"])
        self.assertEqual(
            payload["failed_subjects"],
            [
                "registry-bundle-paths",
                "registry-bundle-validation",
                "registry-completeness",
            ],
        )

    def test_module_execution_emits_json_failure_summary_for_missing_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = Path(tmp) / "manifest.json"
            registry_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "registry_id": "drifted-chain-registry",
                        "reviewed_at": "2026-05-17",
                        "purpose": "Exercise JSON failure summary.",
                        "bundles": [
                            {
                                "bundle_id": BUNDLE_ID,
                                "path": "evidence/chains/missing_bundle.json",
                                "chain_claim_id": CLAIM_ID,
                                "expected_status": STATUS,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "autarkic_systems.chain_evidence_bundle",
                    "--registry",
                    str(registry_path),
                    "--format",
                    "json",
                ],
                check=False,
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1, payload)
        self.assertFalse(payload["accepted"])
        self.assertEqual(
            payload["failed_subjects"],
            ["registry-bundle-paths", "registry-bundle-validation"],
        )


if __name__ == "__main__":
    unittest.main()
