"""Fail-closed unittest suite selection for Autarkic Systems.

The project uses plain stdlib ``unittest`` as its executable evidence harness.
ADR-0272 adds only a small selection layer over that harness: operators can
run the default fast suite, the explicit extended fixed-point suite, or the
complete discovered suite without changing existing tests or validators.
"""

from __future__ import annotations

import argparse
import json
import sys
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TESTS_ROOT = PROJECT_ROOT / "tests"
DEFAULT_MANIFEST_PATH = DEFAULT_TESTS_ROOT / "suite_manifest.json"
EXPECTED_LEAF_SUITES = frozenset({"fast", "extended-fixed-point"})
EXPECTED_AGGREGATE_SUITES = frozenset({"all"})
SELECTABLE_SUITES = ("fast", "extended-fixed-point", "all")
LIST_FORMATS = ("text", "json")
SUITE_INDEX_SCHEMA_VERSION = 1


class SuiteManifestError(ValueError):
    """Raised when the manifest cannot safely select a test suite."""


@dataclass(frozen=True)
class SuiteManifest:
    """Structured wrapper around the checked suite-selection manifest."""

    path: Path
    schema_version: int
    manifest_id: str
    leaf_suites: Mapping[str, Mapping[str, Any]]
    aggregate_suites: Mapping[str, Mapping[str, Any]]
    rationale: tuple[str, ...]
    non_goals: tuple[str, ...]


@dataclass(frozen=True)
class SuitePlan:
    """Validated module selections derived from live discovery."""

    manifest_id: str
    manifest_schema_version: int
    discovered_modules: tuple[str, ...]
    leaf_suites: Mapping[str, tuple[str, ...]]
    aggregate_suites: Mapping[str, tuple[str, ...]]

    def selected_modules(self, suite_name: str) -> tuple[str, ...]:
        """Return the validated module list for one selectable suite."""

        if suite_name in self.leaf_suites:
            return self.leaf_suites[suite_name]
        if suite_name in self.aggregate_suites:
            return self.aggregate_suites[suite_name]
        raise SuiteManifestError(f"unknown suite: {suite_name}")


