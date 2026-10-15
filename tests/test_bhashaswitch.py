"""
Unit tests for BhashaSwitch normalizer, metrics, and models.
"""

import pytest

from bhashaswitch.normalizer import (
    normalize_devanagari_digits,
    normalize_text,
    normalize_unicode,
)
from bhashaswitch.metrics import (
    compute_wer_cer,
    check_category_errors,
    evaluate_utterance,
)
from bhashaswitch.models import MockASRModel


def test_devanagari_digit_normalization():
    assert normalize_devanagari_digits("१२३४५") == "12345"
    assert normalize_devanagari_digits("ट्रेन नंबर ९८७") == "ट्रेन नंबर 987"


def test_text_normalization_hindi_and_english():
    raw_hi = "नमस्ते दुनिया! क्या हाल है? ।"
    norm_hi = normalize_text(raw_hi)
    assert norm_hi == "नमस्ते दुनिया क्या हाल है"

    raw_en = "Hello, World! This is 100% real."
    norm_en = normalize_text(raw_en)
    assert norm_en == "hello world this is 100% real"


def test_compute_wer_cer_perfect_match():
    ref = "aaj meeting cancel nahi hui hai"
    hyp = "aaj meeting cancel nahi hui hai"
    wer, cer, counts = compute_wer_cer(ref, hyp)
    assert wer == 0.0
    assert cer == 0.0
    assert counts["substitutions"] == 0


def test_compute_wer_substitution():
    ref = "send the report today"
    hyp = "send the report tomorrow"
    wer, cer, counts = compute_wer_cer(ref, hyp)
    assert wer == pytest.approx(0.25, abs=0.01)
    assert counts["substitutions"] == 1


def test_negation_and_number_error_detection():
    # Model dropped the negation 'नहीं'
    ref = "यह काम आज नहीं होगा"
    hyp = "यह काम आज होगा"
    has_num, num_err, has_neg, neg_err = check_category_errors(ref, hyp)
    assert not has_num
    assert has_neg is True
    assert neg_err is True

    # Model misrecognized the number
    ref_num = "flight number 402 is delayed"
    hyp_num = "flight number 405 is delayed"
    has_num, num_err, has_neg, neg_err = check_category_errors(ref_num, hyp_num)
    assert has_num is True
    assert num_err is True
    assert not has_neg


def test_mock_asr_model():
    model = MockASRModel(simulated_delay_s=0.0)
    model.register_preset("clip_1.wav", "कॉल कट मत करना")
    res = model.transcribe("clip_1.wav")
    assert res.text == "कॉल कट मत करना"
    assert res.metadata["simulated"] is True
