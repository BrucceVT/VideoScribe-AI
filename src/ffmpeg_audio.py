import subprocess
from moviepy import VideoFileClip


def get_video_duration(video_path: str) -> float:
    with VideoFileClip(video_path) as clip:
        if clip.duration:
            return float(clip.duration)
    return 0.0


def extract_wav_16k_mono(video_path: str, wav_path: str, normalize: bool):
    """
    Extrae audio a WAV mono 16kHz. Normalización ligera opcional.
    Requiere ffmpeg instalado.
    """
    af = "loudnorm=I=-16:TP=-1.5:LRA=11" if normalize else None

    cmd = ["ffmpeg", "-y", "-i", video_path, "-vn", "-ac", "1", "-ar", "16000"]
    if af:
        cmd += ["-af", af]
    cmd += ["-f", "wav", wav_path]

    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        raise RuntimeError("FFmpeg falló al extraer audio. Verifica que ffmpeg esté instalado y en el PATH.")
