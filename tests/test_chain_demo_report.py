import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems.chain_demo import (
    build_chain_demo_report,
    build_chain_demo_registry_report,
    format_chain_demo_report,
    format_chain_demo_registry_report,
    run_chain_demo_cli,
)


BUNDLE = Path("evidence/chains/neighbor_delivery_chain_bundle.json")
REGISTRY = Path("evidence/chains/manifest.json")
BUNDLE_ID = "neighbor-delivery-recipient-chain-evidence-bundle"
REJECTION_BUNDLE_ID = "neighbor-delivery-recipient-rejection-chain-evidence-bundle"
CLAIM_ID = "UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED"
TRACE = "schematics/chains/neighbor_delivery_recipient_chain_trace.json"
SVG = "schematics/chains/neighbor_delivery_recipient_chain_trace.svg"


class ChainDemoReportTests(unittest.TestCase):
    def test_payload_maps_the_vertical_chain_evidence_surface(self):
        report = build_chain_demo_report(BUNDLE)

        self.assertTrue(report["accepted"])
        self.assertEqual(report["bundle_id"], BUNDLE_ID)
        self.assertEqual(report["chain_claim_id"], CLAIM_ID)
        self.assertEqual(
            report["predicate"],
            "neighbor_delivery_consumed_by_recipient",
        )
        self.assertEqual(
            report["transition_chain_function"],
            "execute_neighbor_delivery_recipient_chain",
        )
        self.assertEqual(report["validation"]["failed_subjects"], [])
        self.assertEqual(report["validation"]["result_count"], 9)
        self.assertEqual(report["missing_evidence_paths"], [])

        layers = {(layer["role"], layer["path"]) for layer in report["evidence_layers"]}
        self.assertIn(("chain-claim-manifest", "claims/transition_chain_claims.json"), layers)
        self.assertIn(
            (
                "chain-proof-certificates",
                "claims/transition_chain_proof_certificates.json",
            ),
            layers,
        )
        self.assertIn(("chain-language", "language/transition_chain_claim_language.json"), layers)
        self.assertIn(("chain-trace", TRACE), layers)
        self.assertIn(("chain-svg", SVG), layers)
        self.assertIn(
            (
                "transition-bundle",
                "evidence/neighbor_command_buffer_delivery_bundle.json",
            ),
            layers,
        )
        self.assertIn(
            (
                "transition-bundle",
                "evidence/recipient_init_command_message_bundle.json",
            ),
            layers,
        )
        self.assertIn(
            (
                "source-status",
                "sources/recipient_command_consumption_source_status.json",
            ),
            layers,
        )
        self.assertTrue(all(layer["exists"] for layer in report["evidence_layers"]))
        self.assertGreaterEqual(len(report["boundaries"]), 1)

    def test_payload_reports_missing_evidence_layer_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            drifted_bundle = Path(tmp) / "drifted_chain_bundle.json"
            data = json.loads(BUNDLE.read_text(encoding="utf-8"))
            missing_path = "sources/missing_chain_demo_status.json"
            data["artifacts"]["source_statuses"] = [missing_path]
            drifted_bundle.write_text(json.dumps(data), encoding="utf-8")

            report = build_chain_demo_report(drifted_bundle)

        self.assertFalse(report["accepted"])
        self.assertEqual(report["missing_evidence_paths"], [missing_path])
        missing_layers = [
            layer for layer in report["evidence_layers"] if not layer["exists"]
        ]
        self.assertEqual(
            missing_layers,
            [{"role": "source-status", "path": missing_path, "exists": False}],
        )

    def test_text_report_summarizes_claim_validation_and_artifacts(self):
        report = build_chain_demo_report(BUNDLE)

        text = format_chain_demo_report(report)

        self.assertIn("Vertical chain demo: neighbor-delivery-recipient-chain-evidence-bundle", text)
        self.assertIn(f"Claim: {CLAIM_ID}", text)
        self.assertIn("Validation: accepted", text)
        self.assertIn(f"Trace: {TRACE}", text)
        self.assertIn(f"SVG: {SVG}", text)
        self.assertIn("Missing evidence paths: none", text)
        self.assertIn("Transition bundles: 2", text)
        self.assertIn("Source-status boundaries: 5", text)
        self.assertNotIn("FAIL", text)

    def test_json_mode_preserves_failed_subject_summary_for_success(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_chain_demo_cli(
                ["--bundle", str(BUNDLE), "--format", "json"]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["validation"]["failed_subjects"], [])
        self.assertEqual(payload["missing_evidence_paths"], [])
        self.assertTrue(
            any(
                layer["role"] == "chain-svg"
                and layer["path"] == SVG
                and layer["exists"]
                for layer in payload["evidence_layers"]
            )
        )

    def test_registry_payload_summarizes_all_chain_demo_reports(self):
        report = build_chain_demo_registry_report(REGISTRY)

        self.assertTrue(report["accepted"])
        self.assertEqual(
            report["registry_id"],
            "transition-chain-evidence-bundle-registry",
        )
        self.assertEqual(report["bundle_count"], 2)
        self.assertEqual(report["accepted_count"], 2)
        self.assertEqual(report["failed_count"], 0)
        self.assertEqual(report["missing_evidence_paths"], [])
        self.assertEqual(report["validation"]["failed_subjects"], [])
        self.assertEqual(
            [item["bundle_id"] for item in report["bundle_reports"]],
            [BUNDLE_ID, REJECTION_BUNDLE_ID],
        )
        self.assertTrue(
            all(item["accepted"] for item in report["bundle_reports"]),
            report["bundle_reports"],
        )

    def test_registry_text_report_names_both_chain_bundles(self):
        report = build_chain_demo_registry_report(REGISTRY)

        text = format_chain_demo_registry_report(report)

        self.assertIn(
            "Vertical chain demo registry: transition-chain-evidence-bundle-registry",
            text,
        )
        self.assertIn("Bundles: 2", text)
        self.assertIn("Accepted: 2", text)
        self.assertIn("Failed: 0", text)
        self.assertIn("Missing evidence paths: none", text)
        self.assertIn(BUNDLE_ID, text)
        self.assertIn(REJECTION_BUNDLE_ID, text)

    def test_registry_json_mode_reports_all_registered_bundles(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_chain_demo_cli(
                ["--registry", str(REGISTRY), "--format", "json"]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["bundle_count"], 2)
        self.assertEqual(
            [item["bundle_id"] for item in payload["bundle_reports"]],
            [BUNDLE_ID, REJECTION_BUNDLE_ID],
        )

    def test_registry_json_mode_reports_missing_bundle_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = Path(tmp) / "manifest.json"
            registry_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "registry_id": "drifted-chain-demo-registry",
                        "reviewed_at": "2026-05-17",
                        "purpose": "Exercise demo registry failure reporting.",
                        "bundles": [
                            {
                                "bundle_id": BUNDLE_ID,
                                "path": "evidence/chains/missing_bundle.json",
                                "chain_claim_id": CLAIM_ID,
                                "expected_status": "neighbor-delivery-consumed",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = run_chain_demo_cli(
                    ["--registry", str(registry_path), "--format", "json"]
                )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1, payload)
        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["bundle_count"], 1)
        self.assertEqual(payload["accepted_count"], 0)
        self.assertEqual(payload["failed_count"], 1)
        self.assertEqual(
            payload["missing_evidence_paths"],
            ["evidence/chains/missing_bundle.json"],
        )
        self.assertEqual(payload["bundle_reports"], [])
        self.assertEqual(
            payload["validation"]["failed_subjects"],
            ["registry-bundle-paths", "registry-bundle-validation"],
        )

    def test_module_execution_runs_registry_text_demo_report(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.chain_demo",
                "--registry",
                str(REGISTRY),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Vertical chain demo registry:", completed.stdout)
        self.assertIn(BUNDLE_ID, completed.stdout)
        self.assertIn(REJECTION_BUNDLE_ID, completed.stdout)

    def test_cli_rejects_ambiguous_bundle_and_registry_targets(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.chain_demo",
                "--bundle",
                str(BUNDLE),
                "--registry",
                str(REGISTRY),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 2, completed)
        self.assertIn("not allowed with argument", completed.stderr)

    def test_drifted_bundle_report_exposes_validation_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            drifted_bundle = Path(tmp) / "drifted_chain_bundle.json"
            data = json.loads(BUNDLE.read_text(encoding="utf-8"))
            data["expected_status"] = "recipient-not-consumed"
            drifted_bundle.write_text(json.dumps(data), encoding="utf-8")

            report = build_chain_demo_report(drifted_bundle)

        self.assertFalse(report["accepted"])
        self.assertEqual(
            report["validation"]["failed_subjects"],
            ["chain-claim-example", "chain-trace"],
        )

    def test_module_execution_runs_text_demo_report(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.chain_demo",
                "--bundle",
                str(BUNDLE),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Vertical chain demo:", completed.stdout)
        self.assertIn("Validation: accepted", completed.stdout)

    def test_module_execution_returns_one_for_drifted_json_demo_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            drifted_bundle = Path(tmp) / "drifted_chain_bundle.json"
            data = json.loads(BUNDLE.read_text(encoding="utf-8"))
            data["expected_status"] = "recipient-not-consumed"
            drifted_bundle.write_text(json.dumps(data), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "autarkic_systems.chain_demo",
                    "--bundle",
                    str(drifted_bundle),
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
            payload["validation"]["failed_subjects"],
            ["chain-claim-example", "chain-trace"],
        )


if __name__ == "__main__":
    unittest.main()
