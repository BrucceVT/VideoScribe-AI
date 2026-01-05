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
from src.demucs_vocals import separate_vocals_demucs
from src.postprocess import postprocess_transcript


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
        return

    render_file_info(uploaded)

    if st.button("Iniciar transcripción", type="primary"):
        safe_name = os.path.basename(uploaded.name).replace(" ", "_")
        temp_video_path = f"temp_{safe_name}"
        temp_wav_path = f"temp_{os.path.splitext(safe_name)[0]}.wav"

        with open(temp_video_path, "wb") as f:
            f.write(uploaded.getbuffer())

        audio_for_transcribe = temp_wav_path

        try:
            duration_sec = get_video_duration(temp_video_path)
            if duration_sec > 0:
                st.info(f"Duración detectada: {fmt_time(duration_sec)}")

            # 1) Audio
            show_step("1/4 Preparando audio…")
            extract_wav_16k_mono(
                video_path=temp_video_path,
                wav_path=temp_wav_path,
                normalize=settings["normalize_audio"],
            )

            # 2) Demucs (solo música)
            if settings.get("use_vocals") and "Música" in settings["audio_profile"]:
                show_step("2/4 Separando voz…")
                working_line("Separando voz… esto puede tardar unos minutos.")
                audio_for_transcribe = separate_vocals_demucs(temp_wav_path)

            # 3) Modelo
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
                return

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

            if stats.get("rtf") and duration_sec:
                st.caption(f"Tiempo aprox en este equipo: {fmt_time(duration_sec * stats['rtf'])}")

        except Exception as e:
            st.error("Ocurrió un error durante el proceso.")
            st.exception(e)

        finally:
            for p in (temp_wav_path, temp_video_path):
                if p and os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass


if __name__ == "__main__":
    main()
