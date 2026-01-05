import sys
import subprocess
import shutil
import uuid
from pathlib import Path
from typing import Optional


def separate_vocals_demucs(
    input_wav: str,
    out_root: str = "demucs_out",
    model_name: str = "htdemucs",
    device: str = "cpu",
    mp3_bitrate: int = 256,
) -> tuple[str, str]:
    """
    Ejecuta Demucs y retorna:
      (ruta_a_vocals_mp3, carpeta_run_dir)

    - Usamos --mp3 para evitar guardado WAV vía torchaudio/torchcodec en Windows.
    - Requiere ffmpeg en PATH.
    - out_root se usa como raíz, pero cada ejecución crea un subfolder único.
    """
    input_path = Path(input_wav)
    if not input_path.exists():
        raise RuntimeError(f"No existe el archivo de entrada: {input_wav}")

    out_root_path = Path(out_root)
    out_root_path.mkdir(parents=True, exist_ok=True)

    # Carpeta única por ejecución (evita colisiones y facilita limpieza)
    run_id = uuid.uuid4().hex[:10]
    run_dir = out_root_path / f"run_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "demucs",
        "-n", model_name,
        "--two-stems=vocals",
        "-d", device,
        "--mp3",
        "--mp3-bitrate", str(mp3_bitrate),
        "--filename", "{stem}.{ext}",
        "-o", str(run_dir),
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

    # Salida típica: <run_dir>/<model_name>/<stem>/vocals.mp3
    vocals_mp3 = run_dir / model_name / stem / "vocals.mp3"
    if vocals_mp3.exists():
        return str(vocals_mp3), str(run_dir)

    # Búsqueda defensiva
    candidates = list((run_dir / model_name).glob("**/vocals.mp3"))
    if candidates:
        return str(candidates[0]), str(run_dir)

    raise RuntimeError(
        "Demucs terminó sin error, pero no se encontró vocals.mp3. "
        f"Revisa: {run_dir / model_name}"
    )


def cleanup_demucs_artifacts(run_dir: Optional[str]) -> None:
    """
    Borra la carpeta temporal de Demucs (run_dir).
    Llamar en finally() para evitar acumulación en servidor.
    """
    if not run_dir:
        return
    p = Path(run_dir)
    if p.exists() and p.is_dir():
        shutil.rmtree(p, ignore_errors=True)
