"""Command-line interface for running surface-code experiments.

Examples
--------
    surfacecode run --distance 5 --rounds 5 --p 0.001 --shots 50000
    surfacecode sweep --distances 3,5,7 --p 0.005,0.008,0.01,0.012 --shots 20000
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from .experiment import run_memory_experiment
from .threshold import run_threshold_sweep
from .types import ExperimentConfig


def _parse_int_list(raw: str) -> list[int]:
    return [int(token) for token in raw.split(",") if token.strip()]


def _parse_float_list(raw: str) -> list[float]:
    return [float(token) for token in raw.split(",") if token.strip()]


def _cmd_run(args: argparse.Namespace) -> int:
    config = ExperimentConfig(
        distance=args.distance,
        rounds=args.rounds if args.rounds is not None else args.distance,
        p=args.p,
        shots=args.shots,
        basis=args.basis,
        rotated=not args.unrotated,
        seed=args.seed,
    )
    result = run_memory_experiment(config)
    print(json.dumps(json.loads(result.model_dump_json()), indent=2))
    return 0


def _cmd_sweep(args: argparse.Namespace) -> int:
    result = run_threshold_sweep(
        distances=_parse_int_list(args.distances),
        error_rates=_parse_float_list(args.p),
        rounds=args.rounds,
        shots=args.shots,
        basis=args.basis,
        rotated=not args.unrotated,
        seed=args.seed,
    )
    payload = json.loads(result.model_dump_json())
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        print(f"wrote {len(result.points)} points to {args.output}")
    else:
        print(json.dumps(payload, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="surfacecode", description=__doc__)
    parser.add_argument("--basis", choices=["X", "Z"], default="Z")
    parser.add_argument("--unrotated", action="store_true", help="Use the unrotated layout.")
    parser.add_argument("--seed", type=int, default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run a single memory experiment.")
    run.add_argument("--distance", type=int, required=True)
    run.add_argument("--rounds", type=int, default=None)
    run.add_argument("--p", type=float, required=True)
    run.add_argument("--shots", type=int, default=50_000)
    run.set_defaults(func=_cmd_run)

    sweep = sub.add_parser("sweep", help="Run a distance x p threshold sweep.")
    sweep.add_argument("--distances", type=str, required=True, help="Comma-separated, e.g. 3,5,7")
    sweep.add_argument("--p", type=str, required=True, help="Comma-separated physical rates.")
    sweep.add_argument("--rounds", type=int, default=None)
    sweep.add_argument("--shots", type=int, default=20_000)
    sweep.add_argument("--output", type=str, default=None, help="Optional JSON output path.")
    sweep.set_defaults(func=_cmd_sweep)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
