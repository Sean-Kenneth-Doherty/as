import contextlib
import io
import json
import subprocess
import sys
import unittest

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


class VerticalDemoDigestTests(unittest.TestCase):
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
        self.assertIn(f"Sequence evidence bundle: {SEQUENCE_BUNDLE}", text)
        self.assertIn(f"Transition registry: {TRANSITION_REGISTRY}", text)
        self.assertIn(f"Chain registry: {CHAIN_REGISTRY}", text)
        self.assertIn(f"Sequence registry: {SEQUENCE_REGISTRY}", text)
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


if __name__ == "__main__":
    unittest.main()
