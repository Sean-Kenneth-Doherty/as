import json
import unittest
from pathlib import Path

from autarkic_systems.claim_manifest import load_transition_claims
from autarkic_systems.transition_predicates import (
    recipient_non_init_command_message_rejected,
)
from autarkic_systems.universal_cell import Cell, step_fixed_cell, step_stem_cell


STATUS = Path("sources/multi_command_recipient_input_policy_status.json")
RECIPIENT_NON_INIT = Path("sources/recipient_non_init_command_source_status.json")
RECIPIENT_STATUS = Path("sources/recipient_command_consumption_source_status.json")
STEM_STATUS = Path("sources/stem_command_execution_source_status.json")
WRITE_BUFFER_STATUS = Path("sources/write_buffer_command_semantics_status.json")
STANDARD_SIGNAL_STATUS = Path("sources/standard_signal_command_semantics_status.json")
CLAIMS = Path("claims/transition_claims.json")
CLAIM_ID = "UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED"
EMPTY = ("_", "_", "_")
NO_STANDARD_SIGNAL_SAFE_NEXT = (
    "no-standard-signal-command-token-execution-change-without-new-source-evidence"
)


class MultiCommandRecipientInputPolicyStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = json.loads(STATUS.read_text(encoding="utf-8"))

    def test_decision_selects_reject_and_clear_policy(self):
        self.assertEqual(self.status["schema_version"], 1)
        self.assertEqual(
            self.status["decision"],
            "reject-multiple-recipient-command-message-inputs",
        )
        self.assertEqual(self.status["runtime_change"], "none-policy-status-only")
        self.assertEqual(self.status["accepted_command_message_count"], 1)
        self.assertEqual(self.status["conflict_command_message_count_minimum"], 2)
        self.assertEqual(
            self.status["policy"],
            "reject-and-clear-active-command-input",
        )
        self.assertEqual(
            self.status["safe_next_slice"],
            NO_STANDARD_SIGNAL_SAFE_NEXT,
        )
        self.assertEqual(
            self.status["covered_runtime_surfaces"],
            [
                "fixed-direct-input",
                "fixed-upstream-input",
                "stem-direct-input",
            ],
        )
        self.assertEqual(self.status["policy_effects"]["status"], "rejected-input")
        self.assertIn("role", self.status["policy_effects"]["preserves"])
        self.assertIn("active command input", self.status["policy_effects"]["clears"])

    def test_existing_runtime_matches_policy_without_behavior_change(self):
        cases = (
            (
                "fixed direct all-init conflict",
                Cell(role="wire", memory="right", input=("wire-r-init", "proc-l-init", "_")),
                step_fixed_cell,
            ),
            (
                "fixed upstream all-init conflict",
                Cell(role="proc", memory="left", upstream=("wire-r-init", "proc-l-init", "_")),
                step_fixed_cell,
            ),
            (
                "stem direct mixed conflict",
                Cell(
                    role="stem",
                    memory="right",
                    input=("wire-r-init", "write-buf-one", "_"),
                    control=(0, 0, 1),
                    buffer=(1,),
                ),
                step_stem_cell,
            ),
        )

        for name, before, step in cases:
            with self.subTest(name=name):
                result = step(before)
                predicate = recipient_non_init_command_message_rejected(before, result)

                self.assertEqual(result.status, "rejected-input")
                self.assertEqual(result.cell.role, before.role)
                self.assertEqual(result.cell.memory, before.memory)
                self.assertEqual(result.cell.input, EMPTY)
                self.assertTrue(predicate.holds, predicate.detail)

    def test_claim_manifest_covers_all_init_and_mixed_conflicts(self):
        claims = load_transition_claims(CLAIMS)
        claim = next(claim for claim in claims if claim.claim_id == CLAIM_ID)
        example_names = {example.name for example in claim.examples}

        self.assertIn("fixed all-init command conflict rejected", example_names)
        self.assertIn("stem multi command conflict rejected", example_names)

    def test_source_status_frontiers_move_beyond_multi_command_svg(self):
        recipient_non_init = json.loads(RECIPIENT_NON_INIT.read_text(encoding="utf-8"))
        recipient_status = json.loads(RECIPIENT_STATUS.read_text(encoding="utf-8"))
        stem_status = json.loads(STEM_STATUS.read_text(encoding="utf-8"))
        write_buffer_status = json.loads(WRITE_BUFFER_STATUS.read_text(encoding="utf-8"))
        standard_signal_status = json.loads(STANDARD_SIGNAL_STATUS.read_text(encoding="utf-8"))

        implemented = {
            item["adr"]: item
            for item in recipient_non_init["implemented_source_statuses"]
        }
        self.assertEqual(
            implemented["ADR-0059"]["path"],
            "sources/multi_command_recipient_input_policy_status.json",
        )
        self.assertEqual(
            recipient_non_init["multi_command_input_status"]["decision"],
            "selected-reject-and-clear",
        )
        self.assertEqual(
            recipient_non_init["safe_next_slice"],
            NO_STANDARD_SIGNAL_SAFE_NEXT,
        )
        self.assertEqual(
            write_buffer_status["safe_next_slice"],
            "no-write-buffer-follow-up-pending-after-recipient-evidence-bundle",
        )
        self.assertEqual(
            standard_signal_status["safe_next_slice"],
            NO_STANDARD_SIGNAL_SAFE_NEXT,
        )
        trace = self.status["implemented_traces"][0]
        self.assertEqual(trace["adr"], "ADR-0060")
        self.assertEqual(
            trace["path"],
            "schematics/multi_command_recipient_rejection_trace.json",
        )
        svg = self.status["implemented_svgs"][0]
        self.assertEqual(svg["adr"], "ADR-0061")
        self.assertEqual(
            svg["path"],
            "schematics/multi_command_recipient_rejection_trace.svg",
        )
        bundle = self.status["implemented_evidence_bundles"][0]
        self.assertEqual(bundle["adr"], "ADR-0069")
        self.assertEqual(
            bundle["path"],
            "evidence/multi_command_recipient_rejection_bundle.json",
        )
        self.assertEqual(
            bundle["claim_id"],
            "UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED",
        )
        self.assertEqual(
            bundle["positive_example"],
            "fixed all-init command conflict rejected",
        )
        self.assertFalse(
            any(
                item.startswith("Select a multi-command")
                for item in recipient_status["allowed_next_slices"]
            )
        )
        self.assertFalse(
            any(
                "rendered SVG" in item
                for item in stem_status["allowed_next_slices"]
            )
        )


if __name__ == "__main__":
    unittest.main()
