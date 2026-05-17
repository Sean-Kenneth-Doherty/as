import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.chain_trace import (
    NEIGHBOR_DELIVERY_CHAIN_TRACE_ARTIFACT_ID,
    execute_transition_chain_trace,
    load_transition_chain_trace,
    validate_transition_chain_trace,
)


ARTIFACT = Path("schematics/chains/neighbor_delivery_recipient_chain_trace.json")
CLAIM_ID = "UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED"


class NeighborDeliveryChainTraceTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_transition_chain_trace(ARTIFACT)

    def test_artifact_names_the_neighbor_delivery_recipient_chain(self):
        self.assertEqual(
            NEIGHBOR_DELIVERY_CHAIN_TRACE_ARTIFACT_ID,
            "neighbor-delivery-recipient-chain-trace",
        )
        self.assertEqual(
            self.trace.artifact_id,
            NEIGHBOR_DELIVERY_CHAIN_TRACE_ARTIFACT_ID,
        )
        self.assertEqual(self.trace.claim_id, CLAIM_ID)
        self.assertEqual(
            self.trace.chain_helper,
            "execute_neighbor_delivery_recipient_chain",
        )
        self.assertEqual(self.trace.expected_status, "neighbor-delivery-consumed")

    def test_trace_records_sender_handoff_and_recipient_cells(self):
        sender_before = self.trace.sender_step.before_cell
        sender_after = self.trace.sender_step.expected_after_cell
        recipient_initial = self.trace.recipient_initial_cell
        recipient_before = self.trace.recipient_step.before_cell
        recipient_after = self.trace.recipient_step.expected_after_cell

        self.assertEqual(sender_before["role"], "stem")
        self.assertEqual(sender_before["input"], [1, 0, 0])
        self.assertEqual(sender_before["control"], [1, 0, 0])
        self.assertEqual(sender_before["buffer"], [1, 0, 1, 0])
        self.assertEqual(sender_after["output"], ["_", "proc-l-init", "_"])
        self.assertEqual(self.trace.handoff.delivered_tuple, ("_", "proc-l-init", "_"))
        self.assertEqual(recipient_initial["role"], "wire")
        self.assertEqual(recipient_initial["upstream"], ["_", "_", "_"])
        self.assertEqual(
            self.trace.handoff.expected_recipient_before_cell,
            recipient_before,
        )
        self.assertEqual(recipient_before["upstream"], ["_", "proc-l-init", "_"])
        self.assertEqual(recipient_after["role"], "proc")
        self.assertEqual(recipient_after["memory"], "left")
        self.assertEqual(recipient_after["upstream"], ["_", "_", "_"])

    def test_trace_records_two_step_signal_flow(self):
        self.assertEqual(
            self.trace.sender_step.routed_signal_flow,
            (
                "control[1,0,0] active",
                "input[1,0,0] matches control -> append 1",
                "buffer[1,0,1,0] -> buffer[1,0,1,0,1]",
                "decode value 21 -> neighbor-b/proc-l-init",
                "neighbor command[proc-l-init] -> output[1]",
                "command buffer delivered; control/buffer cleared",
            ),
        )
        self.assertEqual(
            self.trace.recipient_step.routed_signal_flow,
            (
                "sender output[1] -> recipient upstream[1]",
                "command[proc-l-init] -> role proc",
                "command[proc-l-init] -> memory left",
                "command[proc-l-init] consumed -> _",
                "recipient upstream cleared; command state cleared",
            ),
        )

    def test_trace_executes_against_chain_helper(self):
        execution = execute_transition_chain_trace(self.trace)

        self.assertTrue(execution.accepted, execution.detail)
        self.assertEqual(execution.status, self.trace.expected_status)
        self.assertEqual(
            execution.sender_after_cell,
            self.trace.sender_step.expected_after_cell,
        )
        self.assertEqual(
            execution.recipient_before_cell,
            self.trace.handoff.expected_recipient_before_cell,
        )
        self.assertEqual(
            execution.recipient_after_cell,
            self.trace.recipient_step.expected_after_cell,
        )

    def test_trace_validates_chain_contract(self):
        results = validate_transition_chain_trace(self.trace)

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)
        self.assertEqual(
            {result.subject for result in results},
            {
                "schema",
                "participants",
                "sender-step",
                "handoff",
                "recipient-step",
                "chain-execution",
                "boundary",
            },
        )

    def test_drifted_handoff_tuple_is_rejected(self):
        drifted = replace(
            self.trace,
            handoff=replace(
                self.trace.handoff,
                delivered_tuple=("proc-l-init", "_", "_"),
            ),
        )

        results = validate_transition_chain_trace(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "handoff"
                and "delivered tuple" in result.detail
                for result in results
            ),
            results,
        )

    def test_drifted_recipient_after_cell_is_rejected(self):
        drifted_after = dict(self.trace.recipient_step.expected_after_cell)
        drifted_after["role"] = "wire"
        drifted = replace(
            self.trace,
            recipient_step=replace(
                self.trace.recipient_step,
                expected_after_cell=drifted_after,
            ),
        )

        results = validate_transition_chain_trace(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject in {"recipient-step", "chain-execution"}
                for result in results
            ),
            results,
        )


if __name__ == "__main__":
    unittest.main()
