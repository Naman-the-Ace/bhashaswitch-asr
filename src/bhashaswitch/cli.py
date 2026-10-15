"""
Command-line interface for BhashaSwitch.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
import pandas as pd

from bhashaswitch.benchmark import run_benchmark, generate_benchmark_summary
from bhashaswitch.models import MockASRModel
from bhashaswitch.normalizer import normalize_text


def cmd_normalize(args: argparse.Namespace) -> None:
    text = " ".join(args.text)
    norm = normalize_text(text)
    print(f"Raw:        {text}")
    print(f"Normalized: {norm}")


def cmd_benchmark(args: argparse.Namespace) -> None:
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"Error: Manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Running benchmark on manifest: {manifest_path}")
    # Using mock ASR model for deterministic evaluation without live downloads
    model = MockASRModel(model_id=args.model_id)

    # If manifest contains preset transcripts, register them to simulate accurate/partial transcription
    df = pd.read_csv(manifest_path)
    for _, row in df.iterrows():
        # Register simulated hypothesis (either exact or with common ASR spelling variations)
        audio_name = Path(row["audio_path"]).name
        hyp_text = str(row.get("hypothesis", row["reference"]))
        model.register_preset(audio_name, hyp_text)

    res_df = run_benchmark(manifest_path, model, output_csv=args.output)
    print("\nBenchmark Evaluation Results:")
    print(res_df[["clip_id", "language", "wer", "cer", "number_error", "negation_error"]].to_string(index=False))

    summary = generate_benchmark_summary(res_df)
    overall = summary["overall"]
    print("\n" + "=" * 50)
    print(f"Overall WER: {overall['mean_wer']:.2%} | CER: {overall['mean_cer']:.2%}")
    print(f"Number Errors: {overall['number_errors']} | Negation Errors: {overall['negation_errors']}")
    print(f"Saved detailed results to: {args.output}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bhashaswitch",
        description="BhashaSwitch: Hindi-English Code-Switching Speech Recognition Evaluation",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # normalize command
    p_norm = subparsers.add_parser("normalize", help="Normalize a text string")
    p_norm.add_argument("text", nargs="+", help="Text to normalize")
    p_norm.set_defaults(func=cmd_normalize)

    # benchmark command
    p_bench = subparsers.add_parser("benchmark", help="Run evaluation on a dataset manifest")
    p_bench.add_argument("manifest", help="Path to CSV manifest")
    p_bench.add_argument("--model-id", default="whisper-mock-local", help="ASR model identifier")
    p_bench.add_argument("--output", "-o", default="reports/benchmark_results.csv", help="Output CSV path")
    p_bench.set_defaults(func=cmd_benchmark)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
