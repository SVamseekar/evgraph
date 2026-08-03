"""Thin CLI wrapper over the evgraph Python API.

Per docs/ARCHITECTURE.md's Developer First principle: this module contains no
logic that doesn't already exist in `evgraph`. Each subcommand does argument
parsing and output-format selection only; scanning and reporting are entirely
delegated to `evgraph.scan`/`evgraph.scan_dataset_manifest`/`Report`.
"""

from __future__ import annotations

import argparse
import sys

from evgraph import scan, scan_dataset_manifest

_FORMAT_TO_METHOD = {
    "json": "to_json",
    "markdown": "to_markdown",
    "sarif": "to_sarif",
    "oscal": "to_oscal_assessment_results",
}


def _print_report(report, output_format: str) -> None:
    method_name = _FORMAT_TO_METHOD[output_format]
    method = getattr(report, method_name)
    print(method())


def _add_format_argument(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument(
        "--format",
        choices=sorted(_FORMAT_TO_METHOD),
        default="json",
        help="Output format (default: json)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="evgraph")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser(
        "scan", help="Scan a Model Card, approval record, and deployment record."
    )
    scan_parser.add_argument("model_card_path")
    scan_parser.add_argument("approval_path")
    scan_parser.add_argument("deployment_path")
    _add_format_argument(scan_parser)

    dataset_parser = subparsers.add_parser(
        "scan-dataset-manifest", help="Scan a dataset manifest CSV."
    )
    dataset_parser.add_argument("manifest_path")
    _add_format_argument(dataset_parser)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        report = scan(args.model_card_path, args.approval_path, args.deployment_path)
    elif args.command == "scan-dataset-manifest":
        report = scan_dataset_manifest(args.manifest_path)
    else:
        parser.error(f"unknown command: {args.command}")
        return 2

    _print_report(report, args.format)
    return 0


if __name__ == "__main__":
    sys.exit(main())
