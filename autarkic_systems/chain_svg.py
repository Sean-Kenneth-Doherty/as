"""SVG rendering for recorded transition-chain traces."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

from autarkic_systems.chain_trace import TransitionChainTrace


NEIGHBOR_DELIVERY_CHAIN_SVG_ARTIFACT = Path(
    "schematics/chains/neighbor_delivery_recipient_chain_trace.svg"
)
SVG_NAMESPACE = "http://www.w3.org/2000/svg"


@dataclass(frozen=True)
class ChainSvgValidation:
    """One validation result for a rendered transition-chain SVG."""

    subject: str
    accepted: bool
    detail: str


def render_transition_chain_svg(trace: TransitionChainTrace) -> str:
    """Render a two-cell transition-chain trace as SVG."""

    sender_before = trace.sender_step.before_cell
    sender_after = trace.sender_step.expected_after_cell
    recipient_before = trace.recipient_step.before_cell
    recipient_after = trace.recipient_step.expected_after_cell
    delivered = "[" + ", ".join(str(item) for item in trace.handoff.delivered_tuple) + "]"

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="{SVG_NAMESPACE}" width="1200" height="720" '
            'viewBox="0 0 1200 720" role="img" aria-labelledby="title desc" '
            f'data-artifact-id="{_attr(trace.artifact_id)}" '
            f'data-claim-id="{_attr(trace.claim_id)}" '
            f'data-chain-helper="{_attr(trace.chain_helper)}">'
        ),
        f'  <title id="title">{_text(trace.artifact_id)}</title>',
        (
            '  <desc id="desc">Generated from the transition-chain trace for '
            f'{_text(trace.claim_id)}.</desc>'
        ),
        "  <style>",
        "    .canvas { fill: #fbfaf5; stroke: #d0d5dd; stroke-width: 1.5; }",
        "    .cell { fill: #f7f4ea; stroke: #1e3a3a; stroke-width: 3; }",
        "    .sender { fill: #eef7f5; }",
        "    .recipient { fill: #fff7ea; }",
        "    .handoff { fill: none; stroke: #2f80ed; stroke-width: 5; marker-end: url(#arrow); }",
        "    .handoff-label { fill: #1e3a3a; font: 700 17px sans-serif; }",
        "    .label { fill: #162020; font: 700 18px sans-serif; }",
        "    .small { fill: #162020; font: 14px monospace; }",
        "    .flow-title { fill: #162020; font: 700 15px sans-serif; }",
        "    .flow { fill: #384444; font: 13px monospace; }",
        "  </style>",
        "  <defs>",
        '    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">',
        '      <path d="M 0 0 L 10 5 L 0 10 z" fill="#2f80ed" />',
        "    </marker>",
        "  </defs>",
        '  <rect class="canvas" x="24" y="24" width="1152" height="672" rx="10" />',
        '  <g class="chain-summary">',
        f'    <text class="label" x="56" y="70">claim: {_text(trace.claim_id)}</text>',
        f'    <text class="small" x="56" y="98">status: {_text(trace.expected_status)}</text>',
        f'    <text class="small" x="56" y="122">helper: {_text(trace.chain_helper)}</text>',
        "  </g>",
        '  <g class="cell sender-cell" data-step-id="'
        f'{_attr(trace.sender_step.step_id)}">',
        '    <rect class="cell sender" x="64" y="176" width="392" height="212" rx="8" />',
        f'    <text class="label" x="88" y="214">sender: {_text(trace.sender_step.step_id)}</text>',
        f'    <text class="small" x="88" y="244">transition: {_text(trace.sender_step.transition_function)}</text>',
        f'    <text class="small" x="88" y="268">step status: {_text(trace.sender_step.expected_status)}</text>',
        f'    <text class="small" x="88" y="292">sender before input: {_text(_cell_field(sender_before, "input"))}</text>',
        f'    <text class="small" x="88" y="316">sender before buffer: {_text(_cell_field(sender_before, "buffer"))}</text>',
        f'    <text class="small" x="88" y="340">sender after output: {_text(_cell_field(sender_after, "output"))}</text>',
        f'    <text class="small" x="88" y="364">sender after buffer: {_text(_cell_field(sender_after, "buffer"))}</text>',
        "  </g>",
        '  <g class="cell recipient-cell" data-step-id="'
        f'{_attr(trace.recipient_step.step_id)}">',
        '    <rect class="cell recipient" x="744" y="176" width="392" height="212" rx="8" />',
        f'    <text class="label" x="768" y="214">recipient: {_text(trace.recipient_step.step_id)}</text>',
        f'    <text class="small" x="768" y="244">transition: {_text(trace.recipient_step.transition_function)}</text>',
        f'    <text class="small" x="768" y="268">step status: {_text(trace.recipient_step.expected_status)}</text>',
        f'    <text class="small" x="768" y="292">recipient before upstream: {_text(_cell_field(recipient_before, "upstream"))}</text>',
        f'    <text class="small" x="768" y="316">recipient after role: {_text(recipient_after["role"])}</text>',
        f'    <text class="small" x="768" y="340">recipient after memory: {_text(recipient_after["memory"])}</text>',
        f'    <text class="small" x="768" y="364">recipient after upstream: {_text(_cell_field(recipient_after, "upstream"))}</text>',
        "  </g>",
        '  <g class="handoff" data-source-step="'
        f'{_attr(trace.handoff.source_step)}" data-target-step="{_attr(trace.handoff.target_step)}">',
        '    <path class="handoff" d="M 456 282 C 548 210 654 210 744 282" />',
        '    <text class="handoff-label" x="600" y="246" text-anchor="middle">'
        f'{_text(trace.handoff.source_field)} -> {_text(trace.handoff.target_field)}</text>',
        '    <text class="small" x="600" y="274" text-anchor="middle">'
        'sender output[1] -> recipient upstream[1]</text>',
        f'    <text class="small" x="600" y="302" text-anchor="middle">delivered tuple: {_text(delivered)}</text>',
        "  </g>",
        '  <g class="flow-summary sender-flow">',
        '    <text class="flow-title" x="64" y="440">sender flow</text>',
    ]
    lines.extend(_render_flow(trace.sender_step.routed_signal_flow, 64, 466))
    lines.extend(
        [
            '  </g>',
            '  <g class="flow-summary recipient-flow">',
            '    <text class="flow-title" x="626" y="440">recipient flow</text>',
        ]
    )
    lines.extend(_render_flow(trace.recipient_step.routed_signal_flow, 626, 466))
    lines.extend(
        [
            "  </g>",
            "</svg>",
            "",
        ]
    )
    return "\n".join(lines)


def validate_transition_chain_svg(
    trace: TransitionChainTrace,
    *,
    svg_text: str,
) -> list[ChainSvgValidation]:
    """Validate a rendered chain SVG against the trace and renderer."""

    root: ET.Element | None
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as exc:
        root = None
        xml_result = _rejected("xml", f"invalid XML: {exc}")
    else:
        if root.tag != f"{{{SVG_NAMESPACE}}}svg":
            xml_result = _rejected("xml", f"unexpected root tag: {root.tag}")
        else:
            xml_result = _accepted("xml", "SVG root parsed")

    return [
        xml_result,
        _validate_metadata(trace, root),
        _validate_renderer_output(trace, svg_text),
        _validate_chain_labels(trace, root),
        _validate_handoff_flow(trace, root),
    ]


def _render_flow(flow: tuple[str, ...], x: int, y: int) -> list[str]:
    return [
        f'    <text class="flow" x="{x}" y="{y + index * 24}">{_text(item)}</text>'
        for index, item in enumerate(flow)
    ]


def _validate_metadata(
    trace: TransitionChainTrace,
    root: ET.Element | None,
) -> ChainSvgValidation:
    if root is None:
        return _rejected("metadata", "SVG did not parse")
    expected = {
        "data-artifact-id": trace.artifact_id,
        "data-claim-id": trace.claim_id,
        "data-chain-helper": trace.chain_helper,
    }
    mismatched = [
        key for key, value in expected.items() if root.attrib.get(key) != value
    ]
    if mismatched:
        return _rejected("metadata", f"metadata mismatch: {', '.join(mismatched)}")
    return _accepted("metadata", "chain metadata present")


def _validate_renderer_output(
    trace: TransitionChainTrace,
    svg_text: str,
) -> ChainSvgValidation:
    if svg_text != render_transition_chain_svg(trace):
        return _rejected("rendered-svg", "committed SVG does not match renderer")
    return _accepted("rendered-svg", "committed SVG matches renderer output")


def _validate_chain_labels(
    trace: TransitionChainTrace,
    root: ET.Element | None,
) -> ChainSvgValidation:
    if root is None:
        return _rejected("chain-labels", "SVG did not parse")
    visible_text = "\n".join(root.itertext())
    required = (
        f"sender: {trace.sender_step.step_id}",
        f"recipient: {trace.recipient_step.step_id}",
        f"status: {trace.expected_status}",
        f"delivered tuple: {_tuple_text(trace.handoff.delivered_tuple)}",
    )
    missing = [item for item in required if item not in visible_text]
    if missing:
        return _rejected("chain-labels", f"missing labels: {', '.join(missing)}")
    return _accepted("chain-labels", "sender, recipient, status, and tuple visible")


def _validate_handoff_flow(
    trace: TransitionChainTrace,
    root: ET.Element | None,
) -> ChainSvgValidation:
    if root is None:
        return _rejected("handoff-flow", "SVG did not parse")
    visible_text = "\n".join(root.itertext())
    required = [
        "sender output[1] -> recipient upstream[1]",
        *trace.sender_step.routed_signal_flow,
        *trace.recipient_step.routed_signal_flow,
    ]
    missing = [item for item in required if item not in visible_text]
    if missing:
        return _rejected("handoff-flow", f"missing flow: {', '.join(missing)}")
    return _accepted("handoff-flow", "handoff and step flows visible")


def _cell_field(cell: dict[str, object], field: str) -> str:
    value = cell[field]
    if isinstance(value, list):
        return "[" + ", ".join(str(item) for item in value) + "]"
    return str(value)


def _tuple_text(value: tuple[object, ...]) -> str:
    return "[" + ", ".join(str(item) for item in value) + "]"


def _text(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _attr(value: object) -> str:
    return _text(value).replace('"', "&quot;")


def _accepted(subject: str, detail: str) -> ChainSvgValidation:
    return ChainSvgValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> ChainSvgValidation:
    return ChainSvgValidation(subject=subject, accepted=False, detail=detail)
