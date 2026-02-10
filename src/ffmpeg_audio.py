import os
import json
import subprocess

# Extensiones de audio reconocidas
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac", ".wma", ".opus"}

# Extensiones de video reconocidas
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".wmv", ".flv"}


def is_audio_file(path: str) -> bool:
    """Retorna True si la extensión del archivo es de audio."""
    return os.path.splitext(path)[1].lower() in AUDIO_EXTENSIONS


def is_video_file(path: str) -> bool:
    """Retorna True si la extensión del archivo es de video."""
    return os.path.splitext(path)[1].lower() in VIDEO_EXTENSIONS


def is_supported_file(path: str) -> bool:
    """Retorna True si el archivo es de audio o video soportado."""
    return is_audio_file(path) or is_video_file(path)


def get_media_duration(file_path: str) -> float:
    """
    Obtiene la duración de un archivo de audio o video usando FFprobe.
    Funciona con cualquier formato soportado por FFmpeg.
    """
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        file_path,
    ]
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if r.returncode == 0:
            info = json.loads(r.stdout)
            return float(info.get("format", {}).get("duration", 0))
    except Exception:
        pass
    return 0.0


def convert_to_wav_16k_mono(input_path: str, wav_path: str, normalize: bool):
    """
    Convierte un archivo de audio o video a WAV mono 16kHz.
    Normalización ligera opcional. Requiere ffmpeg instalado.
    """
    af = "loudnorm=I=-16:TP=-1.5:LRA=11" if normalize else None

    cmd = ["ffmpeg", "-y", "-i", input_path, "-vn", "-ac", "1", "-ar", "16000"]
    if af:
        cmd += ["-af", af]
    cmd += ["-f", "wav", wav_path]

    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        raise RuntimeError("FFmpeg falló al procesar el archivo. Verifica que ffmpeg esté instalado y en el PATH.")
