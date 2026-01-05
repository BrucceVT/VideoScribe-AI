import os
import streamlit as st

from src.config import SERVICE_NAME
from src.ui import (
    render_header,
    sidebar_settings,
    render_file_info,
    show_step,
    working_line,
    fmt_time,
)
from src.ffmpeg_audio import extract_wav_16k_mono, get_video_duration
from src.transcriber import load_model_cached, transcribe_with_silence_segments
from src.export import build_transcript_file, make_download_name
from src.demucs_vocals import separate_vocals_demucs, cleanup_demucs_artifacts
from src.postprocess import postprocess_transcript


# ---- Límites anti-abuso (ajústalos a tu gusto) ----
MAX_MB = 250                 # tamaño máximo de subida
MAX_MINUTES = 25             # duración máxima del video
MAX_RUNS_PER_SESSION = 3     # transcripciones por sesión


def main():
    st.set_page_config(
        page_title=SERVICE_NAME,
        page_icon="🎙️",
        layout="centered",
    )

    render_header()
    settings = sidebar_settings()

    uploaded = st.file_uploader(
        "Sube un video (MP4, MOV, AVI, MKV)",
        type=["mp4", "mov", "avi", "mkv"],
    )

    if uploaded is None:
        st.caption("Consejo: Para música, activa “Separar voz” y usa modelo medium o large.")
        return

    # --- Validación de tamaño (antes de procesar) ---
    size_mb = uploaded.size / 1024 / 1024
    if size_mb > MAX_MB:
        st.error(f"El archivo excede el máximo permitido ({MAX_MB} MB). Tamaño: {size_mb:.2f} MB.")
        st.stop()

    render_file_info(uploaded)

    if st.button("Iniciar transcripción", type="primary"):
        # --- Rate limit por sesión (anti abuso), NO cuenta si falla ---
        st.session_state.setdefault("runs", 0)
        if st.session_state["runs"] >= MAX_RUNS_PER_SESSION:
            st.warning("Límite de transcripciones por sesión alcanzado. Intenta más tarde.")
            st.stop()

        safe_name = os.path.basename(uploaded.name).replace(" ", "_")
        temp_video_path = f"temp_{safe_name}"
        temp_wav_path = f"temp_{os.path.splitext(safe_name)[0]}.wav"

        # Temporales Demucs
        demucs_run_dir = None

        # Streamlit guarda el archivo en memoria: lo volcamos a disco
        with open(temp_video_path, "wb") as f:
            f.write(uploaded.getbuffer())

        audio_for_transcribe = temp_wav_path

        try:
            # --- Duración (anti abuso) ---
            duration_sec = get_video_duration(temp_video_path)
            if duration_sec > 0:
                st.info(f"Duración detectada: {fmt_time(duration_sec)}")
                if duration_sec > MAX_MINUTES * 60:
                    st.error(
                        f"El video excede el máximo permitido ({MAX_MINUTES} minutos). "
                        f"Duración: {fmt_time(duration_sec)}."
                    )
                    st.stop()
            else:
                duration_sec = 0

            # 1) Convertir a WAV 16k mono
            show_step("1/4 Preparando audio…")
            extract_wav_16k_mono(
                video_path=temp_video_path,
                wav_path=temp_wav_path,
                normalize=settings["normalize_audio"],
            )

            # 2) Demucs (solo si es música y el usuario lo activó)
            if settings.get("use_vocals") and "Música" in settings["audio_profile"]:
                show_step("2/4 Separando voz…")
                working_line("Separando voz… esto puede tardar unos minutos.")

                vocals_mp3, demucs_run_dir = separate_vocals_demucs(temp_wav_path)
                audio_for_transcribe = vocals_mp3
            else:
                show_step("2/4 Saltando separación de voz…")

            # 3) Cargar modelo Whisper
            show_step("3/4 Cargando modelo…")
            model = load_model_cached(settings["model_key"])

            # 4) Transcribir
            show_step("4/4 Transcribiendo…")
            working_line("Procesando audio… (no cierres esta pestaña)")

            raw_text, stats = transcribe_with_silence_segments(
                model=model,
                wav_path=audio_for_transcribe,
                duration_sec=duration_sec,
                settings=settings,
            )

            if not raw_text:
                st.warning("No se generó texto. Prueba otro modelo o ajusta segmentación.")
                st.stop()

            # Post-proceso genérico (NO reemplaza palabras)
            final_text = postprocess_transcript(
                raw_text,
                clean_text=settings.get("clean_text", True),
                normalize_elongations=settings.get("normalize_elongations", False),
                max_consecutive_repeats=settings.get("max_consecutive_repeats", 4),
            )

            st.subheader("Transcripción")
            st.text_area("Resultado", value=final_text, height=360)

            export_txt = build_transcript_file(
                transcript=final_text,
                source_filename=uploaded.name,
                service_name=SERVICE_NAME,
                model_label=settings["model_label"],
                model_key=settings["model_key"],
                audio_profile=settings["audio_profile"],
                precision=settings["precision"],
                language_label=settings["language_label"],
                duration_sec=duration_sec,
                silence_db=stats["silence_db"],
                min_silence=stats["min_silence"],
                min_segment=stats["min_segment"],
                segments_count=stats["segments_count"],
            )

            download_name = make_download_name(uploaded.name, SERVICE_NAME, settings)
            st.download_button(
                label="Descargar transcripción (.txt)",
                data=export_txt,
                file_name=download_name,
                mime="text/plain",
            )

            # Info de rendimiento (aprox)
            if stats.get("rtf") and duration_sec:
                st.caption(f"Tiempo aprox en este equipo: {fmt_time(duration_sec * stats['rtf'])}")

            # ✅ cuenta como “run” solo si terminó OK
            st.session_state["runs"] += 1
            st.success(
                f"Listo. Transcripciones usadas en esta sesión: "
                f"{st.session_state['runs']}/{MAX_RUNS_PER_SESSION}"
            )

        except Exception as e:
            st.error("Ocurrió un error durante el proceso.")
            st.exception(e)

        finally:
            # Limpieza Demucs (evita llenar el disco en servidor)
            cleanup_demucs_artifacts(demucs_run_dir)

            # Limpieza temporales principales
            for p in (temp_wav_path, temp_video_path):
                if p and os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

    # Footer / autor
    st.divider()
    st.markdown("Desarrollado por **BrucceVT** · [github.com/BrucceVT](https://github.com/BrucceVT)")


if __name__ == "__main__":
    main()
