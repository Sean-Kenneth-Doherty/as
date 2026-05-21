import contextlib
import io
import json
import subprocess
import sys
import unittest
from unittest import mock

from autarkic_systems.vertical_demo import (
    build_vertical_demo_digest,
    format_vertical_demo_digest,
    run_vertical_demo_cli,
)


DEMONSTRATION = "post-handoff signal routing through checked evidence"
SEQUENCE_BUNDLE = "evidence/sequences/post_handoff_signal_bundle.json"
TRANSITION_REGISTRY = "evidence/manifest.json"
CHAIN_REGISTRY = "evidence/chains/manifest.json"
SEQUENCE_REGISTRY = "evidence/sequences/manifest.json"
EVIDENCE_TRAIL_ROLES = [
    "sequence-claim-manifest",
    "sequence-proof-certificates",
    "sequence-language",
    "sequence-claim-validator",
    "sequence-witness",
    "sequence-trace",
    "sequence-svg",
    "chain-bundle",
    "source-status",
    "source-status",
    "source-status",
    "source-status",
    "source-status",
]
VALIDATION_SUBJECTS = [
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
]
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
REPRODUCTION_COMMANDS = [
    {
        "label": "vertical-demo",
        "command": "python -m autarkic_systems.vertical_demo",
    },
    {
        "label": "sequence-demo-json",
        "command": "python -m autarkic_systems.network_sequence_demo --format json",
    },
    {
        "label": "project-status-summary",
        "command": "python -m autarkic_systems.project_status --format summary",
    },
    {
        "label": "handoff-refresh",
        "command": "python -m autarkic_systems.handoff --refresh-remotes",
    },
]
PROJECT_STATUS_FOR_DIGEST = {
    "accepted": True,
    "transition_evidence": {
        "bundle_count": 11,
        "path": TRANSITION_REGISTRY,
    },
    "chain_evidence": {
        "bundle_count": 2,
        "path": CHAIN_REGISTRY,
    },
    "sequence_evidence": {
        "bundle_count": 1,
        "path": SEQUENCE_REGISTRY,
        "bundles": [
            {
                "bundle_id": "post-handoff-signal-sequence-evidence-bundle",
                "path": SEQUENCE_BUNDLE,
                "sequence_claim_id": "UC-SEQUENCE-POST-HANDOFF-SIGNAL-ROUTED",
                "expected_status": "post-handoff-signal-routed",
            }
        ],
    },
    "transition_claims": {
        "claim_count": 16,
        "matched_count": 40,
    },
    "chain_claims": {
        "claim_count": 2,
    },
    "sequence_claims": {
        "claim_count": 1,
    },
    "proof_rule_audit": {
        "combined": {
            "rule_counts": {
                "predicate-result": 52,
                "manifest-example": 0,
            }
        }
    },
    "frontier": {
        "blocked_commands": ["standard-signal"],
        "safe_next_slice": "",
    },
    "formal_confidence_validation": FORMAL_CONFIDENCE_VALIDATION_SUMMARY,
}
SEQUENCE_DEMO_FOR_DIGEST = {
    "accepted": True,
    "evidence_layers": [
        {
            "role": "sequence-claim-manifest",
            "path": "claims/network_sequence_claims.json",
            "exists": True,
        },
        {
            "role": "sequence-proof-certificates",
            "path": "claims/network_sequence_proof_certificates.json",
            "exists": True,
        },
    ],
    "missing_evidence_paths": [],
    "validation": {
        "results": [
            {"subject": "schema"},
            {"subject": "boundary"},
        ],
    },
}


