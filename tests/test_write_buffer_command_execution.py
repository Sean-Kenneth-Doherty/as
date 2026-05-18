import unittest

from autarkic_systems.universal_cell import Cell, step_stem_cell


EMPTY = ("_", "_", "_")


class WriteBufferCommandExecutionTests(unittest.TestCase):
    def test_self_mailbox_write_buffer_zero_appends_literal_and_clears_mailbox(self):
        cell = Cell(
            role="stem",
            memory="right",
            self_mailbox="write-buf-zero",
            control=(0, 1, 0),
            buffer=(1, 0),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "self-mailbox-write-buffer-appended")
        self.assertEqual(result.cell.role, "stem")
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.output, EMPTY)
        self.assertEqual(result.cell.automail, "_")
        self.assertEqual(result.cell.self_mailbox, "_")
        self.assertEqual(result.cell.control, (0, 1, 0))
        self.assertEqual(result.cell.buffer, (1, 0, 0))

    def test_self_mailbox_write_buffer_one_appends_literal_and_preserves_control(self):
        cell = Cell(
            role="stem",
            memory="left",
            self_mailbox="write-buf-one",
            control=(1, 0, 0),
            buffer=(0,),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "self-mailbox-write-buffer-appended")
        self.assertEqual(result.cell.memory, "left")
        self.assertEqual(result.cell.self_mailbox, "_")
        self.assertEqual(result.cell.control, (1, 0, 0))
        self.assertEqual(result.cell.buffer, (0, 1))

    def test_self_mailbox_write_buffer_preserves_full_buffer_boundary(self):
        cell = Cell(
            role="stem",
            memory="right",
            self_mailbox="write-buf-one",
            control=(0, 0, 1),
            buffer=(1, 0, 1, 0, 1),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "stem-buffer-full")
        self.assertEqual(result.cell, cell)

    def test_completed_self_write_buffer_zero_command_appends_literal_zero(self):
        cell = Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(0, 1, 0),
            buffer=(0, 0, 1, 1),
        )

        result = step_stem_cell(cell)

        self.assertEqual(
            result.status,
            "stem-command-buffer-self-write-buffer-appended",
        )
        self.assertEqual(result.cell.role, "stem")
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.output, EMPTY)
        self.assertEqual(result.cell.automail, "_")
        self.assertEqual(result.cell.self_mailbox, "_")
        self.assertEqual(result.cell.control, (0, 1, 0))
        self.assertEqual(result.cell.buffer, (0,))

    def test_completed_self_write_buffer_one_command_appends_literal_one(self):
        cell = Cell(
            role="stem",
            memory="left",
            input=(0, 1, 0),
            control=(0, 1, 0),
            buffer=(0, 0, 1, 1),
        )

        result = step_stem_cell(cell)

        self.assertEqual(
            result.status,
            "stem-command-buffer-self-write-buffer-appended",
        )
        self.assertEqual(result.cell.memory, "left")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.self_mailbox, "_")
        self.assertEqual(result.cell.control, (0, 1, 0))
        self.assertEqual(result.cell.buffer, (1,))


if __name__ == "__main__":
    unittest.main()
