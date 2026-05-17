import json
import unittest
from pathlib import Path


STATUS = Path("sources/recipient_non_init_command_source_status.json")
RECIPIENT_STATUS = Path("sources/recipient_command_consumption_source_status.json")
STEM_STATUS = Path("sources/stem_command_execution_source_status.json")
FORMAL_MODEL = Path("/home/sean/Projects/_upstream/prc/theory/official/formal-model.txt")
LEGACY_RAA = Path("/home/sean/Projects/_upstream/prc/practice/legacy/raa.scm")
LEGACY_SEMSIM = Path("/home/sean/Projects/_upstream/prc/practice/legacy/semsim.scm")
LEGACY_FSMSIM = Path("/home/sean/Projects/_upstream/prc/practice/legacy/fsmsim.scm")


class RecipientNonInitCommandSourceStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = json.loads(STATUS.read_text(encoding="utf-8"))

    def test_decision_blocks_runtime_execution_and_selects_rejection_claim(self):
        self.assertEqual(self.status["schema_version"], 1)
        self.assertEqual(
            self.status["decision"],
            "do-not-implement-recipient-non-init-command-messages-yet",
        )
        self.assertEqual(self.status["runtime_change"], "none-source-status-only")
        self.assertEqual(
            self.status["safe_next_slice"],
            "resolve-standard-signal-command-message-divergence",
        )
        claim = self.status["implemented_claims"][0]
        self.assertEqual(
            claim["claim_id"],
            "UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED",
        )
        self.assertEqual(
            claim["predicate"],
            "recipient_non_init_command_message_rejected",
        )
        trace = self.status["implemented_traces"][0]
        self.assertEqual(trace["adr"], "ADR-0055")
        self.assertEqual(
            trace["artifact_id"],
            "recipient-non-init-command-rejection-schematic-and-uc-transition-trace",
        )
        self.assertEqual(
            trace["path"],
            "schematics/recipient_non_init_command_rejection_trace.json",
        )
        svg = self.status["implemented_svgs"][0]
        self.assertEqual(svg["adr"], "ADR-0056")
        self.assertEqual(
            svg["path"],
            "schematics/recipient_non_init_command_rejection_trace.svg",
        )
        source_status = self.status["implemented_source_statuses"][0]
        self.assertEqual(source_status["adr"], "ADR-0057")
        self.assertEqual(
            source_status["path"],
            "sources/write_buffer_command_semantics_status.json",
        )

        blocked = self.status["blocked_runtime_commands"]
        self.assertEqual(
            blocked,
            ["standard-signal", "write-buf-zero", "write-buf-one"],
        )

    def test_standard_signal_divergence_is_recorded(self):
        standard = self.status["standard_signal_status"]

        self.assertEqual(Path(standard["formal_command_table"]["local_witness"]), FORMAL_MODEL)
        self.assertEqual(
            standard["formal_command_table"]["command"],
            "standard-signal",
        )
        self.assertEqual(
            {Path(path) for path in standard["legacy_special_message_exclusion"]["local_witnesses"]},
            {LEGACY_SEMSIM, LEGACY_FSMSIM},
        )
        self.assertNotIn(
            "standard-signal",
            standard["legacy_special_message_exclusion"]["special_messages"],
        )
        self.assertEqual(standard["decision"], "blocked")

    def test_write_buffer_divergences_are_recorded(self):
        divergences = {
            divergence["witness_id"]: divergence
            for divergence in self.status["write_buffer_status"]["legacy_divergences"]
        }

        self.assertEqual(Path(divergences["LEGACY-RAA-WRITE-BUFFER"]["local_witness"]), LEGACY_RAA)
        self.assertIn("buffer-full", divergences["LEGACY-RAA-WRITE-BUFFER"]["summary"])
        self.assertEqual(Path(divergences["LEGACY-SEMSIM-WRITE-BUFFER"]["local_witness"]), LEGACY_SEMSIM)
        self.assertIn("zero-buf", divergences["LEGACY-SEMSIM-WRITE-BUFFER"]["summary"])
        self.assertEqual(Path(divergences["LEGACY-FSMSIM-WRITE-BUFFER"]["local_witness"]), LEGACY_FSMSIM)
        self.assertIn("append", divergences["LEGACY-FSMSIM-WRITE-BUFFER"]["summary"])
        self.assertEqual(
            self.status["write_buffer_status"]["decision"],
            "blocked-by-source-divergence",
        )
        self.assertEqual(
            self.status["write_buffer_status"]["depends_on"],
            "sources/write_buffer_command_semantics_status.json",
        )

    def test_multi_command_policy_remains_blocked(self):
        policy = self.status["multi_command_input_status"]

        self.assertEqual(policy["decision"], "blocked")
        self.assertIn("single command-message", policy["as_boundary"])
        self.assertIn("multiple simultaneous", policy["summary"])

    def test_frontier_moves_from_rejection_evidence_to_source_resolution(self):
        recipient_status = json.loads(RECIPIENT_STATUS.read_text(encoding="utf-8"))
        stem_status = json.loads(STEM_STATUS.read_text(encoding="utf-8"))

        self.assertTrue(
            any(
                "write-buffer" in item
                for item in recipient_status["allowed_next_slices"]
            )
        )
        self.assertTrue(
            any(
                "standard-signal" in item
                for item in recipient_status["allowed_next_slices"]
            )
        )
        self.assertTrue(
            any(
                "standard-signal semantics" in item
                for item in stem_status["allowed_next_slices"]
            )
        )
        self.assertFalse(
            any(
                "write-buffer semantics before executing" in item
                for item in stem_status["allowed_next_slices"]
            )
        )
        self.assertFalse(
            any(
                "rejection trace" in item
                for item in recipient_status["allowed_next_slices"]
            )
        )
        self.assertFalse(
            any(
                "execute non-init recipient commands" in item
                for item in stem_status["allowed_next_slices"]
            )
        )


if __name__ == "__main__":
    unittest.main()
