import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.network_sequence_evidence_bundle import (
    format_network_sequence_evidence_bundle_report,
    format_network_sequence_registry_validation_report,
    load_network_sequence_evidence_bundle,
    load_network_sequence_evidence_bundle_registry,
    network_sequence_evidence_bundle_report_payload,
    network_sequence_registry_validation_report_payload,
    run_network_sequence_evidence_bundle_cli,
    validate_network_sequence_evidence_bundle,
    validate_network_sequence_evidence_bundle_registry,
)


BUNDLE = Path("evidence/sequences/post_handoff_signal_bundle.json")
REGISTRY = Path("evidence/sequences/manifest.json")
BUNDLE_ID = "post-handoff-signal-sequence-evidence-bundle"
CLAIM_ID = "UC-SEQUENCE-POST-HANDOFF-SIGNAL-ROUTED"
PREDICATE = "post_handoff_signal_routed"
EXAMPLE = "proc left init handoff routes later binary signal"
STATUS = "post-handoff-signal-routed"
TRACE = Path("schematics/sequences/post_handoff_signal_sequence_trace.json")
SVG = Path("schematics/sequences/post_handoff_signal_sequence_trace.svg")


def _write_registry_with_drifted_existing_bundle(directory: Path) -> Path:
    bundle_path = directory / "post_handoff_signal_bundle.json"
    registry_path = directory / "manifest.json"

    bundle_data = json.loads(BUNDLE.read_text(encoding="utf-8"))
    bundle_data["expected_status"] = "handoff-not-init-consumed"
    bundle_path.write_text(json.dumps(bundle_data), encoding="utf-8")

    registry_data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    registry_data["bundles"][0]["path"] = str(bundle_path)
    registry_path.write_text(json.dumps(registry_data), encoding="utf-8")
    return registry_path


class NetworkSequenceEvidenceBundleTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_network_sequence_evidence_bundle(BUNDLE)
        self.registry = load_network_sequence_evidence_bundle_registry(REGISTRY)

    def test_bundle_names_post_handoff_sequence_claim(self):
        self.assertEqual(self.bundle.schema_version, 1)
        self.assertEqual(self.bundle.bundle_id, BUNDLE_ID)
        self.assertEqual(self.bundle.sequence_claim_id, CLAIM_ID)
        self.assertEqual(self.bundle.predicate, PREDICATE)
        self.assertEqual(self.bundle.positive_example, EXAMPLE)
        self.assertEqual(
            self.bundle.sequence_function,
            "execute_post_handoff_signal_witness",
        )
        self.assertEqual(self.bundle.expected_status, STATUS)

    def test_bundle_records_artifact_paths(self):
        self.assertEqual(
            self.bundle.sequence_claim_manifest_path,
            Path("claims/network_sequence_claims.json"),
        )
        self.assertEqual(
            self.bundle.sequence_proof_certificate_path,
            Path("claims/network_sequence_proof_certificates.json"),
        )
        self.assertEqual(
            self.bundle.sequence_language_path,
            Path("language/network_sequence_claim_language.json"),
        )
        self.assertEqual(
            self.bundle.sequence_claim_validator_path,
            Path("autarkic_systems/network_sequence_claims.py"),
        )
        self.assertEqual(
            self.bundle.sequence_witness_path,
            Path("autarkic_systems/network_sequence.py"),
        )
        self.assertEqual(self.bundle.sequence_trace_path, TRACE)
        self.assertEqual(self.bundle.sequence_svg_path, SVG)
        self.assertEqual(
            self.bundle.chain_bundle_paths,
            (Path("evidence/chains/neighbor_delivery_chain_bundle.json"),),
        )
        self.assertIn(
            Path("sources/recipient_command_consumption_source_status.json"),
            self.bundle.source_status_paths,
        )

    def test_bundle_validates_claim_proof_witness_chain_sources_and_boundary(self):
        results = validate_network_sequence_evidence_bundle(self.bundle)

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)
        self.assertEqual(
            {result.subject for result in results},
            {
                "schema",
                "sequence-claim-example",
                "sequence-proof-certificate",
                "sequence-language",
                "sequence-witness",
                "sequence-trace",
                "sequence-svg",
                "underlying-chain-bundles",
                "source-statuses",
                "boundary",
            },
        )

    def test_drifted_expected_status_is_rejected(self):
        drifted = replace(self.bundle, expected_status="followup-not-routed")

        results = validate_network_sequence_evidence_bundle(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "sequence-witness"
                and "status mismatch" in result.detail
                for result in results
            ),
            results,
        )

    def test_missing_sequence_language_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing_network_sequence_claim_language.json"
            drifted = replace(self.bundle, sequence_language_path=missing)

            results = validate_network_sequence_evidence_bundle(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "schema"
                and str(missing) in result.detail
                for result in results
            ),
            results,
        )
        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "sequence-language"
                for result in results
            ),
            results,
        )

    def test_missing_sequence_trace_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing_post_handoff_sequence_trace.json"
            drifted = replace(self.bundle, sequence_trace_path=missing)

            results = validate_network_sequence_evidence_bundle(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "schema"
                and str(missing) in result.detail
                for result in results
            ),
            results,
        )
        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "sequence-trace"
                for result in results
            ),
            results,
        )

    def test_missing_sequence_svg_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing_post_handoff_sequence_trace.svg"
            drifted = replace(self.bundle, sequence_svg_path=missing)

            results = validate_network_sequence_evidence_bundle(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "schema"
                and str(missing) in result.detail
                for result in results
            ),
            results,
        )
        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "sequence-svg"
                for result in results
            ),
            results,
        )

    def test_report_and_json_payload_record_bundle_validation(self):
        results = validate_network_sequence_evidence_bundle(self.bundle)

        report = format_network_sequence_evidence_bundle_report(self.bundle, results)
        payload = network_sequence_evidence_bundle_report_payload(self.bundle, results)

        self.assertIn("Network sequence evidence bundle:", report)
        self.assertIn("OK sequence-language:", report)
        self.assertIn("OK sequence-witness:", report)
        self.assertIn("OK sequence-trace:", report)
        self.assertIn("OK sequence-svg:", report)
        self.assertNotIn("FAIL", report)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["bundle_id"], BUNDLE_ID)
        self.assertEqual(payload["sequence_claim_id"], CLAIM_ID)
        self.assertEqual(payload["failed_subjects"], [])

    def test_registry_records_and_validates_checked_in_bundle(self):
        self.assertEqual(self.registry.schema_version, 1)
        self.assertEqual(
            self.registry.registry_id,
            "network-sequence-evidence-bundle-registry",
        )
        self.assertEqual(len(self.registry.bundles), 1)
        entry = self.registry.bundles[0]
        self.assertEqual(entry.bundle_id, BUNDLE_ID)
        self.assertEqual(entry.path, BUNDLE)
        self.assertEqual(entry.sequence_claim_id, CLAIM_ID)
        self.assertEqual(entry.expected_status, STATUS)

        results = validate_network_sequence_evidence_bundle_registry(self.registry)

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

    def test_registry_json_payload_records_bundle_entry(self):
        results = validate_network_sequence_evidence_bundle_registry(self.registry)

        payload = network_sequence_registry_validation_report_payload(
            self.registry,
            results,
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["bundle_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["bundle_failed_subjects"], [])
        self.assertEqual(
            payload["bundles"],
            [
                {
                    "bundle_id": BUNDLE_ID,
                    "path": str(BUNDLE),
                    "sequence_claim_id": CLAIM_ID,
                    "expected_status": STATUS,
                }
            ],
        )

    def test_registry_json_payload_records_inner_bundle_failed_subjects(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = _write_registry_with_drifted_existing_bundle(Path(tmp))
            registry = load_network_sequence_evidence_bundle_registry(registry_path)
            results = validate_network_sequence_evidence_bundle_registry(registry)

            payload = network_sequence_registry_validation_report_payload(
                registry,
                results,
            )

        self.assertFalse(payload["accepted"])
        self.assertIn("registry-bundle-validation", payload["failed_subjects"])
        self.assertEqual(
            payload["bundle_failed_subjects"],
            [
                {
                    "bundle_id": BUNDLE_ID,
                    "failed_subjects": ["sequence-witness", "sequence-trace"],
                }
            ],
        )

    def test_unregistered_sequence_bundle_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = Path(tmp) / "manifest.json"
            registered_bundle = Path(tmp) / "registered_bundle.json"
            unregistered_bundle = Path(tmp) / "unregistered_bundle.json"
            bundle_text = BUNDLE.read_text(encoding="utf-8")
            registered_bundle.write_text(bundle_text, encoding="utf-8")
            unregistered_bundle.write_text(bundle_text, encoding="utf-8")
            registry_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "registry_id": "drifted-sequence-registry",
                        "reviewed_at": "2026-05-18",
                        "purpose": "Exercise sequence registry completeness.",
                        "bundles": [
                            {
                                "bundle_id": BUNDLE_ID,
                                "path": str(registered_bundle),
                                "sequence_claim_id": CLAIM_ID,
                                "expected_status": STATUS,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            registry = load_network_sequence_evidence_bundle_registry(registry_path)
            results = validate_network_sequence_evidence_bundle_registry(registry)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "registry-completeness"
                and "unregistered bundle files" in result.detail
                for result in results
            ),
            results,
        )

    def test_missing_registered_bundle_keeps_registry_level_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = Path(tmp) / "manifest.json"
            missing_bundle = Path(tmp) / "missing_bundle.json"
            registry_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "registry_id": "missing-sequence-registry",
                        "reviewed_at": "2026-05-18",
                        "purpose": "Exercise missing registered bundle handling.",
                        "bundles": [
                            {
                                "bundle_id": BUNDLE_ID,
                                "path": str(missing_bundle),
                                "sequence_claim_id": CLAIM_ID,
                                "expected_status": STATUS,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            registry = load_network_sequence_evidence_bundle_registry(registry_path)
            results = validate_network_sequence_evidence_bundle_registry(registry)
            payload = network_sequence_registry_validation_report_payload(
                registry,
                results,
            )

        self.assertFalse(payload["accepted"])
        self.assertEqual(
            payload["failed_subjects"],
            ["registry-bundle-paths", "registry-bundle-validation"],
        )
        self.assertEqual(payload["bundle_failed_subjects"], [])

    def test_cli_validates_checked_in_bundle_and_registry(self):
        bundle_stdout = io.StringIO()
        registry_stdout = io.StringIO()

        with contextlib.redirect_stdout(bundle_stdout):
            bundle_exit = run_network_sequence_evidence_bundle_cli(
                ["--bundle", str(BUNDLE)]
            )
        with contextlib.redirect_stdout(registry_stdout):
            registry_exit = run_network_sequence_evidence_bundle_cli(
                ["--registry", str(REGISTRY)]
            )

        self.assertEqual(bundle_exit, 0, bundle_stdout.getvalue())
        self.assertIn("OK sequence-proof-certificate", bundle_stdout.getvalue())
        self.assertEqual(registry_exit, 0, registry_stdout.getvalue())
        self.assertIn("OK registry-completeness", registry_stdout.getvalue())

    def test_module_execution_runs_json_registry_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.network_sequence_evidence_bundle",
                "--registry",
                str(REGISTRY),
                "--format",
                "json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["bundle_count"], 1)
        self.assertEqual(payload["bundle_failed_subjects"], [])
        self.assertEqual(payload["bundles"][0]["bundle_id"], BUNDLE_ID)

    def test_module_execution_emits_registry_bundle_failed_subjects(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = _write_registry_with_drifted_existing_bundle(Path(tmp))
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "autarkic_systems.network_sequence_evidence_bundle",
                    "--registry",
                    str(registry_path),
                    "--format",
                    "json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1, payload)
        self.assertEqual(
            payload["bundle_failed_subjects"],
            [
                {
                    "bundle_id": BUNDLE_ID,
                    "failed_subjects": ["sequence-witness", "sequence-trace"],
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
