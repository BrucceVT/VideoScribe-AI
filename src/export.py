import os
from datetime import datetime


def build_transcript_file(
    transcript: str,
    *,
    source_filename: str,
    service_name: str,
    model_label: str,
    model_key: str,
    audio_profile: str,
    precision: str,
    language_label: str,
    duration_sec: float,
    silence_db: int,
    min_silence: float,
    min_segment: float,
    segments_count: int,
) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = [
        f"{service_name} — Transcripción",
        f"Fecha: {ts}",
        f"Archivo: {source_filename}",
        f"Idioma (seleccionado): {language_label}",
        f"Modelo: {model_label} ({model_key})",
        f"Perfil de audio: {audio_profile}",
        f"Precisión: {precision}",
        f"Segmentación: silencios (umbral {silence_db} dB, min_sil {min_silence}s, min_seg {min_segment}s)",
        f"Segmentos generados: {segments_count}",
        "-" * 60,
        "",
    ]
    return "\n".join(header) + transcript.strip() + "\n"


def make_download_name(original_filename: str, service_name: str, settings: dict) -> str:
    base = os.path.splitext(original_filename)[0]
    # Nombre útil y trazable
    model_key = settings["model_key"]
    # compactamos perfil/precisión para filename
    perfil = "voz" if "Voz" in settings["audio_profile"] else "musica"
    prec = "rapido" if settings["precision"] == "Rápido" else ("equilibrado" if settings["precision"] == "Equilibrado" else "max")
    return f"{base}_{service_name}_{model_key}_{perfil}_{prec}.txt"
