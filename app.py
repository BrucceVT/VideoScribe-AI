import os
import streamlit as st

from src.config import SERVICE_NAME
from src.ffmpeg_audio import is_audio_file, convert_to_wav_16k_mono, get_media_duration
from src.ui import (
    render_header,
    render_author_fixed,
    sidebar_settings,
    render_file_info,
    fmt_time,
)
from src.transcriber import load_model_cached, transcribe_with_silence_segments
from src.export import build_transcript_file, make_download_name
from src.demucs_vocals import separate_vocals_demucs, cleanup_demucs_artifacts
from src.postprocess import postprocess_transcript
from src.session_sec import check_rate_limit, increment_usage, get_runs_for_user


# ---- Límites anti-abuso ----
MAX_MB = 250
MAX_MINUTES = 25


def main():
    st.set_page_config(
        page_title=SERVICE_NAME,
        page_icon="🎙️",
        layout="wide",
    )

    render_header()

    # ✅ Intento de footer fijo (visual). Aun si el navegador/iframe lo reacomoda,
    # el autor queda SIEMPRE en sidebar.
    render_author_fixed()

    settings = sidebar_settings()

    # Inicializar estado para saber si hay archivo o no y hacer shift
    if "has_file" not in st.session_state:
        st.session_state.has_file = False

    def on_upload_change():
        st.session_state.has_file = True

    if not st.session_state.has_file:
        # Layout centrado inicial Premium
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col_space_l, center_col, col_space_r = st.columns([1, 1.5, 1])
        with center_col:
            st.markdown(
                "<h1 style='text-align: center; color: #4A90E2;'>Sube tu Archivo</h1>"
                "<p style='text-align: center; font-size: 1.1rem; color: #555;'>"
                "Arrastra tu video o audio aquí y deja que nuestra IA haga el trabajo pesado."
                "</p>", 
                unsafe_allow_html=True
            )
            st.write("")
            uploaded = st.file_uploader(
                "",
                type=["mp4", "mov", "avi", "mkv", "mp3", "wav", "ogg", "flac", "m4a"],
                on_change=on_upload_change,
                key="uploader_center",
                label_visibility="collapsed"
            )
            if uploaded is None:
                st.info("💡 **Tip UX:** Para canciones, ve Configuración (`>` ) y activa **Música**, añade Separar voz para limpiar las letras.", icon="✨")
                return

    # Si hay archivo, diseño profesional a dos paneles limpios
    st.markdown("### ✨ Configuración del Archivo")
    col1, col2 = st.columns([1, 1.2], gap="large")

    with col1:
        uploaded = st.file_uploader(
            "Archivo seleccionado",
            type=["mp4", "mov", "avi", "mkv", "mp3", "wav", "ogg", "flac", "m4a"],
            key="uploader_side"
        )

        if uploaded is None:
            # Si el usuario borra el archivo desde la vista de 2 columnas, regresamos al centro
            st.session_state.has_file = False
            st.rerun()

        size_mb = uploaded.size / 1024 / 1024
        if size_mb > MAX_MB:
            st.error(f"El archivo excede el máximo permitido ({MAX_MB} MB). Tamaño: {size_mb:.2f} MB.")
            st.stop()

        # Mostrar info de forma bonita
        with st.container(border=True):
            is_audio = is_audio_file(uploaded.name)
            render_file_info(uploaded, is_audio)
            st.write("")
            iniciar_btn = st.button("🚀 Iniciar transcripción", type="primary", use_container_width=True)

    if iniciar_btn:
        # --- Rate limit persistente por sesión/IP ---
        if not check_rate_limit(settings):
            with col1:
                st.error("🚫 **Límite de transcripciones alcanzado.**\nIntenta más tarde o ingresa un código VIP en Preferencias.")
            st.stop()

        safe_name = os.path.basename(uploaded.name).replace(" ", "_")
        temp_video_path = f"temp_{safe_name}"
        temp_wav_path = f"temp_{os.path.splitext(safe_name)[0]}.wav"

        demucs_run_dir = None
        audio_for_transcribe = temp_wav_path

        with open(temp_video_path, "wb") as f:
            f.write(uploaded.getbuffer())

        try:
            with col1:
                duration_sec = get_media_duration(temp_video_path)
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

            with col2:
                st.subheader("2. Proceso y Resultado")
                with st.status("Preparando entorno...", expanded=True) as status:
                    if is_audio:
                        status.update(label="1/4 Convirtiendo audio…")
                    else:
                        status.update(label="1/4 Extrayendo audio del video…")
                    convert_to_wav_16k_mono(
                        input_path=temp_video_path,
                        wav_path=temp_wav_path,
                        normalize=settings["normalize_audio"],
                    )

                    if settings.get("use_vocals") and "Música" in settings["audio_profile"]:
                        status.update(label="2/4 Separando voz… (esto puede tardar unos minutos)")
                        vocals_mp3, demucs_run_dir = separate_vocals_demucs(temp_wav_path)
                        audio_for_transcribe = vocals_mp3
                    else:
                        status.update(label="2/4 Saltando separación de voz…")

                    status.update(label="3/4 Cargando modelo de Inteligencia Artificial…")
                    model = load_model_cached(settings["model_key"])

                    status.update(label="4/4 Transcribiendo audio… (no cierres esta pestaña)")
                    # La funcion de transcripcion muestra progreso interno aquí
                    raw_text, stats = transcribe_with_silence_segments(
                        model=model,
                        wav_path=audio_for_transcribe,
                        duration_sec=duration_sec,
                        settings=settings,
                    )
                    
                    status.update(label="Transcripción finalizada con éxito", state="complete", expanded=False)

                if not raw_text:
                    st.warning("No se generó texto. Prueba otro modelo o ajusta segmentación.")
                    st.stop()

                final_text = postprocess_transcript(
                    raw_text,
                    clean_text=settings.get("clean_text", True),
                    normalize_elongations=settings.get("normalize_elongations", False),
                    max_consecutive_repeats=settings.get("max_consecutive_repeats", 4),
                )

                st.subheader("Transcripción Completa")
                st.text_area("Caja de texto (editable)", value=final_text, height=360, label_visibility="collapsed")

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
                
                # Fila para Descargar y Copiar text
                bc1, bc2 = st.columns(2)
                with bc1:
                    st.download_button(
                        label="⬇️ Descargar (.txt)",
                        data=export_txt,
                        file_name=download_name,
                        mime="text/plain",
                        use_container_width=True
                    )
                with bc2:
                    import streamlit.components.v1 as components
                    escaped_text = final_text.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$').replace('\n', '\\n').replace('"', '\\"')
                    html_code = f"""
                    <button onclick="navigator.clipboard.writeText(`{escaped_text}`); this.innerText='✅ Copiado!';" 
                            style="width:100%; height:41px; border:1px solid #ccc; border-radius:8px; background-color:#ffffff; 
                            color:#31333F; font-size:14px; cursor:pointer; font-family:sans-serif; transition: 0.2s;">
                        📋 Copiar todo
                    </button>
                    """
                    components.html(html_code, height=45)

                if stats.get("rtf") and duration_sec:
                    st.caption(f"Tiempo aprox de procesamiento en este equipo: {fmt_time(duration_sec * stats['rtf'])}")

                # ✅ cuenta el run solo si terminó OK
                increment_usage(settings)
                runs, max_runs = get_runs_for_user(settings)
                
                if max_runs == 999:
                    uso_str = "Ilimitado (Modo VIP activo)"
                else:
                    uso_str = f"{runs}/{max_runs}"
                    
                st.success(f"Listo. Transcripciones usadas: {uso_str}")

        except Exception as e:
            st.error("Ocurrió un error durante el proceso.")
            st.exception(e)

        finally:
            cleanup_demucs_artifacts(demucs_run_dir)

            for p in (temp_wav_path, temp_video_path):
                if p and os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass


if __name__ == "__main__":
    main()
