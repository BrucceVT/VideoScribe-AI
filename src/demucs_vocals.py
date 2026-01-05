import sys
import subprocess
from pathlib import Path


def separate_vocals_demucs(
    input_wav: str,
    out_dir: str = "demucs_out",
    model_name: str = "htdemucs",
    device: str = "cpu",
    mp3_bitrate: int = 256,
) -> str:
    """
    Ejecuta Demucs y retorna la ruta a vocals.mp3.
    Usamos --mp3 para evitar el guardado WAV vía torchaudio/torchcodec en Windows.
    Requiere ffmpeg en PATH (ya lo tienes).
    """
    input_path = Path(input_wav)
    if not input_path.exists():
        raise RuntimeError(f"No existe el archivo de entrada: {input_wav}")

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "demucs",
        "-n", model_name,
        "--two-stems=vocals",
        "-d", device,
        "--mp3",
        "--mp3-bitrate", str(mp3_bitrate),
        "--filename", "{stem}.{ext}",
        "-o", str(out_path),
        str(input_path),
    ]

    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if r.returncode != 0:
        err_tail = (r.stderr or "").strip()
        out_tail = (r.stdout or "").strip()
        raise RuntimeError(
            "Demucs falló separando la voz.\n\n"
            f"Comando:\n{' '.join(cmd)}\n\n"
            f"STDOUT:\n{out_tail[-1500:]}\n\n"
            f"STDERR:\n{err_tail[-2000:]}\n"
        )

    stem = input_path.stem

    # Salida típica: demucs_out/htdemucs/<stem>/vocals.mp3
    vocals_mp3 = out_path / model_name / stem / "vocals.mp3"
    if vocals_mp3.exists():
        return str(vocals_mp3)

    # Búsqueda defensiva
    candidates = list((out_path / model_name).glob("**/vocals.mp3"))
    if candidates:
        return str(candidates[0])

    raise RuntimeError(
        "Demucs terminó sin error, pero no se encontró vocals.mp3. "
        f"Revisa: {out_path / model_name}"
    )
