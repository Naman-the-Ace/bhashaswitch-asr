"""
ASR model abstraction layer for BhashaSwitch.

Provides a unified interface for speech recognizers with:
- Mock / baseline recognizers (CPU deterministic, zero download, test-ready)
- Local Whisper / Faster-Whisper backends
- Hugging Face pipeline backends
"""

from __future__ import annotations

import abc
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass(frozen=True)
class ASRHypothesis:
    """ASR prediction result for an audio input."""

    text: str
    latency_s: float
    model_id: str
    device: str
    metadata: dict[str, Any] = field(default_factory=dict)


class ASRModel(abc.ABC):
    """Abstract Base Class for ASR backends."""

    def __init__(self, model_id: str, device: str = "cpu") -> None:
        self.model_id = model_id
        self.device = device

    @abc.abstractmethod
    def transcribe(self, audio_path: str | Path, language: str | None = None) -> ASRHypothesis:
        """Transcribe an audio file into text."""
        pass


class MockASRModel(ASRModel):
    """Deterministic Mock ASR model for continuous integration and benchmark validation."""

    def __init__(
        self,
        model_id: str = "mock-asr-v1",
        simulated_delay_s: float = 0.05,
        word_error_injection_rate: float = 0.0,
    ) -> None:
        super().__init__(model_id=model_id, device="cpu")
        self.simulated_delay_s = simulated_delay_s
        self.word_error_injection_rate = word_error_injection_rate
        # Lookup table for known sample audio clips if provided
        self._preset_transcripts: dict[str, str] = {}

    def register_preset(self, audio_filename: str, transcript: str) -> None:
        """Register a canned transcript for an audio filename."""
        self._preset_transcripts[Path(audio_filename).name] = transcript

    def transcribe(self, audio_path: str | Path, language: str | None = None) -> ASRHypothesis:
        start_time = time.perf_counter()
        if self.simulated_delay_s > 0:
            time.sleep(self.simulated_delay_s)

        filename = Path(audio_path).name
        raw_text = self._preset_transcripts.get(filename, "default recognized transcript")

        latency = time.perf_counter() - start_time
        return ASRHypothesis(
            text=raw_text,
            latency_s=latency,
            model_id=self.model_id,
            device=self.device,
            metadata={"simulated": True},
        )
