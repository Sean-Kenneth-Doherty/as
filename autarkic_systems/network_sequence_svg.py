"""SVG rendering for recorded network-sequence traces."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

from autarkic_systems.network_sequence_trace import NetworkSequenceTrace


POST_HANDOFF_SIGNAL_SEQUENCE_SVG_ARTIFACT = Path(
    "schematics/sequences/post_handoff_signal_sequence_trace.svg"
)
SVG_NAMESPACE = "http://www.w3.org/2000/svg"


@dataclass(frozen=True)
class NetworkSequenceSvgValidation:
    """One validation result for a rendered network-sequence SVG."""

    subject: str
    accepted: bool
    detail: str


def render_network_sequence_svg(trace: NetworkSequenceTrace) -> str:
    """Render a post-handoff network-sequence trace as SVG."""

    sender = trace.sender_initial_cell
    recipient = trace.recipient_initial_cell
    before_followup = trace.expected_recipient_before_followup
    after_followup = trace.expected_recipient_after_followup
    delivered = _tuple_text(trace.expected_delivered_tuple)
    followup = _tuple_text(trace.followup_input)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="{SVG_NAMESPACE}" width="1200" height="760" '
            'viewBox="0 0 1200 760" role="img" aria-labelledby="title desc" '
            f'data-artifact-id="{_attr(trace.artifact_id)}" '
            f'data-sequence-claim-id="{_attr(trace.sequence_claim_id)}" '
            f'data-sequence-helper="{_attr(trace.sequence_helper)}">'
        ),
        f'  <title id="title">{_text(trace.artifact_id)}</title>',
        (
            '  <desc id="desc">Generated from the network-sequence trace for '
            f'{_text(trace.sequence_claim_id)}.</desc>'
        ),
        "  <style>",
        "    .canvas { fill: #fbfaf5; stroke: #d0d5dd; stroke-width: 1.5; }",
        "    .cell { fill: #f7f4ea; stroke: #1e3a3a; stroke-width: 3; }",
        "    .sender { fill: #eef7f5; }",
        "    .recipient { fill: #fff7ea; }",
        "    .followup { fill: #eef2ff; }",
        "    .arrow { fill: none; stroke: #2f80ed; stroke-width: 5; marker-end: url(#arrow); }",
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
        '  <rect class="canvas" x="24" y="24" width="1152" height="712" rx="10" />',
        '  <g class="sequence-summary">',
        f'    <text class="label" x="56" y="70">claim: {_text(trace.sequence_claim_id)}</text>',
        f'    <text class="small" x="56" y="98">status: {_text(trace.expected_status)}</text>',
        f'    <text class="small" x="56" y="122">helper: {_text(trace.sequence_helper)}</text>',
        "  </g>",
        '  <g class="cell sender-cell">',
        '    <rect class="cell sender" x="64" y="170" width="320" height="220" rx="8" />',
        '    <text class="label" x="88" y="208">sender initial</text>',
        f'    <text class="small" x="88" y="238">role: {_text(sender["role"])}</text>',
        f'    <text class="small" x="88" y="262">memory: {_text(sender["memory"])}</text>',
        f'    <text class="small" x="88" y="286">input: {_text(_cell_field(sender, "input"))}</text>',
        f'    <text class="small" x="88" y="310">control: {_text(_cell_field(sender, "control"))}</text>',
        f'    <text class="small" x="88" y="334">buffer: {_text(_cell_field(sender, "buffer"))}</text>',
        f'    <text class="small" x="88" y="358">delivery status: {_text(trace.expected_delivery_status)}</text>',
        "  </g>",
        '  <g class="cell recipient-initial-cell">',
        '    <rect class="cell recipient" x="440" y="170" width="320" height="220" rx="8" />',
        '    <text class="label" x="464" y="208">recipient initial</text>',
        f'    <text class="small" x="464" y="238">role: {_text(recipient["role"])}</text>',
        f'    <text class="small" x="464" y="262">memory: {_text(recipient["memory"])}</text>',
        f'    <text class="small" x="464" y="286">upstream: {_text(_cell_field(recipient, "upstream"))}</text>',
        f'    <text class="small" x="464" y="310">delivered tuple: {_text(delivered)}</text>',
        f'    <text class="small" x="464" y="334">follow-up input: {_text(followup)}</text>',
        f'    <text class="small" x="464" y="358">follow-up status: {_text(trace.expected_followup_status)}</text>',
        "  </g>",
        '  <g class="cell followup-cell">',
        '    <rect class="cell followup" x="816" y="170" width="320" height="220" rx="8" />',
        '    <text class="label" x="840" y="208">recipient follow-up</text>',
        f'    <text class="small" x="840" y="238">before follow-up role: {_text(before_followup["role"])}</text>',
        f'    <text class="small" x="840" y="262">before follow-up memory: {_text(before_followup["memory"])}</text>',
        f'    <text class="small" x="840" y="286">before follow-up input: {_text(_cell_field(before_followup, "input"))}</text>',
        f'    <text class="small" x="840" y="310">after follow-up memory: {_text(after_followup["memory"])}</text>',
        f'    <text class="small" x="840" y="334">after follow-up output: {_text(_cell_field(after_followup, "output"))}</text>',
        f'    <text class="small" x="840" y="358">after follow-up input: {_text(_cell_field(after_followup, "input"))}</text>',
        "  </g>",
        '  <g class="handoff-flow">',
        '    <path class="arrow" d="M 384 280 C 405 250 421 250 440 280" />',
        '    <path class="arrow" d="M 760 280 C 781 250 797 250 816 280" />',
        "  </g>",
        '  <g class="flow-summary">',
        '    <text class="flow-title" x="64" y="460">sequence flow</text>',
    ]
    lines.extend(_render_flow(trace.routed_signal_flow, 64, 488))
    lines.extend(
        [
            "  </g>",
            "</svg>",
            "",
        ]
    )
    return "\n".join(lines)


def validate_network_sequence_svg(
    trace: NetworkSequenceTrace,
    *,
    svg_text: str,
) -> list[NetworkSequenceSvgValidation]:
    """Validate a rendered sequence SVG against the trace and renderer."""

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
        _validate_sequence_labels(trace, root),
        _validate_followup_flow(trace, root),
    ]


def _render_flow(flow: tuple[str, ...], x: int, y: int) -> list[str]:
    return [
        f'    <text class="flow" x="{x}" y="{y + index * 24}">{_text(item)}</text>'
        for index, item in enumerate(flow)
    ]


def _validate_metadata(
    trace: NetworkSequenceTrace,
    root: ET.Element | None,
) -> NetworkSequenceSvgValidation:
    if root is None:
        return _rejected("metadata", "SVG did not parse")
    expected = {
        "data-artifact-id": trace.artifact_id,
        "data-sequence-claim-id": trace.sequence_claim_id,
        "data-sequence-helper": trace.sequence_helper,
    }
    mismatched = [
        key for key, value in expected.items() if root.attrib.get(key) != value
    ]
    if mismatched:
        return _rejected("metadata", f"metadata mismatch: {', '.join(mismatched)}")
    return _accepted("metadata", "sequence metadata present")


def _validate_renderer_output(
    trace: NetworkSequenceTrace,
    svg_text: str,
) -> NetworkSequenceSvgValidation:
    if svg_text != render_network_sequence_svg(trace):
        return _rejected("rendered-svg", "committed SVG does not match renderer")
    return _accepted("rendered-svg", "committed SVG matches renderer output")


def _validate_sequence_labels(
    trace: NetworkSequenceTrace,
    root: ET.Element | None,
) -> NetworkSequenceSvgValidation:
    if root is None:
        return _rejected("sequence-labels", "SVG did not parse")
    visible_text = "\n".join(root.itertext())
    required = (
        f"status: {trace.expected_status}",
        f"delivery status: {trace.expected_delivery_status}",
        f"delivered tuple: {_tuple_text(trace.expected_delivered_tuple)}",
        f"follow-up input: {_tuple_text(trace.followup_input)}",
        f"follow-up status: {trace.expected_followup_status}",
        "before follow-up role: "
        f"{trace.expected_recipient_before_followup['role']}",
        "after follow-up output: "
        f"{_cell_field(trace.expected_recipient_after_followup, 'output')}",
    )
    missing = [item for item in required if item not in visible_text]
    if missing:
        return _rejected("sequence-labels", f"missing labels: {', '.join(missing)}")
    return _accepted(
        "sequence-labels",
        "status, delivery, follow-up, and recipient state visible",
    )


def _validate_followup_flow(
    trace: NetworkSequenceTrace,
    root: ET.Element | None,
) -> NetworkSequenceSvgValidation:
    if root is None:
        return _rejected("followup-flow", "SVG did not parse")
    visible_text = "\n".join(root.itertext())
    required = list(trace.routed_signal_flow)
    missing = [item for item in required if item not in visible_text]
    if missing:
        return _rejected("followup-flow", f"missing flow: {', '.join(missing)}")
    return _accepted("followup-flow", "follow-up flow visible")


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


def _accepted(subject: str, detail: str) -> NetworkSequenceSvgValidation:
    return NetworkSequenceSvgValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> NetworkSequenceSvgValidation:
    return NetworkSequenceSvgValidation(subject=subject, accepted=False, detail=detail)
