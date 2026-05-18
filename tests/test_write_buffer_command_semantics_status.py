import json
import unittest
from pathlib import Path


STATUS = Path("sources/write_buffer_command_semantics_status.json")
RECIPIENT_NON_INIT = Path("sources/recipient_non_init_command_source_status.json")
RECIPIENT_STATUS = Path("sources/recipient_command_consumption_source_status.json")
STEM_STATUS = Path("sources/stem_command_execution_source_status.json")
SELF_MAILBOX_UNSUPPORTED_BUNDLE = Path("evidence/self_mailbox_unsupported_bundle.json")
SELF_MAILBOX_WRITE_BUFFER_BUNDLE = Path("evidence/self_mailbox_write_buffer_bundle.json")
COMMAND_BUFFER_UNSUPPORTED_BUNDLE = Path(
    "evidence/command_buffer_unsupported_bundle.json"
)
SELF_COMMAND_BUFFER_WRITE_BUFFER_BUNDLE = Path(
    "evidence/self_command_buffer_write_buffer_bundle.json"
)
RECIPIENT_WRITE_BUFFER_BUNDLE = Path(
    "evidence/recipient_write_buffer_command_message_bundle.json"
)
FORMAL_MODEL = Path("/home/sean/Projects/_upstream/prc/theory/official/formal-model.txt")
LEGACY_RAA = Path("/home/sean/Projects/_upstream/prc/practice/legacy/raa.scm")
LEGACY_SEMSIM = Path("/home/sean/Projects/_upstream/prc/practice/legacy/semsim.scm")
LEGACY_FSMSIM = Path("/home/sean/Projects/_upstream/prc/practice/legacy/fsmsim.scm")


class WriteBufferCommandSemanticsStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = json.loads(STATUS.read_text(encoding="utf-8"))

    def test_decision_marks_write_buffer_runtime_execution_implemented(self):
        self.assertEqual(self.status["schema_version"], 1)
        self.assertEqual(
            self.status["decision"],
            "write-buffer-command-execution-implemented",
        )
        self.assertEqual(
            self.status["runtime_change"],
            "implemented-by-adr-0169",
        )
        self.assertEqual(
            self.status["safe_next_slice"],
            "no-write-buffer-follow-up-pending-after-recipient-evidence-bundle",
        )
        self.assertEqual(
            self.status["blocked_runtime_surfaces"],
            [],
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

    def test_command_bit_source_is_literal_zero_one(self):
        bit_source = self.status["command_bit_source"]

        self.assertEqual(
            bit_source["decision"],
            "write-buffer-command-bit-is-literal",
        )
        self.assertEqual(
            bit_source["commands"],
            {
                "write-buf-zero": 0,
                "write-buf-one": 1,
            },
        )
        self.assertIn("lines 437-454", bit_source["formal_model_locus"])
        self.assertIn("lines 264-273", bit_source["raa_locus"])
        self.assertIn("lines 346-365", bit_source["semsim_locus"])
        self.assertIn("lines 262-267", bit_source["fsmsim_locus"])
        self.assertIn("literal", bit_source["summary"])
        self.assertIn("high-rail", bit_source["summary"])

    def test_required_resolution_questions_are_resolved(self):
        question_ids = {
            question["question_id"]
            for question in self.status["required_resolution_questions"]
        }

        self.assertEqual(question_ids, set())
        self.assertEqual(self.status["required_resolution_questions"], [])
        self.assertEqual(self.status["resolution_question_evidence"], [])

    def test_recipient_surface_is_implemented_and_no_longer_runtime_blocked(self):
        resolved_questions = {
            question["question_id"]: question
            for question in self.status["resolved_resolution_questions"]
        }
        recipient_non_init = json.loads(
            RECIPIENT_NON_INIT.read_text(encoding="utf-8")
        )

        resolved = resolved_questions["recipient-surface"]
        self.assertEqual(
            resolved["decision"],
            "execute-recipient-write-buffer-command-message-append",
        )
        self.assertEqual(resolved["source_status"], str(STATUS))
        self.assertIn(
            "formal model",
            resolved["legacy_divergence"],
        )
        self.assertIn("RAA", resolved["legacy_divergence"])
        self.assertIn("FSMSIM", resolved["legacy_divergence"])
        self.assertIn("SEMSIM", resolved["legacy_divergence"])
        self.assertNotIn(
            "write-buf-zero",
            recipient_non_init["blocked_runtime_commands"],
        )
        self.assertNotIn(
            "write-buf-one",
            recipient_non_init["blocked_runtime_commands"],
        )
        surface = self.status["recipient_surface_resolution"]
        self.assertEqual(
            surface["decision"],
            "execute-recipient-write-buffer-command-message-append",
        )
        self.assertEqual(surface["source_status"], str(STATUS))
        self.assertEqual(
            surface["claim_id"],
            "UC-RECIPIENT-WRITE-BUFFER-COMMAND-MESSAGE-APPENDED",
        )
        self.assertEqual(
            surface["evidence_bundle_status"],
            "implemented",
        )
        self.assertEqual(
            surface["evidence_bundle"],
            str(RECIPIENT_WRITE_BUFFER_BUNDLE),
        )
        self.assertIn("implemented", surface["summary"])
        self.assertIn("evidence bundle", surface["summary"])

    def test_recipient_command_message_surface_question_is_resolved(self):
        resolved_questions = {
            question["question_id"]: question
            for question in self.status["resolved_resolution_questions"]
        }

        resolved = resolved_questions["recipient-command-message-surface"]
        self.assertEqual(
            resolved["decision"],
            "execute-recipient-write-buffer-command-message-append",
        )
        self.assertEqual(resolved["source_status"], str(STATUS))
        self.assertIn("formal model", resolved["legacy_divergence"])
        self.assertIn("RAA", resolved["legacy_divergence"])
        self.assertIn("FSMSIM", resolved["legacy_divergence"])
        self.assertIn("SEMSIM", resolved["legacy_divergence"])
        self.assertIn("ADR-0160", resolved["legacy_divergence"])

    def test_self_target_surface_is_resolved_to_execution_claims(self):
        resolved_questions = {
            question["question_id"]: question
            for question in self.status["resolved_resolution_questions"]
        }
        self_mailbox_bundle = json.loads(
            SELF_MAILBOX_UNSUPPORTED_BUNDLE.read_text(encoding="utf-8")
        )
        command_buffer_bundle = json.loads(
            COMMAND_BUFFER_UNSUPPORTED_BUNDLE.read_text(encoding="utf-8")
        )
        self_mailbox_write_bundle = json.loads(
            SELF_MAILBOX_WRITE_BUFFER_BUNDLE.read_text(encoding="utf-8")
        )
        command_buffer_write_bundle = json.loads(
            SELF_COMMAND_BUFFER_WRITE_BUFFER_BUNDLE.read_text(encoding="utf-8")
        )

        resolved = resolved_questions["self-target-surface"]
        self.assertEqual(
            resolved["decision"],
            "execute-self-target-write-buffer-append",
        )
        self.assertEqual(resolved["source_status"], str(STATUS))
        self.assertIn(
            "UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED",
            resolved["legacy_divergence"],
        )
        self.assertIn(
            "UC-STEM-COMMAND-BUFFER-SELF-WRITE-BUFFER-APPENDED",
            resolved["legacy_divergence"],
        )
        self.assertNotIn(
            "write buffer zero unsupported preserved",
            self_mailbox_bundle["covered_positive_examples"],
        )
        self.assertIn(
            "standard signal unsupported preserved",
            self_mailbox_bundle["covered_positive_examples"],
        )
        self.assertNotIn(
            "self write buffer zero command remains appended",
            command_buffer_bundle["covered_positive_examples"],
        )
        self.assertIn(
            "self standard signal command remains appended",
            command_buffer_bundle["covered_positive_examples"],
        )
        self.assertEqual(
            self_mailbox_write_bundle["claim_id"],
            "UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED",
        )
        self.assertEqual(
            command_buffer_write_bundle["claim_id"],
            "UC-STEM-COMMAND-BUFFER-SELF-WRITE-BUFFER-APPENDED",
        )
        self.assertIn(
            str(SELF_MAILBOX_WRITE_BUFFER_BUNDLE),
            self.status["self_target_surface_resolution"]["evidence_bundles"],
        )
        self.assertIn(
            str(SELF_COMMAND_BUFFER_WRITE_BUFFER_BUNDLE),
            self.status["self_target_surface_resolution"]["evidence_bundles"],
        )

    def test_standard_signal_interaction_is_resolved_as_literal_bits(self):
        resolved_questions = {
            question["question_id"]: question
            for question in self.status["resolved_resolution_questions"]
        }

        resolved = resolved_questions["standard-signal-interaction"]
        self.assertEqual(
            resolved["decision"],
            "write-buffer-command-bits-are-literal-not-high-rail-derived",
        )
        self.assertEqual(
            resolved["source_status"],
            "sources/write_buffer_command_semantics_status.json",
        )
        self.assertIn("literal 0 and 1 append bits", resolved["legacy_divergence"])
        self.assertIn("ADR-0161", resolved["legacy_divergence"])

    def test_buffer_full_boundary_resolution_records_source_basis(self):
        resolution = self.status["buffer_full_boundary_resolution"]

        self.assertEqual(
            resolution["decision"],
            "preserve-existing-full-buffer-boundary-before-write-buffer-append",
        )
        self.assertIn("lines 152-175", resolution["formal_model_locus"])
        self.assertIn("lines 204-205", resolution["raa_locus"])
        self.assertIn("lines 280-282", resolution["raa_locus"])
        self.assertIn("no contrary full-buffer policy", resolution["summary"])

    def test_buffer_full_boundary_is_resolved_as_preservation_boundary(self):
        resolved_questions = {
            question["question_id"]: question
            for question in self.status["resolved_resolution_questions"]
        }

        resolved = resolved_questions["buffer-full-boundary"]
        self.assertEqual(
            resolved["decision"],
            "preserve-existing-full-buffer-boundary-before-write-buffer-append",
        )
        self.assertEqual(
            resolved["source_status"],
            "sources/write_buffer_command_semantics_status.json",
        )
        self.assertIn("formal model gates writes", resolved["legacy_divergence"])
        self.assertIn("RAA", resolved["legacy_divergence"])
        self.assertIn("no contrary full-buffer policy", resolved["legacy_divergence"])

    def test_post_append_clearing_resolution_records_source_basis(self):
        resolution = self.status["post_append_clearing_resolution"]

        self.assertEqual(
            resolution["decision"],
            "preserve-appended-buffer-clear-command-source",
        )
        self.assertIn("lines 231-254", resolution["raa_locus"])
        self.assertIn("lines 262-267", resolution["fsmsim_locus"])
        self.assertIn("lines 353-365", resolution["semsim_locus"])
        self.assertIn("SEMSIM", resolution["legacy_divergence"])

    def test_post_append_clearing_is_resolved_as_buffer_preservation(self):
        resolved_questions = {
            question["question_id"]: question
            for question in self.status["resolved_resolution_questions"]
        }

        resolved = resolved_questions["post-append-clearing"]
        self.assertEqual(
            resolved["decision"],
            "preserve-appended-buffer-clear-command-source",
        )
        self.assertEqual(
            resolved["source_status"],
            "sources/write_buffer_command_semantics_status.json",
        )
        self.assertIn("RAA", resolved["legacy_divergence"])
        self.assertIn("FSMSIM", resolved["legacy_divergence"])
        self.assertIn("SEMSIM", resolved["legacy_divergence"])

    def test_execution_readiness_records_implemented_surfaces(self):
        readiness = self.status["execution_readiness"]

        self.assertEqual(
            readiness["decision"],
            "implemented",
        )
        self.assertFalse(readiness["execution_change_allowed"])
        self.assertEqual(
            readiness["blocked_by_resolution_questions"],
            [],
        )
        self.assertIn("implemented", readiness["summary"])
        self.assertIn("recipient command-message", readiness["summary"])

    def test_existing_source_status_frontiers_point_past_write_buffer(self):
        recipient_non_init = json.loads(RECIPIENT_NON_INIT.read_text(encoding="utf-8"))
        recipient_status = json.loads(RECIPIENT_STATUS.read_text(encoding="utf-8"))
        stem_status = json.loads(STEM_STATUS.read_text(encoding="utf-8"))

        implemented = {
            item["adr"]: item
            for item in recipient_non_init["implemented_source_statuses"]
        }
        self.assertEqual(
            implemented["ADR-0057"]["path"],
            "sources/write_buffer_command_semantics_status.json",
        )
        self.assertEqual(
            implemented["ADR-0058"]["path"],
            "sources/standard_signal_command_semantics_status.json",
        )
        self.assertEqual(
            recipient_non_init["safe_next_slice"],
            "no-standard-signal-command-token-execution-change-without-new-source-evidence",
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
                item.startswith("Resolve write-buffer")
                for item in recipient_status["allowed_next_slices"]
            )
        )
        self.assertFalse(
            any(
                item.startswith("Implement recipient write-buffer")
                for item in recipient_status["allowed_next_slices"]
            )
        )
        self.assertFalse(
            any(
                "standard-signal" in item
                for item in recipient_status["allowed_next_slices"]
            )
        )
        self.assertFalse(
            any(
                "recipient write-buffer command-message evidence bundle" in item
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
