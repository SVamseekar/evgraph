"""Thin CLI wrapper over the evgraph Python API.

Per docs/ARCHITECTURE.md's Developer First principle: this module contains no
logic that doesn't already exist in `evgraph`. Each subcommand does argument
parsing and output-format selection only; scanning and reporting are entirely
delegated to `evgraph.scan`/`evgraph.scan_promotion`/`evgraph.scan_dataset_manifest`/
`evgraph.evaluate_gate`/`Report`.
"""

from __future__ import annotations

import argparse
import sys

from evgraph import evaluate_gate, scan, scan_dataset_manifest, scan_promotion
from evgraph_core import AdapterError

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


def _add_gate_arguments(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument(
        "--gate",
        action="store_true",
        help="Return exit code 1 when gate findings should fail a pipeline.",
    )
    subparser.add_argument(
        "--strict",
        action="store_true",
        help="With --gate, also fail on inconclusive findings.",
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
    _add_gate_arguments(scan_parser)

    dataset_parser = subparsers.add_parser(
        "scan-dataset-manifest", help="Scan a dataset manifest CSV."
    )
    dataset_parser.add_argument("manifest_path")
    _add_format_argument(dataset_parser)
    _add_gate_arguments(dataset_parser)

    promotion_parser = subparsers.add_parser(
        "scan-promotion",
        help="Scan promotion evidence (JSON trio and/or MLflow).",
    )
    promotion_parser.add_argument("--model-card", dest="model_card_path")
    promotion_parser.add_argument("--approval", dest="approval_path")
    promotion_parser.add_argument("--deployment", dest="deployment_path")
    promotion_parser.add_argument("--mlflow-uri", dest="mlflow_tracking_uri")
    promotion_parser.add_argument("--model-name", dest="mlflow_model_name")
    promotion_parser.add_argument("--model-version", dest="mlflow_model_version")
    _add_format_argument(promotion_parser)
    _add_gate_arguments(promotion_parser)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.strict and not args.gate:
        print("evgraph: error: --strict requires --gate", file=sys.stderr)
        return 2

    try:
        if args.command == "scan":
            report = scan(args.model_card_path, args.approval_path, args.deployment_path)
        elif args.command == "scan-dataset-manifest":
            report = scan_dataset_manifest(args.manifest_path)
        elif args.command == "scan-promotion":
            report = scan_promotion(
                model_card_path=args.model_card_path,
                approval_path=args.approval_path,
                deployment_path=args.deployment_path,
                mlflow_tracking_uri=args.mlflow_tracking_uri,
                mlflow_model_name=args.mlflow_model_name,
                mlflow_model_version=args.mlflow_model_version,
            )
        else:
            parser.error(f"unknown command: {args.command}")
            return 2
    except (AdapterError, ValueError, ImportError) as exc:
        print(f"evgraph: error: {exc}", file=sys.stderr)
        return 2

    _print_report(report, args.format)
    if args.gate:
        gate = evaluate_gate(report, fail_on_inconclusive=args.strict)
        return 1 if gate.should_fail else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
