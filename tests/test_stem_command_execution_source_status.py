import json
import unittest
from pathlib import Path


STATUS = Path("sources/stem_command_execution_source_status.json")
FORMAL_MODEL = Path("/home/sean/Projects/_upstream/prc/theory/official/formal-model.txt")
LEGACY_RAA = Path("/home/sean/Projects/_upstream/prc/practice/legacy/raa.scm")
LEGACY_SEMSIM = Path("/home/sean/Projects/_upstream/prc/practice/legacy/semsim.scm")
LEGACY_FSMSIM = Path("/home/sean/Projects/_upstream/prc/practice/legacy/fsmsim.scm")


class StemCommandExecutionSourceStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = json.loads(STATUS.read_text(encoding="utf-8"))

    def test_full_execution_is_blocked_after_narrow_self_init_dispatch(self):
        self.assertEqual(self.status["schema_version"], 1)
        self.assertEqual(
            self.status["decision"],
            "do-not-implement-full-stem-command-execution-yet",
        )
        self.assertEqual(
            self.status["map_dependency"],
            "sources/stem_command_buffer_map.json",
        )

        blocker_ids = {blocker["blocker_id"] for blocker in self.status["blockers"]}
        self.assertIn("recipient-non-init-command-message-semantics", blocker_ids)
        self.assertIn("standard-signal-command-semantics", blocker_ids)
        self.assertIn("write-buffer-command-semantics", blocker_ids)

        execution_gap = self.status["formal_model_execution_anchor"]["as_gap"]
        self.assertIn("self-target init command-buffer dispatch", execution_gap)
        self.assertIn("neighbor-target command-buffer delivery", execution_gap)
        self.assertIn("recipient-side init-family command-message input consumption", execution_gap)
        self.assertIn("unsupported self-target non-init append boundary", execution_gap)
        self.assertIn("does not execute non-init command-message inputs", execution_gap)

    def test_formal_model_command_table_matches_adr_0026_map(self):
        formal = self.status["formal_model_command_table"]

        self.assertEqual(Path(formal["local_witness"]), FORMAL_MODEL)
        self.assertEqual(
            formal["target_order"],
            ["self", "neighbor-a", "neighbor-b", "neighbor-c"],
        )
        self.assertEqual(
            formal["command_order"],
            [
                "standard-signal",
                "stem-init",
                "wire-r-init",
                "wire-l-init",
                "proc-r-init",
                "proc-l-init",
                "write-buf-zero",
                "write-buf-one",
            ],
        )

    def test_legacy_command_and_target_divergences_are_recorded(self):
        divergences = {
            divergence["witness_id"]: divergence
            for divergence in self.status["legacy_divergences"]
        }

        raa = divergences["LEGACY-RAA-BUFFER-PROCESS"]
        self.assertEqual(Path(raa["local_witness"]), LEGACY_RAA)
        self.assertEqual(raa["target_00_interpretation"], "neighbor-a-output")
        self.assertEqual(raa["command_000_interpretation"], "stem-init")
        self.assertEqual(raa["command_111_interpretation"], "standard-signal")

        special_messages = divergences["LEGACY-SEMSIM-FSMSIM-SPECIAL-MESSAGES"]
        self.assertEqual(
            {Path(path) for path in special_messages["local_witnesses"]},
            {LEGACY_SEMSIM, LEGACY_FSMSIM},
        )
        self.assertEqual(
            special_messages["special_messages"],
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
        self.assertNotIn("standard-signal", special_messages["special_messages"])

    def test_allowed_next_slices_are_narrower_than_full_execution(self):
        allowed = self.status["allowed_next_slices"]

        self.assertTrue(allowed)
        self.assertTrue(
            any(
                "recipient-side standard-signal and write-buffer" in item
                for item in allowed
            )
        )
        self.assertTrue(any("write-buffer semantics" in item for item in allowed))
        self.assertTrue(
            all("full stem command execution" not in item for item in allowed)
        )


if __name__ == "__main__":
    unittest.main()
