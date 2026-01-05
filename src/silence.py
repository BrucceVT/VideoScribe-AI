import re
import subprocess
from typing import List, Tuple


def detect_silences_ffmpeg(
    wav_path: str,
    silence_db: int,
    min_silence: float
) -> List[Tuple[float, float]]:
    """
    Detecta silencios usando ffmpeg silencedetect.
    Retorna [(start, end), ...]
    """
    cmd = [
        "ffmpeg", "-hide_banner", "-i", wav_path,
        "-af", f"silencedetect=n={silence_db}dB:d={min_silence}",
        "-f", "null", "-"
    ]
    p = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    log = p.stderr
    silences = []
    start = None

    for line in log.splitlines():
        m_start = re.search(r"silence_start:\s*([0-9.]+)", line)
        if m_start:
            start = float(m_start.group(1))

        m_end = re.search(
            r"silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)",
            line
        )
        if m_end and start is not None:
            end = float(m_end.group(1))
            silences.append((start, end))
            start = None

    return silences


def build_segments_from_silences(
    total_sec: float,
    silences: List[Tuple[float, float]],
    min_segment: float
) -> List[Tuple[float, float]]:
    """
    Convierte silencios en segmentos con audio.
    """
    if total_sec <= 0:
        return [(0.0, 999999.0)]

    segments = []
    cur = 0.0

    for s0, s1 in silences:
        if s0 > cur:
            seg = (cur, s0)
            if (seg[1] - seg[0]) >= min_segment:
                segments.append(seg)
        cur = max(cur, s1)

    if cur < total_sec:
        seg = (cur, total_sec)
        if (seg[1] - seg[0]) >= min_segment:
            segments.append(seg)

    return segments


def build_fixed_segments(
    total_sec: float,
    chunk_sec: float = 20.0
) -> List[Tuple[float, float]]:
    """
    Fallback: segmentación fija por tiempo (MUY importante para música).
    """
    if total_sec <= 0:
        return [(0.0, 999999.0)]

    segments = []
    t = 0.0
    while t < total_sec:
        segments.append((t, min(total_sec, t + chunk_sec)))
        t += chunk_sec

    return segments
