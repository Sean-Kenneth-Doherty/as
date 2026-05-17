import json
import unittest
from pathlib import Path


STATUS = Path("sources/recipient_command_consumption_source_status.json")
STEM_STATUS = Path("sources/stem_command_execution_source_status.json")
FORMAL_MODEL = Path("/home/sean/Projects/_upstream/prc/theory/official/formal-model.txt")
LEGACY_RAA = Path("/home/sean/Projects/_upstream/prc/practice/legacy/raa.scm")
LEGACY_SEMSIM = Path("/home/sean/Projects/_upstream/prc/practice/legacy/semsim.scm")
LEGACY_FSMSIM = Path("/home/sean/Projects/_upstream/prc/practice/legacy/fsmsim.scm")


class RecipientCommandConsumptionSourceStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = json.loads(STATUS.read_text(encoding="utf-8"))

    def test_decision_blocks_full_consumption_but_allows_init_family_slice(self):
        self.assertEqual(self.status["schema_version"], 1)
        self.assertEqual(
            self.status["decision"],
            "implement-recipient-init-family-command-message-consumption-next",
        )
        self.assertEqual(
            self.status["runtime_change"],
            "none-source-status-only",
        )
        self.assertTrue(self.status["allowed_next_slice"]["recipient_init_family"])
        self.assertFalse(self.status["allowed_next_slice"]["standard_signal"])
        self.assertFalse(self.status["allowed_next_slice"]["write_buffer"])

        implemented = self.status["implemented_slices"][0]
        self.assertEqual(implemented["adr"], "ADR-0049")
        self.assertEqual(
            implemented["status"],
            "recipient-init-command-message-processed",
        )
        self.assertEqual(
            implemented["commands"],
            [
                "stem-init",
                "wire-r-init",
                "wire-l-init",
                "proc-r-init",
                "proc-l-init",
            ],
        )

        claim = self.status["implemented_claims"][0]
        self.assertEqual(
            claim["claim_id"],
            "UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED",
        )
        self.assertEqual(
            claim["predicate"],
            "recipient_init_command_message_processed",
        )

        trace = self.status["implemented_traces"][0]
        self.assertEqual(
            trace["artifact_id"],
            "recipient-init-command-message-schematic-and-uc-transition-trace",
        )
        self.assertEqual(
            trace["path"],
            "schematics/recipient_init_command_message_trace.json",
        )

        svg = self.status["implemented_svgs"][0]
        self.assertEqual(svg["adr"], "ADR-0052")
        self.assertEqual(
            svg["path"],
            "schematics/recipient_init_command_message_trace.svg",
        )

    def test_formal_model_records_input_special_message_processing(self):
        formal = self.status["formal_model_input_special_message_anchor"]

        self.assertEqual(Path(formal["local_witness"]), FORMAL_MODEL)
        self.assertEqual(formal["locus"], "lines 604-613")
        self.assertEqual(
            formal["covered_roles"],
            ["wire", "proc", "stem"],
        )
        self.assertIn(
            "input-channel special messages",
            formal["summary"],
        )

    def test_legacy_sources_agree_on_special_message_set_without_standard_signal(self):
        legacy = {
            witness["witness_id"]: witness
            for witness in self.status["legacy_special_message_witnesses"]
        }

        self.assertEqual(Path(legacy["LEGACY-RAA-SPECIAL-MESSAGES"]["local_witness"]), LEGACY_RAA)
        self.assertEqual(Path(legacy["LEGACY-SEMSIM-SPECIAL-MESSAGES"]["local_witness"]), LEGACY_SEMSIM)
        self.assertEqual(Path(legacy["LEGACY-FSMSIM-SPECIAL-MESSAGES"]["local_witness"]), LEGACY_FSMSIM)
        for witness in legacy.values():
            self.assertEqual(
                witness["special_messages"],
                [
                    "stem-init",
                    "wire-r-init",
                    "wire-l-init",
                    "proc-r-init",
                    "proc-l-init",
                    "write-buf-zero",
                    "write-buf-one",
                ],
            )
            self.assertNotIn("standard-signal", witness["special_messages"])

    def test_blockers_keep_unresolved_consumption_out_of_next_slice(self):
        blocker_ids = {blocker["blocker_id"] for blocker in self.status["blockers"]}

        self.assertIn("standard-signal-command-message-divergence", blocker_ids)
        self.assertIn("write-buffer-command-message-semantics", blocker_ids)
        self.assertIn("multi-command-input-conflict-policy", blocker_ids)

        implemented_statuses = {
            item["adr"]: item for item in self.status["implemented_source_statuses"]
        }
        self.assertEqual(
            implemented_statuses["ADR-0057"]["path"],
            "sources/write_buffer_command_semantics_status.json",
        )

    def test_stem_status_points_to_recipient_init_consumption_next(self):
        stem_status = json.loads(STEM_STATUS.read_text(encoding="utf-8"))
        allowed = stem_status["allowed_next_slices"]

        self.assertTrue(any("standard-signal" in item for item in allowed))
        self.assertFalse(
            any(
                item.startswith("Resolve write-buffer")
                for item in allowed
            )
        )
        self.assertFalse(
            any(
                "execute non-init recipient commands" in item
                for item in allowed
            )
        )


if __name__ == "__main__":
    unittest.main()
