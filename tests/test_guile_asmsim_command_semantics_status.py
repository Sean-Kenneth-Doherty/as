import json
import unittest
from pathlib import Path


STATUS = Path("sources/guile_asmsim_command_semantics_status.json")
STANDARD_SIGNAL_STATUS = Path("sources/standard_signal_command_semantics_status.json")
WRITE_BUFFER_STATUS = Path("sources/write_buffer_command_semantics_status.json")
STEM_STATUS = Path("sources/stem_command_execution_source_status.json")
GUILE_ASMSIM = Path("/home/sean/Projects/_upstream/prc/practice/legacy/guile-asmsim.scm")


class GuileAsmsimCommandSemanticsStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = json.loads(STATUS.read_text(encoding="utf-8"))
        self.source = GUILE_ASMSIM.read_text(encoding="utf-8")

    def test_status_records_source_only_blocking_decision(self):
        self.assertEqual(self.status["schema_version"], 1)
        self.assertEqual(
            self.status["decision"],
            "do-not-implement-command-semantics-from-guile-asmsim",
        )
        self.assertEqual(self.status["runtime_change"], "none-source-status-only")
        self.assertEqual(Path(self.status["local_witness"]), GUILE_ASMSIM)
        self.assertEqual(
            self.status["safe_next_slice"],
            "keep-command-execution-blocked-pending-source-resolution",
        )

    def test_special_message_set_is_init_family_only(self):
        special = self.status["special_message_status"]

        self.assertEqual(special["locus"], "lines 15-18")
        self.assertEqual(
            special["special_messages"],
            [
                "stem-init",
                "wire-r-init",
                "wire-l-init",
                "proc-r-init",
                "proc-l-init",
            ],
        )
        self.assertEqual(
            special["excluded_tokens"],
            ["standard-signal", "write-buf-zero", "write-buf-one"],
        )
        self.assertIn("(define special-messages", self.source)
        self.assertIn("'proc-l-init))", self.source)

    def test_write_buffer_evidence_is_numeric_not_named_commands(self):
        write_buffer = self.status["write_buffer_status"]

        self.assertEqual(write_buffer["write_buf_locus"], "lines 210-212")
        self.assertEqual(
            write_buffer["self_mailbox_numeric_append_locus"],
            "lines 259-265",
        )
        self.assertEqual(write_buffer["named_write_buffer_commands"], [])
        self.assertIn("binary 0/1 values", write_buffer["summary"])
        self.assertIn("(define (write-buf inp buf)", self.source)
        self.assertIn("(member sms (list 0 1))", self.source)

    def test_command_buffer_list_diverges_from_formal_named_commands(self):
        command_buffer = self.status["command_buffer_status"]

        self.assertEqual(command_buffer["locus"], "lines 213-234")
        self.assertEqual(
            command_buffer["command_list_expression"],
            "(append special-messages standard-signals)",
        )
        self.assertIn("index-shape ambiguity", command_buffer["as_interpretation"])
        self.assertIn("(append special-messages standard-signals)", self.source)

    def test_existing_command_statuses_reference_guile_asmsim_evidence(self):
        standard = json.loads(STANDARD_SIGNAL_STATUS.read_text(encoding="utf-8"))
        write_buffer = json.loads(WRITE_BUFFER_STATUS.read_text(encoding="utf-8"))
        stem = json.loads(STEM_STATUS.read_text(encoding="utf-8"))

        self.assertEqual(
            standard["additional_source_statuses"][0]["path"],
            "sources/guile_asmsim_command_semantics_status.json",
        )
        self.assertEqual(
            write_buffer["additional_source_statuses"][0]["path"],
            "sources/guile_asmsim_command_semantics_status.json",
        )
        self.assertTrue(
            any(
                divergence["witness_id"] == "LEGACY-GUILE-ASMSIM-COMMAND-LIST"
                for divergence in stem["legacy_divergences"]
            )
        )


if __name__ == "__main__":
    unittest.main()
