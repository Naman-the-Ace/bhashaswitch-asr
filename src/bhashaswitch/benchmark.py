"""
Benchmark runner and evaluation harness for BhashaSwitch.

Coordinates dataset loading, model transcription, metrics computation,
and generating summary statistics segmented by language category.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any
import pandas as pd

from bhashaswitch.metrics import ClipEvaluation, evaluate_utterance
from bhashaswitch.models import ASRModel


def run_benchmark(
    manifest_path: str | Path,
    model: ASRModel,
    output_csv: str | Path | None = None,
) -> pd.DataFrame:
    """Run an evaluation benchmark across a dataset manifest."""
    manifest_df = pd.read_csv(manifest_path)
    required = {"clip_id", "audio_path", "reference", "language"}
    if not required.issubset(set(manifest_df.columns)):
        raise ValueError(f"Manifest missing columns: {required - set(manifest_df.columns)}")

    results: list[dict[str, Any]] = []

    for _, row in manifest_df.iterrows():
        clip_id = str(row["clip_id"])
        audio_path = str(row["audio_path"])
        ref_text = str(row["reference"])
        lang = str(row["language"])
        notes = str(row.get("notes", ""))

        hyp = model.transcribe(audio_path, language=lang)
        eval_res = evaluate_utterance(
            clip_id=clip_id,
            language_category=lang,
            reference=ref_text,
            hypothesis=hyp.text,
            latency_s=hyp.latency_s,
            notes=notes,
        )

        results.append({
            "clip_id": eval_res.clip_id,
            "language": eval_res.language_category,
            "reference": eval_res.reference_norm,
            "hypothesis": eval_res.hypothesis_norm,
            "wer": round(eval_res.wer, 4),
            "cer": round(eval_res.cer, 4),
            "substitutions": eval_res.substitutions,
            "deletions": eval_res.deletions,
            "insertions": eval_res.insertions,
            "latency_s": round(eval_res.latency_s, 4),
            "has_numbers": eval_res.has_numbers,
            "number_error": eval_res.number_error,
            "has_negation": eval_res.has_negation,
            "negation_error": eval_res.negation_error,
        })

    res_df = pd.DataFrame(results)
    if output_csv:
        Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
        res_df.to_csv(output_csv, index=False)

    return res_df


def generate_benchmark_summary(res_df: pd.DataFrame) -> dict[str, Any]:
    """Generate aggregate metrics by language condition."""
    grouped = res_df.groupby("language").agg({
        "wer": ["count", "mean"],
        "cer": "mean",
        "latency_s": "mean",
        "number_error": "sum",
        "negation_error": "sum",
    })
    
    summary = {
        "overall": {
            "total_clips": len(res_df),
            "mean_wer": float(res_df["wer"].mean()),
            "mean_cer": float(res_df["cer"].mean()),
            "mean_latency_s": float(res_df["latency_s"].mean()),
            "number_errors": int(res_df["number_error"].sum()),
            "negation_errors": int(res_df["negation_error"].sum()),
        },
        "by_language": grouped.to_dict(),
    }
    return summary
