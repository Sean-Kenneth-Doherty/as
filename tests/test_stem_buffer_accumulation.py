import unittest

from autarkic_systems.universal_cell import Cell, step_stem_cell


EMPTY = ("_", "_", "_")


class StemBufferAccumulationTests(unittest.TestCase):
    def test_one_hot_standard_signal_selects_control_rail(self):
        cell = Cell(role="stem", memory="right", input=(0, 0, 1))

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "stem-control-selected")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.control, (0, 0, 1))
        self.assertEqual(result.cell.buffer, ())
        self.assertEqual(result.cell.role, "stem")

    def test_matching_control_signal_appends_one_to_buffer(self):
        cell = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(0, 1, 0),
            buffer=(0,),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "stem-buffer-appended")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.control, (0, 1, 0))
        self.assertEqual(result.cell.buffer, (0, 1))

    def test_different_one_hot_signal_appends_zero_to_buffer(self):
        cell = Cell(
            role="stem",
            memory="left",
            input=(1, 0, 0),
            control=(0, 1, 0),
            buffer=(1, 1),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "stem-buffer-appended")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.control, (0, 1, 0))
        self.assertEqual(result.cell.buffer, (1, 1, 0))

    def test_full_buffer_is_explicit_boundary_without_consuming_input(self):
        cell = Cell(
            role="stem",
            memory="right",
            input=(0, 0, 1),
            control=(0, 0, 1),
            buffer=(1, 0, 1, 0, 1),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "stem-buffer-full")
        self.assertEqual(result.cell, cell)

    def test_malformed_stem_input_is_rejected_and_cleared(self):
        cell = Cell(
            role="stem",
            memory="right",
            input=(1, 1, 0),
            control=(0, 0, 1),
            buffer=(1,),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "rejected-input")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.control, (0, 0, 1))
        self.assertEqual(result.cell.buffer, (1,))

    def test_automail_reconfiguration_still_has_priority(self):
        cell = Cell(role="stem", memory="right", automail="wl", input=(0, 0, 1))

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "automail-reconfigured")
        self.assertEqual(result.cell.role, "wire")
        self.assertEqual(result.cell.memory, "left")
        self.assertEqual(result.cell.automail, "_")
        self.assertEqual(result.cell.control, ())
        self.assertEqual(result.cell.buffer, ())


if __name__ == "__main__":
    unittest.main()
