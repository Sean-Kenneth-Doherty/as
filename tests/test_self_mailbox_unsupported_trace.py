import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.prc_hardware_map import load_prc_hardware_witness_map
from autarkic_systems.schematic_trace import (
    REQUIRED_CELL_FIELDS,
    REQUIRED_INTERPRETIVE_LAYERS,
    SELF_MAILBOX_UNSUPPORTED_TRACE_ARTIFACT_ID,
    execute_schematic_trace,
    load_schematic_trace,
    validate_schematic_trace,
)


ARTIFACT = Path("schematics/self_mailbox_unsupported_trace.json")
WITNESS_MAP = Path("sources/prc_hardware_witness_map.json")


class SelfMailboxUnsupportedTraceTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_schematic_trace(ARTIFACT)
        self.witness_map = load_prc_hardware_witness_map(WITNESS_MAP)

    def test_artifact_is_self_mailbox_unsupported_trace(self):
        self.assertEqual(
            SELF_MAILBOX_UNSUPPORTED_TRACE_ARTIFACT_ID,
            "self-mailbox-unsupported-schematic-and-uc-transition-trace",
        )
        self.assertEqual(
            self.trace.artifact_id,
            SELF_MAILBOX_UNSUPPORTED_TRACE_ARTIFACT_ID,
        )
        self.assertEqual(self.trace.trace.transition_function, "step_stem_cell")

    def test_unsupported_trace_uses_existing_schema_vocabulary(self):
        self.assertEqual(REQUIRED_CELL_FIELDS, self.trace.trace.cell_fields)
        self.assertEqual(
            REQUIRED_INTERPRETIVE_LAYERS,
            tuple(layer.layer_id for layer in self.trace.schematic.layers),
        )
        self.assertEqual(len(self.trace.schematic.ports), 3)

    def test_unsupported_trace_records_standard_signal_preservation(self):
        before = self.trace.trace.before_cell
        after = self.trace.trace.expected_after_cell

        self.assertEqual(before["role"], "stem")
        self.assertEqual(before["automail"], "_")
        self.assertEqual(before["self_mailbox"], "standard-signal")
        self.assertEqual(before["control"], [1, 0, 0])
        self.assertEqual(before["buffer"], [0])
        self.assertEqual(after, before)
        self.assertEqual(self.trace.trace.expected_status, "self-mailbox-unsupported")

    def test_unsupported_trace_records_preservation_flow(self):
        self.assertEqual(
            self.trace.trace.routed_signal_flow,
            (
                "self_mailbox[standard-signal] unsupported",
                "cell state preserved",
                "standard-signal command semantics unresolved",
            ),
        )

    def test_unsupported_trace_executes_against_existing_probe(self):
        execution = execute_schematic_trace(self.trace)

        self.assertEqual(execution.status, self.trace.trace.expected_status)
        self.assertEqual(execution.after_cell, self.trace.trace.expected_after_cell)

    def test_unsupported_trace_validates_against_witness_map(self):
        results = validate_schematic_trace(
            self.trace,
            hardware_witness_map=self.witness_map,
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_drifted_cleared_mailbox_is_rejected(self):
        drifted_after = dict(self.trace.trace.expected_after_cell)
        drifted_after["self_mailbox"] = "_"
        drifted = replace(
            self.trace,
            trace=replace(self.trace.trace, expected_after_cell=drifted_after),
        )

        results = validate_schematic_trace(
            drifted,
            hardware_witness_map=self.witness_map,
        )

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "self-mailbox-unsupported"
                for result in results
            ),
            results,
        )

    def test_drifted_control_state_is_rejected(self):
        drifted_after = dict(self.trace.trace.expected_after_cell)
        drifted_after["control"] = []
        drifted = replace(
            self.trace,
            trace=replace(self.trace.trace, expected_after_cell=drifted_after),
        )

        results = validate_schematic_trace(
            drifted,
            hardware_witness_map=self.witness_map,
        )

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "self-mailbox-unsupported"
                for result in results
            ),
            results,
        )

    def test_drifted_unsupported_flow_is_rejected(self):
        drifted = replace(
            self.trace,
            trace=replace(
                self.trace.trace,
                routed_signal_flow=("self_mailbox[standard-signal] executed",),
            ),
        )

        results = validate_schematic_trace(
            drifted,
            hardware_witness_map=self.witness_map,
        )

        self.assertTrue(
            any(
                not result.accepted and result.subject == "routed_signal_flow"
                for result in results
            ),
            results,
        )


if __name__ == "__main__":
    unittest.main()
