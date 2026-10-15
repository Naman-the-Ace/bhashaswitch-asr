"""
Text normalization module for Hindi, English, and Code-Switched text.

Handles Unicode normalization (NFC/NFD), Devanagari nukta normalization,
punctuation removal, whitespace trimming, and case standardization.
"""

from __future__ import annotations

import re
import unicodedata


# Common Devanagari punctuation & danda
DEVANAGARI_DANDA = "\u0964"  # ।
DEVANAGARI_DOUBLE_DANDA = "\u0965"  # ॥
NUKTA = "\u093C"

# Devanagari digits to ASCII digits
DEVANAGARI_DIGITS = {
    "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
    "५": "5", "६": "6", "७": "7", "८": "8", "९": "9"
}

# Common English and Hindi punctuation to strip during WER computation
PUNCTUATION_REGEX = re.compile(r"[\.,;:!\?\"\'\(\)\[\]\{\}\-\—\–…/\\।॥]")


def normalize_devanagari_digits(text: str) -> str:
    """Convert Devanagari numerals (०-९) to Arabic numerals (0-9)."""
    for d_char, a_char in DEVANAGARI_DIGITS.items():
        text = text.replace(d_char, a_char)
    return text


def normalize_unicode(text: str, form: str = "NFC") -> str:
    """Normalize text into canonical Unicode form (default NFC)."""
    return unicodedata.normalize(form, text)


def normalize_text(
    text: str,
    lowercase: bool = True,
    remove_punctuation: bool = True,
    normalize_digits: bool = True,
    strip_nukta: bool = False,
) -> str:
    """Normalize Hindi, English, or Code-Switched text for fair ASR evaluation.

    Args:
        text: Raw reference or hypothesis transcript.
        lowercase: Whether to convert Latin characters to lowercase.
        remove_punctuation: Whether to strip commas, periods, dandas, etc.
        normalize_digits: Whether to map Devanagari digits to standard 0-9.
        strip_nukta: Whether to remove Devanagari nukta character (\u093C).

    Returns:
        Clean, token-ready string.
    """
    if not text:
        return ""

    text = normalize_unicode(text, "NFC")

    if lowercase:
        text = text.lower()

    if normalize_digits:
        text = normalize_devanagari_digits(text)

    if strip_nukta:
        text = text.replace(NUKTA, "")

    if remove_punctuation:
        text = PUNCTUATION_REGEX.sub(" ", text)

    # Collapse multiple whitespaces and trim
    text = re.sub(r"\s+", " ", text).strip()
    return text
