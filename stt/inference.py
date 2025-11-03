from __future__ import annotations

import os
import numpy as np
import librosa
import torch
from django.conf import settings
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor


_MODEL: Wav2Vec2ForCTC | None = None
_PROCESSOR: Wav2Vec2Processor | None = None


def load_asr_model() -> tuple[Wav2Vec2Processor, Wav2Vec2ForCTC]:
    global _MODEL, _PROCESSOR
    if _MODEL is not None and _PROCESSOR is not None:
        return _PROCESSOR, _MODEL

    model_dir = getattr(settings, "ASR_MODEL_DIR", None)
    if not model_dir or not os.path.isdir(model_dir):
        raise RuntimeError(f"ASR model directory not found: {model_dir}")

    _PROCESSOR = Wav2Vec2Processor.from_pretrained(model_dir)
    _MODEL = Wav2Vec2ForCTC.from_pretrained(model_dir)
    _MODEL.eval()
    return _PROCESSOR, _MODEL


def transcribe_wav_file(path: str, target_sr: int = 16000) -> str:
    processor, model = load_asr_model()

    audio, sr = librosa.load(path, sr=target_sr, mono=True)
    input_values = processor(audio, sampling_rate=target_sr, return_tensors="pt").input_values

    with torch.no_grad():
        logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)[0]
    return transcription

