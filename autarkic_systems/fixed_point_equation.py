"""Checked fixed-point equation candidate surface for AS.

This module deliberately does not prove a fixed point. It constructs the naive
candidate obtained by substituting the checked quotation term into the current
fixed-point target template, encodes the result, and records whether that code
actually matches the original quoted target code. At this stage the answer is
negative, which is exactly the guardrail AS needs before attempting a real
diagonal construction.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point import (
    FixedPointTarget,
    load_fixed_point_targets,
    validate_fixed_point_targets,
)
from autarkic_systems.formal_code import (
    FormalCodebook,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.formal_quotation_term import (
    QuotationTermExample,
    load_quotation_term_examples,
    quote_tokens_as_term,
    validate_quotation_term_examples,
)
from autarkic_systems.formal_substitution import substitute_node
from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_CANDIDATES = Path("claims/fixed_point_equation_candidates.json")
DEFAULT_FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D3.4-GENERIC-CONFIGURATION",
    "W2011-D5.7-SELFCONSK",
    "W2020-D3.2-SELF-JUSTIFYING-GENAC",
)
VALID_CANDIDATE_KIND = "naive-quotation-substitution-candidate"
VALID_CANDIDATE_STATUSES = {
    "candidate-not-fixed",
}
REQUIRED_FUTURE_WORK = (
    "diagonal-construction",
    "fixed-point-equation-proof",
    "self-consistency-theorem",
)


@dataclass(frozen=True)
class FixedPointEquationCandidate:
    """One checked fixed-point equation candidate."""

    candidate_id: str
    target_id: str
    quotation_term_example_id: str
    status: str
    expected_original_code: tuple[int, ...]
    expected_candidate_code_length: int
    expected_candidate_code_prefix: tuple[int, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointEquationManifest:
    """Loaded fixed-point equation candidate manifest."""

    path: Path
    schema_version: int
    candidate_set_id: str
    reviewed_at: str
    purpose: str
    fixed_point_targets_path: str
    quotation_term_examples_path: str
    codebook_path: str
    candidate_kind: str
    willard_anchor_ids: tuple[str, ...]
    candidates: tuple[FixedPointEquationCandidate, ...]


@dataclass(frozen=True)
class FixedPointEquationValidation:
    """One validation result for fixed-point equation candidates."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class CandidateObservation:
    """Observed code facts for one fixed-point equation candidate."""

    candidate_id: str
    target_id: str
    quotation_term_example_id: str
    status: str
    candidate_is_fixed: bool
    original_code: tuple[int, ...]
    candidate_code_length: int
    candidate_code_prefix: tuple[int, ...]