def _as_object(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise SuiteManifestError(f"{field_name} must be an object")
    return value


def _as_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise SuiteManifestError(f"{field_name} must be a non-empty string")
    return value


def _as_string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise SuiteManifestError(f"{field_name} must be a list")
    strings = tuple(_as_string(item, f"{field_name}[]") for item in value)
    if len(strings) != len(set(strings)):
        raise SuiteManifestError(f"{field_name} must not contain duplicates")
    return strings


def load_suite_manifest(path: Path | str = DEFAULT_MANIFEST_PATH) -> SuiteManifest:
    """Load and structurally validate the suite manifest.

    Discovery-sensitive checks are deliberately left to ``build_suite_plan``.
    Keeping the two phases separate lets tests mutate a structurally valid
    manifest and prove that stale or overlapping suite selections fail at the
    point where live repository discovery is known.
    """

    manifest_path = Path(path)
    if not manifest_path.exists():
        raise SuiteManifestError(f"suite manifest not found: {manifest_path}")

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SuiteManifestError(
            f"suite manifest is not valid JSON: {manifest_path}: {error}"
        ) from error

    top = _as_object(data, "manifest")
    schema_version = top.get("schema_version")
    if schema_version != 1:
        raise SuiteManifestError("schema_version must be 1")

    manifest_id = _as_string(top.get("manifest_id"), "manifest_id")
    leaf_suites = _as_object(top.get("leaf_suites"), "leaf_suites")
    aggregate_suites = _as_object(top.get("aggregate_suites"), "aggregate_suites")
    rationale = _as_string_tuple(top.get("rationale"), "rationale")
    non_goals = _as_string_tuple(top.get("non_goals"), "non_goals")

    if set(leaf_suites) != EXPECTED_LEAF_SUITES:
        raise SuiteManifestError(
            "leaf_suites must contain exactly fast and extended-fixed-point"
        )
    if set(aggregate_suites) != EXPECTED_AGGREGATE_SUITES:
        raise SuiteManifestError("aggregate_suites must contain exactly all")

    for suite_name, definition in leaf_suites.items():
        suite = _as_object(definition, f"leaf_suites.{suite_name}")
        kind = _as_string(suite.get("kind"), f"leaf_suites.{suite_name}.kind")
        _as_string(suite.get("description"), f"leaf_suites.{suite_name}.description")
        if kind == "explicit":
            modules = _as_string_tuple(
                suite.get("modules"),
                f"leaf_suites.{suite_name}.modules",
            )
            for module_name in modules:
                if not module_name.startswith("tests.test_"):
                    raise SuiteManifestError(
                        f"{suite_name} contains non-test module {module_name}"
                    )
        elif kind == "discovered-minus":
            _as_string_tuple(
                suite.get("exclude_suites"),
                f"leaf_suites.{suite_name}.exclude_suites",
            )
        else:
            raise SuiteManifestError(f"{suite_name} has unsupported kind: {kind}")

    all_suite = _as_object(aggregate_suites["all"], "aggregate_suites.all")
    if _as_string(all_suite.get("kind"), "aggregate_suites.all.kind") != "union":
        raise SuiteManifestError("aggregate_suites.all.kind must be union")
    _as_string(all_suite.get("description"), "aggregate_suites.all.description")
    _as_string_tuple(all_suite.get("suites"), "aggregate_suites.all.suites")

    return SuiteManifest(
        path=manifest_path,
        schema_version=schema_version,
        manifest_id=manifest_id,
        leaf_suites=leaf_suites,
        aggregate_suites=aggregate_suites,
        rationale=rationale,
        non_goals=non_goals,
    )


def discover_test_modules(tests_root: Path | str = DEFAULT_TESTS_ROOT) -> tuple[str, ...]:
    """Discover top-level ``tests/test_*.py`` modules as unittest names."""

    root = Path(tests_root)
    if not root.exists():
        raise SuiteManifestError(f"tests root not found: {root}")
    if not root.is_dir():
        raise SuiteManifestError(f"tests root is not a directory: {root}")

    module_names = tuple(
        sorted(f"{root.name}.{path.stem}" for path in root.glob("test_*.py"))
    )
    if not module_names:
        raise SuiteManifestError(f"no unittest modules discovered under {root}")
    return module_names


def _require_unique_discovery(discovered_modules: Sequence[str]) -> tuple[str, ...]:
    discovered = tuple(sorted(discovered_modules))
    if len(discovered) != len(set(discovered)):
        raise SuiteManifestError("discovered test modules contain duplicates")
    return discovered


def _build_explicit_leaf(
    suite_name: str,
    definition: Mapping[str, Any],
    discovered: frozenset[str],
) -> tuple[str, ...]:
    modules = tuple(definition["modules"])
    stale_modules = sorted(module for module in modules if module not in discovered)
    if stale_modules:
        raise SuiteManifestError(
            f"{suite_name} module(s) not discovered: {', '.join(stale_modules)}"
        )
    return tuple(sorted(modules))


def _build_discovered_minus_leaf(
    suite_name: str,
    definition: Mapping[str, Any],
    discovered: frozenset[str],
    leaf_suites: Mapping[str, tuple[str, ...]],
) -> tuple[str, ...]:
    excluded: set[str] = set()
    for excluded_suite in definition["exclude_suites"]:
        if excluded_suite not in leaf_suites:
            raise SuiteManifestError(
                f"{suite_name} excludes unknown or unavailable suite {excluded_suite}"
            )
        excluded.update(leaf_suites[excluded_suite])
    return tuple(sorted(discovered - excluded))


def _assert_leaf_partition(
    discovered: tuple[str, ...],
    leaf_suites: Mapping[str, tuple[str, ...]],
) -> None:
    """Fail unless every discovered module has exactly one leaf-suite owner.

    This is the selector's core invariant. The manifest is allowed to be partly
    hand-maintained, but the resulting leaf suites may not silently drop a
    discovered module or run a module twice through two different leaves.
    """

    owners = {module_name: [] for module_name in discovered}
    for suite_name, module_names in leaf_suites.items():
        for module_name in module_names:
            if module_name not in owners:
                raise SuiteManifestError(
                    f"{suite_name} contains undiscovered module {module_name}"
                )
            owners[module_name].append(suite_name)

    missing = sorted(
        module_name for module_name, suite_names in owners.items() if not suite_names
    )
    duplicated = sorted(
        (module_name, suite_names)
        for module_name, suite_names in owners.items()
        if len(suite_names) > 1
    )

    if missing:
        raise SuiteManifestError(
            "module(s) not classified by any leaf suite: " + ", ".join(missing)
        )
    if duplicated:
        first_module, suite_names = duplicated[0]
        raise SuiteManifestError(
            f"{first_module} classified more than once: {', '.join(suite_names)}"
        )


def build_suite_plan(
    manifest: SuiteManifest,
    discovered_modules: Sequence[str],
) -> SuitePlan:
    """Derive a validated selection plan from the manifest and discovery."""

    discovered = _require_unique_discovery(discovered_modules)
    discovered_set = frozenset(discovered)
    leaf_suites: dict[str, tuple[str, ...]] = {}

    # Explicit leaves are evaluated before discovered-minus leaves so the fast
    # suite can be a live complement of the extended fixed-point list.
    for suite_name, definition in manifest.leaf_suites.items():
        if definition["kind"] == "explicit":
            leaf_suites[suite_name] = _build_explicit_leaf(
                suite_name,
                definition,
                discovered_set,
            )

    for suite_name, definition in manifest.leaf_suites.items():
        if definition["kind"] == "discovered-minus":
            leaf_suites[suite_name] = _build_discovered_minus_leaf(
                suite_name,
                definition,
                discovered_set,
                leaf_suites,
            )

    _assert_leaf_partition(discovered, leaf_suites)

    aggregate_suites: dict[str, tuple[str, ...]] = {}
    for suite_name, definition in manifest.aggregate_suites.items():
        if definition["kind"] != "union":
            raise SuiteManifestError(f"{suite_name} has unsupported kind")
        selected: set[str] = set()
        for leaf_name in definition["suites"]:
            if leaf_name not in leaf_suites:
                raise SuiteManifestError(
                    f"{suite_name} references unknown leaf suite {leaf_name}"
                )
            selected.update(leaf_suites[leaf_name])
        aggregate_suites[suite_name] = tuple(sorted(selected))

    if set(aggregate_suites["all"]) != discovered_set:
        raise SuiteManifestError("all suite must be the union of discovered modules")

    return SuitePlan(
        manifest_id=manifest.manifest_id,
        manifest_schema_version=manifest.schema_version,
        discovered_modules=discovered,
        leaf_suites=leaf_suites,
        aggregate_suites=aggregate_suites,
    )


def build_suite_list_payload(plan: SuitePlan, suite_name: str) -> Mapping[str, Any]:
    """Return the machine-readable list payload for one validated suite."""

    module_names = plan.selected_modules(suite_name)
    unittest_argv = ["python", "-m", "unittest", *module_names]
    return {
        "manifest_id": plan.manifest_id,
        "manifest_schema_version": plan.manifest_schema_version,
        "suite": suite_name,
        "module_count": len(module_names),
        "modules": list(module_names),
        "discovered_module_count": len(plan.discovered_modules),
        "command": {
            "program": "python",
            "module": "unittest",
            "argv": unittest_argv,
            "module_count": len(module_names),
        },
    }


def build_suite_index_payload(plan: SuitePlan) -> Mapping[str, Any]:
    """Return one machine-readable index for every selectable suite.

    The index deliberately embeds the same per-suite payload used by ADR-0293
    JSON list mode. That keeps automation from reconciling two subtly
    different suite descriptions, while the top-level fields expose the
    manifest and discovery facts shared by the whole checked plan.
    """

    return {
        "manifest_id": plan.manifest_id,
        "manifest_schema_version": plan.manifest_schema_version,
        "index_schema_version": SUITE_INDEX_SCHEMA_VERSION,
        "discovered_module_count": len(plan.discovered_modules),
        "selectable_suites": list(SELECTABLE_SUITES),
        "suites": {
            suite_name: build_suite_list_payload(plan, suite_name)
            for suite_name in SELECTABLE_SUITES
        },
    }


def format_suite_list(
    plan: SuitePlan,
    suite_name: str,
    stream: IO[str],
) -> None:
    """Print a stable human-readable module list for one suite."""

    module_names = plan.selected_modules(suite_name)
    print(f"manifest: {plan.manifest_id}", file=stream)
    print(f"suite: {suite_name}", file=stream)
    print(f"module_count: {len(module_names)}", file=stream)
    print("modules:", file=stream)
    for module_name in module_names:
        print(f"- {module_name}", file=stream)


def format_suite_list_json(
    plan: SuitePlan,
    suite_name: str,
    stream: IO[str],
) -> None:
    """Print a stable JSON module list for one validated suite."""

    payload = build_suite_list_payload(plan, suite_name)
    json.dump(payload, stream, indent=2)
    print(file=stream)


def format_suite_index_json(plan: SuitePlan, stream: IO[str]) -> None:
    """Print the validated all-suite index as stable JSON."""

    payload = build_suite_index_payload(plan)
    json.dump(payload, stream, indent=2)
    print(file=stream)


def run_selected_modules(
    module_names: Sequence[str],
    *,
    loader: unittest.TestLoader = unittest.defaultTestLoader,
    runner_factory: Any = unittest.TextTestRunner,
    stream: IO[str],
) -> int:
    """Load selected modules by name and run them through stdlib unittest."""

    suite = loader.loadTestsFromNames(list(module_names))
    runner = runner_factory(stream=stream, verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Select and run Autarkic Systems unittest suites.",
    )
    parser.add_argument(
        "--suite",
        choices=SELECTABLE_SUITES,
        default="fast",
        help="suite to list or run",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list selected modules without running unittest",
    )
    parser.add_argument(
        "--list-suites",
        action="store_true",
        help="emit the machine-readable index of all selectable suites",
    )
    parser.add_argument(
        "--format",
        choices=LIST_FORMATS,
        default="text",
        help="output format for --list or --list-suites",
    )
    return parser


def run_cli(
    argv: Sequence[str] | None = None,
    *,
    stdout: IO[str] = sys.stdout,
    stderr: IO[str] = sys.stderr,
    loader: unittest.TestLoader = unittest.defaultTestLoader,
    runner_factory: Any = unittest.TextTestRunner,
    manifest_path: Path | str = DEFAULT_MANIFEST_PATH,
    tests_root: Path | str = DEFAULT_TESTS_ROOT,
) -> int:
    """Entry point used by both ``python -m`` and the focused unit tests."""

    parser = _build_argument_parser()
    args = parser.parse_args(argv)

    try:
        manifest = load_suite_manifest(manifest_path)
        discovered = discover_test_modules(tests_root)
        plan = build_suite_plan(manifest, discovered)
    except SuiteManifestError as error:
        print(f"error: {error}", file=stderr)
        return 2

    if args.list_suites:
        if args.format != "json":
            print("error: --list-suites requires --format json", file=stderr)
            return 2
        format_suite_index_json(plan, stdout)
        return 0

    module_names = plan.selected_modules(args.suite)

    if args.list:
        if args.format == "json":
            format_suite_list_json(plan, args.suite, stdout)
        else:
            format_suite_list(plan, args.suite, stdout)
        return 0

    print(
        f"manifest: {plan.manifest_id} suite: {args.suite} "
        f"module_count: {len(module_names)}",
        file=stdout,
    )
    return run_selected_modules(
        module_names,
        loader=loader,
        runner_factory=runner_factory,
        stream=stderr,
    )


def main(argv: Sequence[str] | None = None) -> int:
    return run_cli(argv)


if __name__ == "__main__":
    raise SystemExit(main())
