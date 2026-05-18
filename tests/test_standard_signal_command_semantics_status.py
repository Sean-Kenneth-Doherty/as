import json
import unittest
from pathlib import Path


STATUS = Path("sources/standard_signal_command_semantics_status.json")
COMMAND_MAP = Path("sources/stem_command_buffer_map.json")
RECIPIENT_NON_INIT = Path("sources/recipient_non_init_command_source_status.json")
RECIPIENT_STATUS = Path("sources/recipient_command_consumption_source_status.json")
STEM_STATUS = Path("sources/stem_command_execution_source_status.json")
FORMAL_MODEL = Path("/home/sean/Projects/_upstream/prc/theory/official/formal-model.txt")
LEGACY_RAA = Path("/home/sean/Projects/_upstream/prc/practice/legacy/raa.scm")
LEGACY_SEMSIM = Path("/home/sean/Projects/_upstream/prc/practice/legacy/semsim.scm")
LEGACY_FSMSIM = Path("/home/sean/Projects/_upstream/prc/practice/legacy/fsmsim.scm")


class StandardSignalCommandSemanticsStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = json.loads(STATUS.read_text(encoding="utf-8"))

    def test_decision_blocks_standard_signal_command_token_execution(self):
        self.assertEqual(self.status["schema_version"], 1)
        self.assertEqual(
            self.status["decision"],
            "do-not-implement-standard-signal-command-execution-yet",
        )
        self.assertEqual(self.status["runtime_change"], "none-source-status-only")
        self.assertEqual(
            self.status["safe_next_slice"],
            "revisit-standard-signal-or-write-buffer-command-semantics",
        )
        self.assertEqual(
            self.status["blocked_runtime_surfaces"],
            [
                "self-mailbox-command",
                "self-target-command-buffer",
            ],
        )

    def test_formal_model_distinguishes_binary_standard_from_command_token(self):
        formal = self.status["formal_model_status"]

        self.assertEqual(Path(formal["local_witness"]), FORMAL_MODEL)
        self.assertEqual(formal["decision"], "insufficient")
        self.assertIn("lines 420-427", formal["ordinary_standard_signal_locus"])
        self.assertIn("lines 437-454", formal["command_table_locus"])
        self.assertIn("lines 593-657", formal["standard_process_locus"])
        self.assertEqual(formal["command_table_offset"], 0)
        self.assertIn("binary-input behavior", formal["gap"])

    def test_formal_model_self_mailbox_exception_is_recorded(self):
        exception = self.status["formal_model_self_mailbox_exception"]
        formal_text = FORMAL_MODEL.read_text(encoding="utf-8")

        self.assertEqual(Path(exception["local_witness"]), FORMAL_MODEL)
        self.assertIn("lines 207-218", exception["locus"])
        self.assertIn("self-mailbox of a stem cell", formal_text)
        self.assertEqual(
            exception["narrowed_question"],
            "self-target-surface",
        )
        self.assertEqual(
            exception["decision"],
            "do-not-treat-self-mailbox-standard-signal-as-binary-input",
        )
        self.assertIn("self-mailbox", exception["summary"])
        self.assertIn("ordinary binary-input", exception["summary"])

    def test_command_table_offset_is_resolved_to_formal_map(self):
        resolved = {
            question["question_id"]: question
            for question in self.status["resolved_resolution_questions"]
        }
        command_map = json.loads(COMMAND_MAP.read_text(encoding="utf-8"))

        self.assertIn("command-table-offset", resolved)
        offset = resolved["command-table-offset"]
        self.assertEqual(
            offset["decision"],
            "preserve-formal-command-offset-0",
        )
        self.assertEqual(offset["source_status"], str(COMMAND_MAP))
        self.assertEqual(offset["formal_command_offset"], 0)
        self.assertEqual(command_map["commands"][0]["offset"], 0)
        self.assertEqual(command_map["commands"][0]["command_id"], "standard-signal")
        self.assertIn("RAA", offset["legacy_divergence"])

    def test_self_mailbox_binary_input_equivalence_is_resolved(self):
        resolved = {
            question["question_id"]: question
            for question in self.status["resolved_resolution_questions"]
        }

        self_mailbox = resolved[
            "self-mailbox-standard-signal-binary-input-equivalence"
        ]
        self.assertEqual(
            self_mailbox["decision"],
            "do-not-treat-self-mailbox-standard-signal-as-binary-input",
        )
        self.assertEqual(self_mailbox["source_status"], str(STATUS))
        self.assertIn("self-mailbox of a stem cell", self_mailbox["legacy_divergence"])
        self.assertIn(
            "command-token execution rule",
            self_mailbox["legacy_divergence"],
        )

    def test_recipient_surface_is_resolved_to_existing_rejection_boundary(self):
        resolved = {
            question["question_id"]: question
            for question in self.status["resolved_resolution_questions"]
        }
        recipient_non_init = json.loads(
            RECIPIENT_NON_INIT.read_text(encoding="utf-8")
        )

        recipient_surface = resolved["recipient-surface"]
        self.assertEqual(
            recipient_surface["decision"],
            "reject-recipient-standard-signal-command-message-as-non-init",
        )
        self.assertEqual(recipient_surface["source_status"], str(RECIPIENT_NON_INIT))
        self.assertIn(
            "UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED",
            recipient_surface["legacy_divergence"],
        )
        self.assertEqual(
            recipient_non_init["implemented_evidence_bundles"][0]["path"],
            "evidence/recipient_non_init_command_rejection_bundle.json",
        )

    def test_command_token_binary_input_equivalence_is_resolved(self):
        resolved = {
            question["question_id"]: question
            for question in self.status["resolved_resolution_questions"]
        }

        binary_input = resolved["command-token-vs-binary-input"]
        self.assertEqual(
            binary_input["decision"],
            "do-not-replay-ordinary-binary-input-standard-signal",
        )
        self.assertEqual(binary_input["source_status"], str(STATUS))
        self.assertIn(
            "separately names ordinary standard-signal processing",
            binary_input["legacy_divergence"],
        )
        self.assertIn(
            "exclude standard-signal from special-message dispatch",
            binary_input["legacy_divergence"],
        )

    def test_legacy_witnesses_exclude_standard_signal_from_special_messages(self):
        witnesses = {
            witness["witness_id"]: witness
            for witness in self.status["legacy_standard_signal_witnesses"]
        }

        raa = witnesses["LEGACY-RAA-STANDARD-SIGNAL"]
        self.assertEqual(Path(raa["local_witness"]), LEGACY_RAA)
        self.assertEqual(raa["special_message_membership"], "excluded")
        self.assertEqual(raa["command_buffer_offset"], 7)
        self.assertIn("lines 213-221", raa["command_buffer_locus"])

        semsim = witnesses["LEGACY-SEMSIM-STANDARD-SIGNAL"]
        self.assertEqual(Path(semsim["local_witness"]), LEGACY_SEMSIM)
        self.assertEqual(semsim["special_message_membership"], "excluded")
        self.assertIn("lines 86-90", semsim["special_message_locus"])

        fsmsim = witnesses["LEGACY-FSMSIM-STANDARD-SIGNAL"]
        self.assertEqual(Path(fsmsim["local_witness"]), LEGACY_FSMSIM)
        self.assertEqual(fsmsim["special_message_membership"], "excluded")
        self.assertIn("lines 12-14", fsmsim["special_message_locus"])
        self.assertIn("lines 84-88", fsmsim["ordinary_standard_signal_locus"])

    def test_required_resolution_questions_are_explicit(self):
        question_ids = {
            question["question_id"]
            for question in self.status["required_resolution_questions"]
        }

        self.assertEqual(
            question_ids,
            {
                "self-target-surface",
            },
        )

    def test_existing_source_status_frontiers_point_to_multi_command_trace(self):
        recipient_non_init = json.loads(RECIPIENT_NON_INIT.read_text(encoding="utf-8"))
        recipient_status = json.loads(RECIPIENT_STATUS.read_text(encoding="utf-8"))
        stem_status = json.loads(STEM_STATUS.read_text(encoding="utf-8"))

        implemented = {
            item["adr"]: item
            for item in recipient_non_init["implemented_source_statuses"]
        }
        self.assertEqual(
            implemented["ADR-0058"]["path"],
            "sources/standard_signal_command_semantics_status.json",
        )
        self.assertEqual(
            recipient_non_init["safe_next_slice"],
            "revisit-standard-signal-or-write-buffer-command-semantics",
        )
        self.assertFalse(
            any(
                "multiple command-message" in item
                for item in recipient_status["allowed_next_slices"]
            )
        )
        self.assertFalse(
            any(
                "rendered SVG" in item
                for item in recipient_status["allowed_next_slices"]
            )
        )
        self.assertFalse(
            any(
                item.startswith("Resolve standard-signal")
                for item in recipient_status["allowed_next_slices"]
            )
        )
        self.assertFalse(
            any(
                "standard-signal semantics before executing" in item
                for item in stem_status["allowed_next_slices"]
            )
        )


if __name__ == "__main__":
    unittest.main()
