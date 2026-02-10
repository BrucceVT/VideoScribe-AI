import os
import whisper
from src.ffmpeg_audio import is_audio_file, is_supported_file, AUDIO_EXTENSIONS, VIDEO_EXTENSIONS


def extraer_y_transcribir(ruta_archivo):
    ruta_archivo = ruta_archivo.replace('"', '').replace("'", "").strip()
    es_audio = is_audio_file(ruta_archivo)
    nombre_audio = "temp_audio.mp3"

    try:
        if es_audio:
            print("\n--- 1. Archivo de audio detectado, procesando directamente ---")
            nombre_audio = ruta_archivo
        else:
            print("\n--- 1. Extrayendo audio del video ---")
            from moviepy import VideoFileClip
            with VideoFileClip(ruta_archivo) as video:
                video.audio.write_audiofile(nombre_audio, logger=None)

        # --- Seleccionamos un modelo más potente ---
        # 'base' < 'small' < 'medium' < 'large'
        # 'medium' es excelente para español latino.
        print("\n--- 2. Cargando modelo Whisper MEDIUM (Más preciso) ---")
        model = whisper.load_model("medium")

        print("--- 3. Transcribiendo en Español Latino... ---")
        resultado = model.transcribe(
            nombre_audio,
            language="es",   # Forzar español
            fp16=False       # Evita el error/aviso de CPU
        )

        nombre_txt = os.path.splitext(ruta_archivo)[0] + ".txt"
        with open(nombre_txt, "w", encoding="utf-8") as f:
            f.write(resultado["text"])

        print(f"\n✅ ¡Listo! Transcripción mejorada en: {nombre_txt}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Solo borrar el temp si fue extraído de un video
        if not es_audio and os.path.exists(nombre_audio):
            os.remove(nombre_audio)


if __name__ == "__main__":
    ext_list = ", ".join(sorted(e.upper().replace(".", "") for e in AUDIO_EXTENSIONS | VIDEO_EXTENSIONS))
    print("--- TRANSCRIPTOR PRO (ESPAÑOL) ---")
    print(f"    Formatos soportados: {ext_list}")
    archivo = input("Arrastra el archivo aquí: ")

    archivo = archivo.strip().replace('"', '').replace("'", "")
    if not is_supported_file(archivo):
        ext = os.path.splitext(archivo)[1]
        print(f"❌ Formato no soportado: {ext}")
        print(f"   Formatos válidos: {ext_list}")
    else:
        extraer_y_transcribir(archivo)