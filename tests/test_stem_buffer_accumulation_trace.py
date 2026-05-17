import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.prc_hardware_map import load_prc_hardware_witness_map
from autarkic_systems.schematic_trace import (
    REQUIRED_CELL_FIELDS,
    REQUIRED_INTERPRETIVE_LAYERS,
    STEM_BUFFER_ACCUMULATION_TRACE_ARTIFACT_ID,
    execute_schematic_trace,
    load_schematic_trace,
    validate_schematic_trace,
)


ARTIFACT = Path("schematics/stem_buffer_accumulation_trace.json")
WITNESS_MAP = Path("sources/prc_hardware_witness_map.json")


class StemBufferAccumulationTraceTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_schematic_trace(ARTIFACT)
        self.witness_map = load_prc_hardware_witness_map(WITNESS_MAP)

    def test_artifact_is_stem_buffer_accumulation_trace(self):
        self.assertEqual(
            STEM_BUFFER_ACCUMULATION_TRACE_ARTIFACT_ID,
            "stem-buffer-accumulation-schematic-and-uc-transition-trace",
        )
        self.assertEqual(self.trace.artifact_id, STEM_BUFFER_ACCUMULATION_TRACE_ARTIFACT_ID)
        self.assertEqual(self.trace.trace.transition_function, "step_stem_cell")

    def test_stem_buffer_trace_uses_existing_schema_vocabulary(self):
        self.assertEqual(REQUIRED_CELL_FIELDS, self.trace.trace.cell_fields)
        self.assertEqual(
            REQUIRED_INTERPRETIVE_LAYERS,
            tuple(layer.layer_id for layer in self.trace.schematic.layers),
        )
        self.assertEqual(len(self.trace.schematic.ports), 3)

    def test_stem_buffer_trace_records_matching_append(self):
        before = self.trace.trace.before_cell
        after = self.trace.trace.expected_after_cell

        self.assertEqual(before["role"], "stem")
        self.assertEqual(before["automail"], "_")
        self.assertEqual(before["input"], [0, 1, 0])
        self.assertEqual(before["control"], [0, 1, 0])
        self.assertEqual(before["buffer"], [0])
        self.assertEqual(after["buffer"], [0, 1])
        self.assertEqual(after["input"], ["_", "_", "_"])
        self.assertEqual(self.trace.trace.expected_status, "stem-buffer-appended")

    def test_stem_buffer_trace_records_buffer_flow(self):
        self.assertEqual(
            self.trace.trace.routed_signal_flow,
            (
                "control[0,1,0] active",
                "input[0,1,0] matches control -> append 1",
                "buffer[0] -> buffer[0,1]",
            ),
        )

    def test_stem_buffer_trace_executes_against_existing_probe(self):
        execution = execute_schematic_trace(self.trace)

        self.assertEqual(execution.status, self.trace.trace.expected_status)
        self.assertEqual(execution.after_cell, self.trace.trace.expected_after_cell)

    def test_stem_buffer_trace_validates_against_witness_map(self):
        results = validate_schematic_trace(
            self.trace,
            hardware_witness_map=self.witness_map,
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_drifted_buffer_append_is_rejected(self):
        drifted_after = dict(self.trace.trace.expected_after_cell)
        drifted_after["buffer"] = [0, 0]
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
                and result.subject == "stem-buffer-accumulation"
                for result in results
            ),
            results,
        )

    def test_drifted_buffer_flow_is_rejected(self):
        drifted = replace(
            self.trace,
            trace=replace(
                self.trace.trace,
                routed_signal_flow=("input[0,1,0] -> buffer[0,0]",),
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
