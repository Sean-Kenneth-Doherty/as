import json
import unittest
from pathlib import Path


STATUS = Path("sources/write_buffer_command_semantics_status.json")
RECIPIENT_NON_INIT = Path("sources/recipient_non_init_command_source_status.json")
RECIPIENT_STATUS = Path("sources/recipient_command_consumption_source_status.json")
STEM_STATUS = Path("sources/stem_command_execution_source_status.json")
FORMAL_MODEL = Path("/home/sean/Projects/_upstream/prc/theory/official/formal-model.txt")
LEGACY_RAA = Path("/home/sean/Projects/_upstream/prc/practice/legacy/raa.scm")
LEGACY_SEMSIM = Path("/home/sean/Projects/_upstream/prc/practice/legacy/semsim.scm")
LEGACY_FSMSIM = Path("/home/sean/Projects/_upstream/prc/practice/legacy/fsmsim.scm")


class WriteBufferCommandSemanticsStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = json.loads(STATUS.read_text(encoding="utf-8"))

    def test_decision_blocks_write_buffer_runtime_execution(self):
        self.assertEqual(self.status["schema_version"], 1)
        self.assertEqual(
            self.status["decision"],
            "do-not-implement-write-buffer-command-execution-yet",
        )
        self.assertEqual(self.status["runtime_change"], "none-source-status-only")
        self.assertEqual(
            self.status["safe_next_slice"],
            "resolve-standard-signal-command-message-divergence",
        )
        self.assertEqual(
            self.status["blocked_runtime_surfaces"],
            [
                "recipient-command-message",
                "self-mailbox-command",
                "self-target-command-buffer",
            ],
        )
        self.assertEqual(
            self.status["commands"],
            ["write-buf-zero", "write-buf-one"],
        )

    def test_formal_model_names_commands_but_not_write_buffer_primitive(self):
        formal = self.status["formal_model_status"]

        self.assertEqual(Path(formal["local_witness"]), FORMAL_MODEL)
        self.assertEqual(formal["decision"], "insufficient")
        self.assertIn("lines 437-454", formal["command_table_locus"])
        self.assertIn("lines 604-613", formal["input_special_message_locus"])
        self.assertIn("lines 674-681", formal["stem_self_mailbox_locus"])
        self.assertEqual(
            formal["named_commands"],
            ["write-buf-zero", "write-buf-one"],
        )
        self.assertIn("does not define", formal["gap"])

    def test_legacy_write_buffer_witnesses_record_incompatible_boundaries(self):
        witnesses = {
            witness["witness_id"]: witness
            for witness in self.status["legacy_write_buffer_witnesses"]
        }

        raa = witnesses["LEGACY-RAA-WRITE-BUFFER"]
        self.assertEqual(Path(raa["local_witness"]), LEGACY_RAA)
        self.assertEqual(raa["append_behavior"], "append-if-buffer-not-full")
        self.assertEqual(raa["buffer_full_guard"], "present")
        self.assertEqual(raa["post_append_buffer_clearing"], "none")
        self.assertIn("lines 280-282", raa["write_buffer_locus"])

        semsim = witnesses["LEGACY-SEMSIM-WRITE-BUFFER"]
        self.assertEqual(Path(semsim["local_witness"]), LEGACY_SEMSIM)
        self.assertEqual(semsim["append_behavior"], "append-then-stem-wrapper-clears-buffer")
        self.assertEqual(semsim["post_append_buffer_clearing"], "zero-buf")
        self.assertIn("lines 346-365", semsim["write_buffer_locus"])

        fsmsim = witnesses["LEGACY-FSMSIM-WRITE-BUFFER"]
        self.assertEqual(Path(fsmsim["local_witness"]), LEGACY_FSMSIM)
        self.assertEqual(fsmsim["append_behavior"], "append-and-clear-mail-input")
        self.assertEqual(fsmsim["buffer_full_guard"], "absent")
        self.assertIn("lines 262-267", fsmsim["write_buffer_locus"])

    def test_required_resolution_questions_are_explicit(self):
        question_ids = {
            question["question_id"]
            for question in self.status["required_resolution_questions"]
        }

        self.assertEqual(
            question_ids,
            {
                "recipient-vs-stem-surface",
                "buffer-full-boundary",
                "post-append-clearing",
                "standard-signal-interaction",
            },
        )

    def test_existing_source_status_frontiers_point_past_write_buffer(self):
        recipient_non_init = json.loads(RECIPIENT_NON_INIT.read_text(encoding="utf-8"))
        recipient_status = json.loads(RECIPIENT_STATUS.read_text(encoding="utf-8"))
        stem_status = json.loads(STEM_STATUS.read_text(encoding="utf-8"))

        implemented = recipient_non_init["implemented_source_statuses"][0]
        self.assertEqual(implemented["adr"], "ADR-0057")
        self.assertEqual(
            implemented["path"],
            "sources/write_buffer_command_semantics_status.json",
        )
        self.assertEqual(
            recipient_non_init["safe_next_slice"],
            "resolve-standard-signal-command-message-divergence",
        )
        self.assertTrue(
            any(
                "standard-signal" in item
                for item in recipient_status["allowed_next_slices"]
            )
        )
        self.assertFalse(
            any(
                item.startswith("Resolve write-buffer")
                for item in recipient_status["allowed_next_slices"]
            )
        )
        self.assertTrue(
            any(
                "standard-signal" in item
                for item in stem_status["allowed_next_slices"]
            )
        )
        self.assertFalse(
            any(
                "write-buffer semantics before executing" in item
                for item in stem_status["allowed_next_slices"]
            )
        )


if __name__ == "__main__":
    unittest.main()