class VerticalDemoDigestTests(unittest.TestCase):
    def test_digest_accepts_prebuilt_project_status_without_rebuilding(self):
        with (
            mock.patch(
                "autarkic_systems.vertical_demo.build_project_status_report",
                side_effect=AssertionError("project status should be reused"),
            ) as project_status_builder,
            mock.patch(
                "autarkic_systems.vertical_demo.build_network_sequence_demo_report",
                return_value=SEQUENCE_DEMO_FOR_DIGEST,
            ),
        ):
            digest = build_vertical_demo_digest(
                project_status=PROJECT_STATUS_FOR_DIGEST,
            )

        project_status_builder.assert_not_called()
        self.assertTrue(digest["accepted"])
        self.assertEqual(
            digest["evidence_counts"],
            {
                "transition_bundles": 11,
                "chain_bundles": 2,
                "sequence_bundles": 1,
            },
        )
        self.assertEqual(
            digest["claim_counts"],
            {
                "transition_claims": 16,
                "transition_matched_examples": 40,
                "chain_claims": 2,
                "sequence_claims": 1,
            },
        )
        self.assertEqual(
            digest["sequence_evidence_bundle"],
            PROJECT_STATUS_FOR_DIGEST["sequence_evidence"]["bundles"][0],
        )
        self.assertEqual(
            digest["registries"],
            {
                "transition": TRANSITION_REGISTRY,
                "chain": CHAIN_REGISTRY,
                "sequence": SEQUENCE_REGISTRY,
            },
        )
        self.assertEqual(
            digest["evidence_trail"],
            SEQUENCE_DEMO_FOR_DIGEST["evidence_layers"],
        )
        self.assertEqual(digest["validation_subjects"], ["schema", "boundary"])
        self.assertIn(
            "Autarkic Systems vertical demo: accepted",
            format_vertical_demo_digest(digest),
        )

    def test_digest_reuses_project_status_formal_confidence_validation_summary(self):
        with mock.patch(
            "autarkic_systems.vertical_demo.build_network_sequence_demo_report",
            return_value=SEQUENCE_DEMO_FOR_DIGEST,
        ):
            digest = build_vertical_demo_digest(
                project_status=PROJECT_STATUS_FOR_DIGEST,
            )

        self.assertEqual(
            digest["formal_confidence_validation"],
            FORMAL_CONFIDENCE_VALIDATION_SUMMARY,
        )

    def test_text_output_names_formal_confidence_validation_frontier(self):
        with mock.patch(
            "autarkic_systems.vertical_demo.build_network_sequence_demo_report",
            return_value=SEQUENCE_DEMO_FOR_DIGEST,
        ):
            digest = build_vertical_demo_digest(
                project_status=PROJECT_STATUS_FOR_DIGEST,
            )

        text = format_vertical_demo_digest(digest)
        self.assertIn(
            (
                "Formal confidence validation: 19 accepted, 0 failed; "
                "fixed_point_construction_frontier_status accepted"
            ),
            text,
        )

    def test_digest_derives_formal_confidence_validation_from_status_results(self):
        project_status = {
            **PROJECT_STATUS_FOR_DIGEST,
            "formal_confidence": {
                "results": [
                    {
                        "subject": FORMAL_CONFIDENCE_FRONTIER_SUBJECT,
                        "accepted": True,
                    },
                    {
                        "subject": (
                            "AS-FORMAL-CONFIDENCE-TARGET-001."
                            "substitution_graph_correctness_frontier_status"
                        ),
                        "accepted": True,
                    },
                    {
                        "subject": (
                            "AS-FORMAL-CONFIDENCE-TARGET-001."
                            "fixed_point_equation_lifting_frontier_status"
                        ),
                        "accepted": False,
                    },
                ],
            },
        }
        project_status.pop("formal_confidence_validation")

        with mock.patch(
            "autarkic_systems.vertical_demo.build_network_sequence_demo_report",
            return_value=SEQUENCE_DEMO_FOR_DIGEST,
        ):
            digest = build_vertical_demo_digest(project_status=project_status)

        self.assertEqual(
            digest["formal_confidence_validation"],
            {
                "accepted_validation_count": 2,
                "failed_validation_count": 1,
                "accepted_frontier_subjects": [
                    FORMAL_CONFIDENCE_FRONTIER_SUBJECT,
                ],
                "accepted_frontier_labels": [
                    "fixed_point_construction_frontier_status",
                ],
            },
        )

    def test_digest_summarizes_current_accepted_demonstration(self):
        digest = build_vertical_demo_digest()

        self.assertTrue(digest["accepted"])
        self.assertEqual(digest["demonstration"], DEMONSTRATION)
        self.assertEqual(
            digest["evidence_counts"],
            {
                "transition_bundles": 11,
                "chain_bundles": 2,
                "sequence_bundles": 1,
            },
        )
        self.assertEqual(
            digest["claim_counts"],
            {
                "transition_claims": 16,
                "transition_matched_examples": 40,
                "chain_claims": 2,
                "sequence_claims": 1,
            },
        )
        self.assertEqual(
            digest["proof_rules"],
            {
                "predicate-result": 52,
                "manifest-example": 0,
            },
        )
        self.assertEqual(digest["blocked_commands"], ["standard-signal"])
        self.assertEqual(digest["safe_next_slice"], "")
        self.assertEqual(
            digest["registries"],
            {
                "transition": TRANSITION_REGISTRY,
                "chain": CHAIN_REGISTRY,
                "sequence": SEQUENCE_REGISTRY,
            },
        )
        self.assertEqual(
            digest["sequence_evidence_bundle"],
            {
                "bundle_id": "post-handoff-signal-sequence-evidence-bundle",
                "path": SEQUENCE_BUNDLE,
                "sequence_claim_id": "UC-SEQUENCE-POST-HANDOFF-SIGNAL-ROUTED",
                "expected_status": "post-handoff-signal-routed",
            },
        )
        self.assertEqual(digest["missing_evidence_paths"], [])
        self.assertEqual(digest["validation_subjects"], VALIDATION_SUBJECTS)
        self.assertEqual(
            digest["formal_confidence_validation"],
            FORMAL_CONFIDENCE_VALIDATION_SUMMARY,
        )
        self.assertEqual(digest["reproduction_commands"], REPRODUCTION_COMMANDS)
        self.assertEqual(
            [layer["role"] for layer in digest["evidence_trail"]],
            EVIDENCE_TRAIL_ROLES,
        )
        self.assertTrue(all(layer["exists"] for layer in digest["evidence_trail"]))
        self.assertIn(
            {
                "role": "sequence-trace",
                "path": "schematics/sequences/post_handoff_signal_sequence_trace.json",
                "exists": True,
            },
            digest["evidence_trail"],
        )
        self.assertIn(
            {
                "role": "sequence-svg",
                "path": "schematics/sequences/post_handoff_signal_sequence_trace.svg",
                "exists": True,
            },
            digest["evidence_trail"],
        )

    def test_text_output_names_artifacts_and_closed_boundary(self):
        text = format_vertical_demo_digest(build_vertical_demo_digest())

        self.assertIn("Autarkic Systems vertical demo: accepted", text)
        self.assertIn(f"Current demonstration: {DEMONSTRATION}", text)
        self.assertIn(
            "Evidence: 11 transition bundles; 2 chain bundles; 1 sequence bundle",
            text,
        )
        self.assertIn("Proof rules: predicate-result=52, manifest-example=0", text)
        self.assertIn("Blocked command frontier: standard-signal", text)
        self.assertIn(
            (
                "Formal confidence validation: 19 accepted, 0 failed; "
                "fixed_point_construction_frontier_status accepted"
            ),
            text,
        )
        self.assertIn(f"Sequence evidence bundle: {SEQUENCE_BUNDLE}", text)
        self.assertIn(f"Transition registry: {TRANSITION_REGISTRY}", text)
        self.assertIn(f"Chain registry: {CHAIN_REGISTRY}", text)
        self.assertIn(f"Sequence registry: {SEQUENCE_REGISTRY}", text)
        self.assertIn("Missing evidence paths: none", text)
        self.assertIn("Evidence trail:", text)
        self.assertIn(
            "- sequence-trace: schematics/sequences/post_handoff_signal_sequence_trace.json",
            text,
        )
        self.assertIn(
            "- sequence-svg: schematics/sequences/post_handoff_signal_sequence_trace.svg",
            text,
        )
        self.assertIn(
            "- source-status: sources/standard_signal_command_semantics_status.json",
            text,
        )
        self.assertIn("Reproduce:", text)
        self.assertIn(
            "- vertical-demo: python -m autarkic_systems.vertical_demo",
            text,
        )
        self.assertIn(
            "- handoff-refresh: python -m autarkic_systems.handoff --refresh-remotes",
            text,
        )
        self.assertIn(
            "Boundary: no standard-signal command-token execution change "
            "without new source evidence",
            text,
        )

    def test_json_cli_emits_the_same_digest(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_vertical_demo_cli(["--format", "json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["demonstration"], DEMONSTRATION)
        self.assertEqual(payload["proof_rules"]["predicate-result"], 52)
        self.assertEqual(payload["sequence_evidence_bundle"]["path"], SEQUENCE_BUNDLE)
        self.assertEqual(payload["missing_evidence_paths"], [])
        self.assertEqual(payload["validation_subjects"], VALIDATION_SUBJECTS)
        self.assertEqual(
            payload["formal_confidence_validation"],
            FORMAL_CONFIDENCE_VALIDATION_SUMMARY,
        )
        self.assertEqual(payload["reproduction_commands"], REPRODUCTION_COMMANDS)
        self.assertEqual(
            payload["evidence_trail"][0]["path"],
            "claims/network_sequence_claims.json",
        )

    def test_module_execution_runs_json_digest(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.vertical_demo",
                "--format",
                "json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["demonstration"], DEMONSTRATION)
        self.assertEqual(
            payload["formal_confidence_validation"],
            FORMAL_CONFIDENCE_VALIDATION_SUMMARY,
        )


if __name__ == "__main__":
    unittest.main()
