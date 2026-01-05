import time
from typing import Dict, Tuple, List

import streamlit as st
import whisper

from .silence import (
    detect_silences_ffmpeg,
    build_segments_from_silences,
    build_fixed_segments,
)


@st.cache_resource
def load_model_cached(model_name: str):
    return whisper.load_model(model_name)


def build_decode_kwargs(settings: Dict) -> Dict:
    precision = settings["precision"]
    audio_profile = settings["audio_profile"]
    lang_code = settings["language_code"]

    is_music = "Música" in audio_profile

    # Base común: evitar “arrastre” de texto entre segmentos
    kwargs: Dict = {
        "task": "transcribe",
        "fp16": False,
        "language": lang_code,
        "condition_on_previous_text": False,
        # thresholds: más permisivos en música para NO perder frases
        "compression_ratio_threshold": 2.6,
        "logprob_threshold": -1.2 if is_music else -1.0,
        "no_speech_threshold": 0.35 if is_music else 0.6,
    }

    # Decode: optimizado para tiempo/calidad (sobre todo en medium)
    if precision == "Rápido":
        kwargs.update({"temperature": 0.0, "beam_size": 1, "best_of": 1})
    elif precision == "Equilibrado":
        kwargs.update({"temperature": 0.0, "beam_size": 5, "best_of": 2})
    else:
        # Máxima precisión
        if is_music:
            # IMPORTANTE: para música, 0.0 suele ser mejor y evita “inventos”
            kwargs.update({"temperature": 0.0, "beam_size": 5, "best_of": 3})
        else:
            kwargs.update({"temperature": 0.2, "beam_size": 7, "best_of": 5})

    return kwargs


def _segments_total_audio_sec(segments: List[Tuple[float, float]]) -> float:
    return max(0.01, sum(max(0.0, e - s) for s, e in segments))


def transcribe_with_silence_segments(
    model,
    wav_path: str,
    duration_sec: float,
    settings: Dict
) -> Tuple[str, Dict]:
    decode_kwargs = build_decode_kwargs(settings)
    audio_profile = settings["audio_profile"]
    is_music = "Música" in audio_profile

    silences = detect_silences_ffmpeg(
        wav_path,
        settings["silence_db"],
        settings["min_silence"],
    )

    segments = build_segments_from_silences(
        duration_sec,
        silences,
        settings["min_segment"],
    )

    # Si hay demasiados cortes (pasa en música), reduce cantidad de llamadas:
    # fallback a chunks fijos de 22s si hay más de 18 segmentos.
    if len(segments) > 18 and duration_sec > 0:
        segments = build_fixed_segments(duration_sec, chunk_sec=22.0)

    if len(segments) <= 1:
        chunk = 20.0
        segments = build_fixed_segments(duration_sec, chunk_sec=chunk)

    # Overlap pequeño (reduce cortes, pero no dispara costo)
    overlap_sec = 0.15 if is_music else 0.10

    audio = whisper.load_audio(wav_path)
    sr = 16000

    total_audio_sec = _segments_total_audio_sec(segments)
    progress = st.progress(0)
    status = st.empty()
    eta_box = st.empty()

    texts: List[str] = []
    processed = 0.0
    rtf = None

    for i, (s, e) in enumerate(segments, start=1):
        s2 = max(0.0, s - overlap_sec)
        e2 = min(duration_sec, e + overlap_sec) if duration_sec > 0 else e + overlap_sec

        status.info(f"Transcribiendo segmento {i}/{len(segments)}")

        start_sample = int(s2 * sr)
        end_sample = int(e2 * sr)
        chunk = audio[start_sample:end_sample]
        chunk_dur = max(0.01, (end_sample - start_sample) / sr)

        if rtf is not None:
            remaining = max(0.0, total_audio_sec - processed)
            eta_box.info(f"Tiempo estimado restante: ~{int(remaining * rtf)}s")

        t0 = time.time()
        res = model.transcribe(chunk, **decode_kwargs)
        t1 = time.time()

        txt = (res.get("text") or "").strip()
        if txt:
            texts.append(txt)

        wall = max(0.001, t1 - t0)
        if rtf is None:
            rtf = min(max(wall / chunk_dur, 0.4), 12.0)

        processed += max(0.0, (e - s))
        progress.progress(int(min(1.0, processed / total_audio_sec) * 100))

    status.success("Transcripción completada.")
    eta_box.empty()

    stats = {
        "segments_count": len(segments),
        "silence_db": settings["silence_db"],
        "min_silence": settings["min_silence"],
        "min_segment": settings["min_segment"],
        "rtf": rtf or 0.0,
    }
    return "\n".join(texts).strip(), stats
