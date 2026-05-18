"""Top-level vertical demo digest for the current AS evidence stack."""

from __future__ import annotations

import argparse
import json
from typing import Any

from autarkic_systems.network_sequence_demo import build_network_sequence_demo_report
from autarkic_systems.project_status import build_project_status_report


DEMONSTRATION = "post-handoff signal routing through checked evidence"
STANDARD_SIGNAL_BOUNDARY = (
    "no standard-signal command-token execution change without new source evidence"
)


def build_vertical_demo_digest() -> dict[str, Any]:
    """Build a first-run digest from the accepted project-status surface."""

    status = build_project_status_report()
    sequence_demo = build_network_sequence_demo_report()
    transition = status["transition_evidence"]
    chain = status["chain_evidence"]
    sequence = status["sequence_evidence"]
    transition_claims = status["transition_claims"]
    chain_claims = status["chain_claims"]
    sequence_claims = status["sequence_claims"]
    proof_rules = status["proof_rule_audit"]["combined"]["rule_counts"]
    sequence_bundle = sequence["bundles"][0] if sequence["bundles"] else {}
    frontier = status["frontier"]
    return {
        "accepted": status["accepted"] and sequence_demo["accepted"],
        "demonstration": DEMONSTRATION,
        "evidence_counts": {
            "transition_bundles": transition["bundle_count"],
            "chain_bundles": chain["bundle_count"],
            "sequence_bundles": sequence["bundle_count"],
        },
        "claim_counts": {
            "transition_claims": transition_claims["claim_count"],
            "transition_matched_examples": transition_claims["matched_count"],
            "chain_claims": chain_claims["claim_count"],
            "sequence_claims": sequence_claims["claim_count"],
        },
        "proof_rules": {
            "predicate-result": proof_rules.get("predicate-result", 0),
            "manifest-example": proof_rules.get("manifest-example", 0),
        },
        "blocked_commands": frontier["blocked_commands"],
        "safe_next_slice": frontier["safe_next_slice"],
        "registries": {
            "transition": transition["path"],
            "chain": chain["path"],
            "sequence": sequence["path"],
        },
        "sequence_evidence_bundle": sequence_bundle,
        "evidence_trail": sequence_demo["evidence_layers"],
        "missing_evidence_paths": sequence_demo["missing_evidence_paths"],
        "validation_subjects": [
            result["subject"]
            for result in sequence_demo["validation"]["results"]
        ],
        "boundary": STANDARD_SIGNAL_BOUNDARY,
    }


def format_vertical_demo_digest(digest: dict[str, Any]) -> str:
    """Format the vertical demo digest for a first-run human reader."""

    status = "accepted" if digest["accepted"] else "rejected"
    evidence = digest["evidence_counts"]
    claims = digest["claim_counts"]
    proof_rules = digest["proof_rules"]
    blocked = digest["blocked_commands"] or []
    registries = digest["registries"]
    sequence_bundle = digest["sequence_evidence_bundle"]
    missing_paths = digest["missing_evidence_paths"] or []
    evidence_trail = digest["evidence_trail"]
    return "\n".join([
        f"Autarkic Systems vertical demo: {status}",
        f"Current demonstration: {digest['demonstration']}",
        (
            f"Evidence: {evidence['transition_bundles']} transition bundles; "
            f"{evidence['chain_bundles']} chain bundles; "
            f"{evidence['sequence_bundles']} sequence "
            f"{_count_noun(evidence['sequence_bundles'], 'bundle', 'bundles')}"
        ),
        (
            f"Claims: {claims['transition_claims']} transition claims/"
            f"{claims['transition_matched_examples']} matched examples; "
            f"{claims['chain_claims']} chain claims; "
            f"{claims['sequence_claims']} sequence "
            f"{_count_noun(claims['sequence_claims'], 'claim', 'claims')}"
        ),
        (
            "Proof rules: "
            f"predicate-result={proof_rules['predicate-result']}, "
            f"manifest-example={proof_rules['manifest-example']}"
        ),
        "Blocked command frontier: " + (", ".join(blocked) if blocked else "none"),
        f"Safe next slice: {digest['safe_next_slice'] or 'none'}",
        f"Sequence evidence bundle: {sequence_bundle.get('path', '')}",
        f"Sequence claim: {sequence_bundle.get('sequence_claim_id', '')}",
        f"Expected status: {sequence_bundle.get('expected_status', '')}",
        f"Transition registry: {registries['transition']}",
        f"Chain registry: {registries['chain']}",
        f"Sequence registry: {registries['sequence']}",
        "Missing evidence paths: "
        + (", ".join(missing_paths) if missing_paths else "none"),
        "Evidence trail:",
        *[
            f"- {layer['role']}: {layer['path']}"
            + ("" if layer["exists"] else " (missing)")
            for layer in evidence_trail
        ],
        f"Boundary: {digest['boundary']}",
    ])


def run_vertical_demo_cli(argv: list[str] | None = None) -> int:
    """Run the top-level vertical demo digest command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.vertical_demo",
        description="Render the AS vertical evidence demo digest.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the demo digest.",
    )
    args = parser.parse_args(argv)

    digest = build_vertical_demo_digest()
    if args.format == "json":
        print(json.dumps(digest, sort_keys=True))
    else:
        print(format_vertical_demo_digest(digest))
    return 0 if digest["accepted"] else 1


def _count_noun(count: int, singular: str, plural: str) -> str:
    return singular if count == 1 else plural


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess test.
    raise SystemExit(run_vertical_demo_cli())