@dataclass(frozen=True)
class FixedPointEquationReport:
    """Validation report for fixed-point equation candidates."""

    manifest: FixedPointEquationManifest
    fixed_point_targets_path: Path
    quotation_term_examples_path: Path
    codebook_path: Path
    formal_language_path: Path
    willard_map_path: Path
    results: tuple[FixedPointEquationValidation, ...]
    observations: tuple[CandidateObservation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every fixed-point equation validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def candidate_count(self) -> int:
        """Return the number of checked candidates."""

        return len(self.manifest.candidates)

    @property
    def failed_subjects(self) -> tuple[str, ...]:
        """Return compact failure subjects for automation and reports."""

        subjects: list[str] = []
        for result in self.results:
            if result.accepted:
                continue
            subject = _failed_subject_for_result(result.subject)
            if subject not in subjects:
                subjects.append(subject)
        return tuple(subjects)


def build_candidate_code(
    *,
    target_id: str,
    quotation_term_example_id: str,
    fixed_point_targets_path: Path | str = "claims/fixed_point_targets.json",
    quotation_term_examples_path: Path | str = "language/formal_quotation_term_examples.json",
    codebook_path: Path | str = "language/formal_codebook.json",
) -> tuple[int, ...]:
    """Build and encode the naive quotation-substitution candidate."""

    fixed_point_targets = load_fixed_point_targets(fixed_point_targets_path)
    quotation_terms = load_quotation_term_examples(quotation_term_examples_path)
    codebook = load_formal_codebook(codebook_path)
    target = _find_target(fixed_point_targets.targets, target_id)
    example = _find_quotation_term_example(
        quotation_terms.examples,
        quotation_term_example_id,
    )
    return _candidate_code_for(target, example, codebook)


def load_fixed_point_equation_candidates(
    path: Path | str = DEFAULT_CANDIDATES,
) -> FixedPointEquationManifest:
    """Load fixed-point equation candidates from JSON."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return FixedPointEquationManifest(
        path=manifest_path,
        schema_version=_required_int(data, "schema_version"),
        candidate_set_id=_required_text(data, "candidate_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        fixed_point_targets_path=_required_text(data, "fixed_point_targets_path"),
        quotation_term_examples_path=_required_text(
            data,
            "quotation_term_examples_path",
        ),
        codebook_path=_required_text(data, "codebook_path"),
        candidate_kind=_required_text(data, "candidate_kind"),
        willard_anchor_ids=tuple(_required_text_list(data, "willard_anchor_ids")),
        candidates=tuple(
            _parse_candidate(item) for item in _required_list(data, "candidates")
        ),
    )


def validate_fixed_point_equation_candidates(
    manifest: FixedPointEquationManifest,
    formal_language_path: Path | str = DEFAULT_FORMAL_LANGUAGE,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointEquationReport:
    """Validate fixed-point equation candidates and their dependencies."""

    checked_language_path = Path(formal_language_path)
    checked_willard_map_path = Path(willard_map_path)
    checked_fixed_point_path = Path(manifest.fixed_point_targets_path)
    checked_quotation_term_path = Path(manifest.quotation_term_examples_path)
    checked_codebook_path = Path(manifest.codebook_path)

    willard_map = load_willard_definition_map(checked_willard_map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}
    fixed_point_targets = load_fixed_point_targets(checked_fixed_point_path)
    fixed_point_report = validate_fixed_point_targets(
        fixed_point_targets,
        checked_willard_map_path,
        checked_language_path,
    )
    quotation_terms = load_quotation_term_examples(checked_quotation_term_path)
    quotation_term_report = validate_quotation_term_examples(
        quotation_terms,
        checked_codebook_path,
        checked_language_path,
        checked_willard_map_path,
    )
    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )

    results: list[FixedPointEquationValidation] = [
        _accepted("manifest", f"loaded {len(manifest.candidates)} candidate(s)")
    ]
    observations: list[CandidateObservation] = []
    results.extend(_validate_references(manifest))
    results.extend(
        _validate_dependency_reports(
            fixed_point_report,
            quotation_term_report,
            codebook_report,
        )
    )
    results.extend(_validate_candidate_kind(manifest))
    results.extend(_validate_willard_anchors(manifest, known_anchor_ids))
    candidate_results, observations = _validate_candidates(
        manifest.candidates,
        fixed_point_targets.targets,
        quotation_terms.examples,
        codebook,
    )
    results.extend(candidate_results)

    return FixedPointEquationReport(
        manifest=manifest,
        fixed_point_targets_path=checked_fixed_point_path,
        quotation_term_examples_path=checked_quotation_term_path,
        codebook_path=checked_codebook_path,
        formal_language_path=checked_language_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        observations=tuple(observations),
    )


def fixed_point_equation_report_payload(
    report: FixedPointEquationReport,
) -> dict[str, Any]:
    """Return a JSON-ready fixed-point equation candidate payload."""

    observations = {observation.candidate_id: observation for observation in report.observations}
    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "candidate_manifest": str(report.manifest.path),
        "candidate_set_id": report.manifest.candidate_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "fixed_point_targets_path": str(report.fixed_point_targets_path),
        "quotation_term_examples_path": str(report.quotation_term_examples_path),
        "codebook_path": str(report.codebook_path),
        "formal_language_path": str(report.formal_language_path),
        "willard_map": str(report.willard_map_path),
        "candidate_kind": report.manifest.candidate_kind,
        "willard_anchor_ids": list(report.manifest.willard_anchor_ids),
        "candidate_count": report.candidate_count,
        "failed_subjects": list(report.failed_subjects),
        "candidates": [
            _candidate_payload(candidate, observations.get(candidate.candidate_id))
            for candidate in report.manifest.candidates
        ],
        "result_count": len(report.results),
        "results": [
            {
                "subject": result.subject,
                "accepted": result.accepted,
                "detail": result.detail,
            }
            for result in report.results
        ],
    }


def format_fixed_point_equation_report(report: FixedPointEquationReport) -> str:
    """Format a concise human-readable fixed-point equation report."""

    observations = {observation.candidate_id: observation for observation in report.observations}
    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point equation candidates: {status}",
        f"Candidate set: {report.manifest.candidate_set_id}",
        f"Candidates: {report.candidate_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for candidate in report.manifest.candidates:
        observation = observations.get(candidate.candidate_id)
        fixed_text = "unknown"
        length_text = "unknown"
        if observation is not None:
            fixed_text = "yes" if observation.candidate_is_fixed else "no"
            length_text = str(observation.candidate_code_length)
        lines.extend([
            f"- {candidate.candidate_id}",
            f"  Target: {candidate.target_id}",
            f"  Status: {candidate.status}",
            f"  Candidate fixed: {fixed_text}",
            f"  Candidate code length: {length_text}",
            "  Future work: " + _joined_or_none(candidate.required_future_work),
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_equation_cli(argv: list[str] | None = None) -> int:
    """Run the fixed-point equation candidate validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.fixed_point_equation",
        description="Validate AS fixed-point equation candidates.",
    )
    parser.add_argument(
        "--candidates",
        default=str(DEFAULT_CANDIDATES),
        help="Path to the fixed-point equation candidate manifest.",
    )
    parser.add_argument(
        "--language",
        default=str(DEFAULT_FORMAL_LANGUAGE),
        help="Path to the formal arithmetic language manifest.",
    )
    parser.add_argument(
        "--willard-map",
        default=str(DEFAULT_WILLARD_MAP),
        help="Path to the Willard definition map.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    manifest = load_fixed_point_equation_candidates(args.candidates)
    report = validate_fixed_point_equation_candidates(
        manifest,
        args.language,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(fixed_point_equation_report_payload(report), sort_keys=True))
    else:
        print(format_fixed_point_equation_report(report))
    return 0 if report.accepted else 1


def _candidate_payload(
    candidate: FixedPointEquationCandidate,
    observation: CandidateObservation | None,
) -> dict[str, Any]:
    payload = {
        "candidate_id": candidate.candidate_id,
        "target_id": candidate.target_id,
        "quotation_term_example_id": candidate.quotation_term_example_id,
        "status": candidate.status,
        "expected_original_code": list(candidate.expected_original_code),
        "expected_candidate_code_length": candidate.expected_candidate_code_length,
        "expected_candidate_code_prefix": list(candidate.expected_candidate_code_prefix),
        "required_future_work": list(candidate.required_future_work),
        "non_claims": list(candidate.non_claims),
        "next_as_action": candidate.next_as_action,
    }
    if observation is None:
        payload.update({
            "candidate_is_fixed": None,
            "observed_candidate_code_length": None,
            "observed_candidate_code_prefix": None,
        })
    else:
        payload.update({
            "candidate_is_fixed": observation.candidate_is_fixed,
            "observed_candidate_code_length": observation.candidate_code_length,
            "observed_candidate_code_prefix": list(observation.candidate_code_prefix),
        })
    return payload


def _validate_references(
    manifest: FixedPointEquationManifest,
) -> list[FixedPointEquationValidation]:
    expected = (
        (
            "fixed_point_targets_path",
            manifest.fixed_point_targets_path,
            "claims/fixed_point_targets.json",
        ),
        (
            "quotation_term_examples_path",
            manifest.quotation_term_examples_path,
            "language/formal_quotation_term_examples.json",
        ),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
    )
    results: list[FixedPointEquationValidation] = []
    for subject, actual, expected_value in expected:
        if actual != expected_value:
            results.append(
                _rejected(subject, f"expected {expected_value} but found {actual}")
            )
        else:
            results.append(_accepted(subject, f"{expected_value} referenced"))
    return results


def _validate_dependency_reports(
    fixed_point_report: Any,
    quotation_term_report: Any,
    codebook_report: Any,
) -> list[FixedPointEquationValidation]:
    checks = (
        ("fixed_point", fixed_point_report, "fixed-point target"),
        ("quotation_term", quotation_term_report, "formal quotation term"),
        ("codebook", codebook_report, "formal codebook"),
    )
    results: list[FixedPointEquationValidation] = []
    for subject, report, label in checks:
        if report.accepted:
            results.append(_accepted(subject, f"{label} accepted"))
        else:
            results.append(
                _rejected(
                    subject,
                    f"{label} rejected: " + _joined_or_none(report.failed_subjects),
                )
            )
    return results


def _validate_candidate_kind(
    manifest: FixedPointEquationManifest,
) -> list[FixedPointEquationValidation]:
    if manifest.candidate_kind == VALID_CANDIDATE_KIND:
        return [_accepted("candidate_kind", VALID_CANDIDATE_KIND)]
    return [
        _rejected(
            "candidate_kind",
            f"unknown candidate kind: {manifest.candidate_kind}",
        )
    ]


def _validate_willard_anchors(
    manifest: FixedPointEquationManifest,
    known_anchor_ids: set[str],
) -> list[FixedPointEquationValidation]:
    unknown_anchor_ids = sorted(set(manifest.willard_anchor_ids) - known_anchor_ids)
    missing_required = sorted(
        set(REQUIRED_WILLARD_ANCHORS) - set(manifest.willard_anchor_ids)
    )
    if unknown_anchor_ids:
        return [
            _rejected(
                "willard_anchors",
                "unknown Willard anchor IDs: " + ", ".join(unknown_anchor_ids),
            )
        ]
    if missing_required:
        return [
            _rejected(
                "willard_anchors",
                "missing required Willard anchors: " + ", ".join(missing_required),
            )
        ]
    return [_accepted("willard_anchors", "required anchors are present and known")]


def _validate_candidates(
    candidates: tuple[FixedPointEquationCandidate, ...],
    targets: tuple[FixedPointTarget, ...],
    quotation_examples: tuple[QuotationTermExample, ...],
    codebook: FormalCodebook,
) -> tuple[list[FixedPointEquationValidation], list[CandidateObservation]]:
    if not candidates:
        return [_rejected("candidates", "no fixed-point equation candidates")], []

    results: list[FixedPointEquationValidation] = []
    observations: list[CandidateObservation] = []
    ids = [candidate.candidate_id for candidate in candidates]
    duplicate_ids = _duplicates(ids)
    if duplicate_ids:
        results.append(
            _rejected("candidates.candidate_id", "duplicate candidate ids: " + ", ".join(duplicate_ids))
        )
    else:
        results.append(_accepted("candidates.candidate_id", "candidate ids are unique"))

    for candidate in candidates:
        candidate_results, observation = _validate_candidate(
            candidate,
            targets,
            quotation_examples,
            codebook,
        )
        results.extend(candidate_results)
        if observation is not None:
            observations.append(observation)
    results.append(_accepted("candidates", f"checked {len(candidates)} candidate(s)"))
    return results, observations


def _validate_candidate(
    candidate: FixedPointEquationCandidate,
    targets: tuple[FixedPointTarget, ...],
    quotation_examples: tuple[QuotationTermExample, ...],
    codebook: FormalCodebook,
) -> tuple[list[FixedPointEquationValidation], CandidateObservation | None]:
    subject = candidate.candidate_id
    results: list[FixedPointEquationValidation] = []

    if candidate.status == "fixed-point-equation-proved":
        results.append(
            _rejected(
                f"{subject}.status",
                "proved fixed-point equations are not supported",
            )
        )
    elif candidate.status not in VALID_CANDIDATE_STATUSES:
        results.append(_rejected(f"{subject}.status", f"unknown status: {candidate.status}"))
    else:
        results.append(_accepted(f"{subject}.status", "candidate status preserves non-claim"))

    missing_future_work = [
        item for item in REQUIRED_FUTURE_WORK if item not in candidate.required_future_work
    ]
    if missing_future_work:
        results.append(
            _rejected(
                f"{subject}.required_future_work",
                "missing future work: " + ", ".join(missing_future_work),
            )
        )
    else:
        results.append(_accepted(f"{subject}.required_future_work", "future work is explicit"))

    if not candidate.non_claims:
        results.append(_rejected(f"{subject}.non_claims", "non-claims must be explicit"))
    else:
        results.append(_accepted(f"{subject}.non_claims", "non-claims are explicit"))

    try:
        target = _find_target(targets, candidate.target_id)
        quotation_example = _find_quotation_term_example(
            quotation_examples,
            candidate.quotation_term_example_id,
        )
        candidate_code = _candidate_code_for(target, quotation_example, codebook)
    except ValueError as exc:
        results.append(_rejected(f"{subject}.candidate", str(exc)))
        return results, None

    observation = CandidateObservation(
        candidate_id=candidate.candidate_id,
        target_id=candidate.target_id,
        quotation_term_example_id=candidate.quotation_term_example_id,
        status=candidate.status,
        candidate_is_fixed=candidate_code == target.expected_instance_code,
        original_code=target.expected_instance_code,
        candidate_code_length=len(candidate_code),
        candidate_code_prefix=candidate_code[: len(candidate.expected_candidate_code_prefix)],
    )

    if candidate.expected_original_code != target.expected_instance_code:
        results.append(
            _rejected(
                f"{subject}.candidate",
                "expected original code mismatch: expected "
                + _format_code(candidate.expected_original_code)
                + " got "
                + _format_code(target.expected_instance_code),
            )
        )
    elif len(candidate_code) != candidate.expected_candidate_code_length:
        results.append(
            _rejected(
                f"{subject}.candidate",
                "candidate code length mismatch: expected "
                + str(candidate.expected_candidate_code_length)
                + " got "
                + str(len(candidate_code)),
            )
        )
    elif candidate_code[: len(candidate.expected_candidate_code_prefix)] != candidate.expected_candidate_code_prefix:
        results.append(
            _rejected(
                f"{subject}.candidate",
                "candidate code prefix mismatch",
            )
        )
    elif candidate.status == "candidate-not-fixed" and observation.candidate_is_fixed:
        results.append(
            _rejected(
                f"{subject}.candidate",
                "candidate unexpectedly satisfies the fixed-point code equation",
            )
        )
    else:
        detail = (
            "naive candidate is not fixed; original code length "
            + str(len(target.expected_instance_code))
            + ", candidate code length "
            + str(len(candidate_code))
        )
        results.append(_accepted(f"{subject}.candidate", detail))

    return results, observation


def _candidate_code_for(
    target: FixedPointTarget,
    quotation_example: QuotationTermExample,
    codebook: FormalCodebook,
) -> tuple[int, ...]:
    quotation_term = quote_tokens_as_term(quotation_example.tokens)
    candidate_instance = substitute_node(
        target.template_node,
        target.template_variable,
        quotation_term,
    )
    return encode_node(candidate_instance, codebook)


def _find_target(
    targets: tuple[FixedPointTarget, ...],
    target_id: str,
) -> FixedPointTarget:
    for target in targets:
        if target.target_id == target_id:
            return target
    raise ValueError(f"unknown fixed-point target: {target_id}")


def _find_quotation_term_example(
    examples: tuple[QuotationTermExample, ...],
    example_id: str,
) -> QuotationTermExample:
    for example in examples:
        if example.example_id == example_id:
            return example
    raise ValueError(f"unknown quotation term example: {example_id}")


def _parse_candidate(item: dict[str, Any]) -> FixedPointEquationCandidate:
    return FixedPointEquationCandidate(
        candidate_id=_required_text(item, "candidate_id"),
        target_id=_required_text(item, "target_id"),
        quotation_term_example_id=_required_text(item, "quotation_term_example_id"),
        status=_required_text(item, "status"),
        expected_original_code=tuple(_required_int_list(item, "expected_original_code")),
        expected_candidate_code_length=_required_int(item, "expected_candidate_code_length"),
        expected_candidate_code_prefix=tuple(_required_int_list(item, "expected_candidate_code_prefix")),
        required_future_work=tuple(_required_text_list(item, "required_future_work")),
        non_claims=tuple(_required_text_list(item, "non_claims")),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "willard_anchors":
        return "fixed-point-equation-willard-anchor"
    if subject.endswith(".status"):
        return "fixed-point-equation-status"
    if subject.endswith(".candidate") or subject.startswith("candidates"):
        return "fixed-point-equation-candidate"
    if subject in {
        "fixed_point",
        "quotation_term",
        "codebook",
        "candidate_kind",
    }:
        return "fixed-point-equation-manifest"
    if subject in {
        "fixed_point_targets_path",
        "quotation_term_examples_path",
        "codebook_path",
    }:
        return "fixed-point-equation-reference"
    if subject.startswith("AS-FIXED-POINT"):
        return "fixed-point-equation-candidate"
    return "fixed-point-equation"


def _required_text(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"required text field missing: {key}")
    return value


def _required_int(item: dict[str, Any], key: str) -> int:
    value = item.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"required integer field missing: {key}")
    return value


def _required_list(item: dict[str, Any], key: str) -> list[Any]:
    value = item.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"required list field missing: {key}")
    return value


def _required_text_list(item: dict[str, Any], key: str) -> list[str]:
    values = _required_list(item, key)
    text_values: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} contains non-text item")
        text_values.append(value)
    return text_values


def _required_int_list(item: dict[str, Any], key: str) -> list[int]:
    value = item.get(key)
    if not isinstance(value, list):
        raise ValueError(f"required integer list missing: {key}")
    result: list[int] = []
    for list_item in value:
        if not isinstance(list_item, int) or isinstance(list_item, bool):
            raise ValueError(f"{key} contains non-integer item")
        result.append(list_item)
    return result


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def _format_code(code: tuple[int, ...]) -> str:
    return "[" + ", ".join(str(item) for item in code) + "]"


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _accepted(subject: str, detail: str) -> FixedPointEquationValidation:
    return FixedPointEquationValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> FixedPointEquationValidation:
    return FixedPointEquationValidation(subject=subject, accepted=False, detail=detail)


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess test.
    raise SystemExit(run_fixed_point_equation_cli())
