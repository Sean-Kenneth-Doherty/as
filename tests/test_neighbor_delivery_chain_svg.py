import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from autarkic_systems.chain_svg import (
    NEIGHBOR_DELIVERY_CHAIN_SVG_ARTIFACT,
    SVG_NAMESPACE,
    render_transition_chain_svg,
    validate_transition_chain_svg,
)
from autarkic_systems.chain_trace import load_transition_chain_trace


TRACE_ARTIFACT = Path("schematics/chains/neighbor_delivery_recipient_chain_trace.json")


class NeighborDeliveryChainSvgTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_transition_chain_trace(TRACE_ARTIFACT)
        self.svg_text = render_transition_chain_svg(self.trace)

    def test_svg_is_nonblank_xml_with_chain_metadata(self):
        self.assertGreater(len(self.svg_text), 1000)

        root = ET.fromstring(self.svg_text)

        self.assertEqual(root.tag, f"{{{SVG_NAMESPACE}}}svg")
        self.assertEqual(root.attrib["data-artifact-id"], self.trace.artifact_id)
        self.assertEqual(root.attrib["data-claim-id"], self.trace.claim_id)
        self.assertEqual(root.attrib["data-chain-helper"], self.trace.chain_helper)

    def test_svg_records_sender_recipient_and_handoff_details(self):
        self.assertIn("sender: sender-neighbor-delivery", self.svg_text)
        self.assertIn("recipient: recipient-init-consumption", self.svg_text)
        self.assertIn("status: neighbor-delivery-consumed", self.svg_text)
        self.assertIn("sender output[1] -> recipient upstream[1]", self.svg_text)
        self.assertIn("delivered tuple: [_, proc-l-init, _]", self.svg_text)
        self.assertIn("sender after output: [_, proc-l-init, _]", self.svg_text)
        self.assertIn("recipient before upstream: [_, proc-l-init, _]", self.svg_text)
        self.assertIn("recipient after role: proc", self.svg_text)
        self.assertIn("recipient after memory: left", self.svg_text)

    def test_svg_records_both_step_signal_flows(self):
        root = ET.fromstring(self.svg_text)
        visible_text = "\n".join(root.itertext())

        for flow in self.trace.sender_step.routed_signal_flow:
            with self.subTest(flow=flow):
                self.assertIn(flow, visible_text)
        for flow in self.trace.recipient_step.routed_signal_flow:
            with self.subTest(flow=flow):
                self.assertIn(flow, visible_text)

    def test_committed_chain_svg_matches_renderer_output(self):
        committed = NEIGHBOR_DELIVERY_CHAIN_SVG_ARTIFACT.read_text(
            encoding="utf-8",
        )

        self.assertEqual(committed, self.svg_text)

    def test_chain_svg_validator_accepts_committed_svg(self):
        results = validate_transition_chain_svg(
            self.trace,
            svg_text=NEIGHBOR_DELIVERY_CHAIN_SVG_ARTIFACT.read_text(
                encoding="utf-8",
            ),
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)
        self.assertEqual(
            {result.subject for result in results},
            {
                "xml",
                "metadata",
                "rendered-svg",
                "chain-labels",
                "handoff-flow",
            },
        )

    def test_chain_svg_validator_rejects_drifted_handoff_text(self):
        drifted = self.svg_text.replace(
            "sender output[1] -> recipient upstream[1]",
            "sender output[0] -> recipient upstream[0]",
        )

        results = validate_transition_chain_svg(self.trace, svg_text=drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "rendered-svg"
                and "does not match" in result.detail
                for result in results
            ),
            results,
        )


if __name__ == "__main__":
    unittest.main()
