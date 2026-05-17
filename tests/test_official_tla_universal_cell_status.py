import json
import unittest
from pathlib import Path


STATUS = Path("sources/official_tla_universal_cell_status.json")
STANDARD_SIGNAL_STATUS = Path("sources/standard_signal_command_semantics_status.json")
WRITE_BUFFER_STATUS = Path("sources/write_buffer_command_semantics_status.json")
STEM_STATUS = Path("sources/stem_command_execution_source_status.json")
OFFICIAL = Path("/home/sean/Projects/_upstream/prc/theory/official")
UNIVERSAL_CELL = OFFICIAL / "universal-cell.tla"
UNIVERSALCELL = OFFICIAL / "universalcell.tla"
UC = OFFICIAL / "uc.tla"


class OfficialTlaUniversalCellStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = json.loads(STATUS.read_text(encoding="utf-8"))
        self.universal_cell = UNIVERSAL_CELL.read_text(encoding="utf-8")
        self.universalcell = UNIVERSALCELL.read_text(encoding="utf-8")
        self.uc = UC.read_text(encoding="utf-8")

    def test_status_records_source_only_blocking_decision(self):
        self.assertEqual(self.status["schema_version"], 1)
        self.assertEqual(
            self.status["decision"],
            "do-not-use-official-tla-as-executable-uc-spec",
        )
        self.assertEqual(self.status["runtime_change"], "none-source-status-only")
        self.assertEqual(
            self.status["safe_next_slice"],
            "keep-command-execution-blocked-pending-complete-specification",
        )

    def test_tla_witnesses_are_recorded_with_line_counts(self):
        witnesses = {
            Path(witness["local_witness"]).name: witness
            for witness in self.status["tla_witnesses"]
        }

        self.assertEqual(witnesses["universal-cell.tla"]["line_count"], 45)
        self.assertEqual(witnesses["universalcell.tla"]["line_count"], 1)
        self.assertEqual(witnesses["uc.tla"]["line_count"], 0)
        self.assertEqual(witnesses["universalcell.tla"]["status"], "stub")
        self.assertEqual(witnesses["uc.tla"]["status"], "empty")

    def test_universal_cell_tla_is_partial_activation_skeleton(self):
        partial = self.status["universal_cell_status"]

        self.assertEqual(Path(partial["local_witness"]), UNIVERSAL_CELL)
        self.assertEqual(partial["status"], "partial-incomplete")
        self.assertEqual(partial["module_locus"], "lines 4-12")
        self.assertEqual(partial["init_locus"], "lines 14-22")
        self.assertEqual(partial["activate_locus"], "lines 24-33")
        self.assertEqual(partial["incomplete_wire_locus"], "lines 37-41")
        self.assertIn("MODULE Universal-Cell", self.universal_cell)
        self.assertIn("Init ==", self.universal_cell)
        self.assertIn("Activate ==", self.universal_cell)
        self.assertIn("\\/ /\\ u", self.universal_cell)

    def test_tla_files_do_not_resolve_command_semantics(self):
        command = self.status["command_semantics_status"]

        self.assertEqual(command["decision"], "absent")
        self.assertEqual(
            command["missing_terms"],
            [
                "Next",
                "process-buffer",
                "command-buffer",
                "standard-signal",
                "write-buf-zero",
                "write-buf-one",
            ],
        )
        joined = "\n".join((self.universal_cell, self.universalcell, self.uc))
        for term in command["missing_terms"]:
            with self.subTest(term=term):
                self.assertNotIn(term, joined)

    def test_existing_command_statuses_reference_tla_evidence(self):
        standard = json.loads(STANDARD_SIGNAL_STATUS.read_text(encoding="utf-8"))
        write_buffer = json.loads(WRITE_BUFFER_STATUS.read_text(encoding="utf-8"))
        stem = json.loads(STEM_STATUS.read_text(encoding="utf-8"))

        self.assertTrue(
            any(
                item["path"] == "sources/official_tla_universal_cell_status.json"
                for item in standard["additional_source_statuses"]
            )
        )
        self.assertTrue(
            any(
                item["path"] == "sources/official_tla_universal_cell_status.json"
                for item in write_buffer["additional_source_statuses"]
            )
        )
        self.assertTrue(
            any(
                divergence["witness_id"] == "PRC-OFFICIAL-TLA-INCOMPLETE"
                for divergence in stem["legacy_divergences"]
            )
        )


if __name__ == "__main__":
    unittest.main()
