"""
Metrics and evaluation module for BhashaSwitch.

Computes:
- Word Error Rate (WER) via jiwer
- Character Error Rate (CER)
- Category-specific error breakdown (numbers, proper nouns/names, negation, code-switches)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any
import jiwer

from bhashaswitch.normalizer import normalize_text


# High-frequency Hindi & English negation markers
NEGATION_WORDS = {
    "no", "not", "never", "none", "neither", "nor", "nothing", "nowhere", "hardly", "barely",
    "नहीं", "ना", "मत", "नाहीं", "कदापि"
}

# Number words / digits regex
NUMBER_REGEX = re.compile(r"\b\d+\b")


@dataclass
class ClipEvaluation:
    """Detailed evaluation result for a single utterance."""

    clip_id: str
    language_category: str  # "hindi", "english", "code_switch"
    reference_raw: str
    hypothesis_raw: str
    reference_norm: str
    hypothesis_norm: str
    wer: float
    cer: float
    substitutions: int
    deletions: int
    insertions: int
    hits: int
    latency_s: float
    has_numbers: bool
    has_negation: bool
    number_error: bool = False
    negation_error: bool = False
    notes: str = ""


def compute_wer_cer(reference: str, hypothesis: str) -> tuple[float, float, dict[str, int]]:
    """Compute WER and CER between normalized strings using jiwer."""
    if not reference.strip() and not hypothesis.strip():
        return 0.0, 0.0, {"substitutions": 0, "deletions": 0, "insertions": 0, "hits": 0}
    
    if not reference.strip() and hypothesis.strip():
        num_hyp_words = len(hypothesis.strip().split())
        return 1.0, 1.0, {"substitutions": 0, "deletions": 0, "insertions": num_hyp_words, "hits": 0}

    # jiwer process_words
    out = jiwer.process_words(reference, hypothesis)
    wer = float(out.wer)
    
    # CER: compute character-level error
    cer_out = jiwer.process_characters(reference, hypothesis)
    cer = float(cer_out.cer)
    
    counts = {
        "substitutions": out.substitutions,
        "deletions": out.deletions,
        "insertions": out.insertions,
        "hits": out.hits,
    }
    return wer, cer, counts


def check_category_errors(reference_norm: str, hypothesis_norm: str) -> tuple[bool, bool, bool, bool]:
    """Check whether numbers or negations exist and whether they were misrecognized.

    Returns:
        (has_numbers, number_error, has_negation, negation_error)
    """
    ref_words = set(reference_norm.split())
    hyp_words = set(hypothesis_norm.split())

    # Numbers
    ref_numbers = set(NUMBER_REGEX.findall(reference_norm))
    hyp_numbers = set(NUMBER_REGEX.findall(hypothesis_norm))
    has_numbers = len(ref_numbers) > 0
    number_error = False
    if has_numbers:
        number_error = ref_numbers != hyp_numbers

    # Negation
    ref_negations = ref_words.intersection(NEGATION_WORDS)
    hyp_negations = hyp_words.intersection(NEGATION_WORDS)
    has_negation = len(ref_negations) > 0
    negation_error = False
    if has_negation:
        negation_error = ref_negations != hyp_negations

    return has_numbers, number_error, has_negation, negation_error


def evaluate_utterance(
    clip_id: str,
    language_category: str,
    reference: str,
    hypothesis: str,
    latency_s: float = 0.0,
    notes: str = "",
) -> ClipEvaluation:
    """Evaluate a single utterance and classify errors."""
    ref_norm = normalize_text(reference)
    hyp_norm = normalize_text(hypothesis)

    wer, cer, counts = compute_wer_cer(ref_norm, hyp_norm)
    has_nums, num_err, has_neg, neg_err = check_category_errors(ref_norm, hyp_norm)

    return ClipEvaluation(
        clip_id=clip_id,
        language_category=language_category,
        reference_raw=reference,
        hypothesis_raw=hypothesis,
        reference_norm=ref_norm,
        hypothesis_norm=hyp_norm,
        wer=wer,
        cer=cer,
        substitutions=counts["substitutions"],
        deletions=counts["deletions"],
        insertions=counts["insertions"],
        hits=counts["hits"],
        latency_s=latency_s,
        has_numbers=has_nums,
        has_negation=has_neg,
        number_error=num_err,
        negation_error=neg_err,
        notes=notes,
    )
