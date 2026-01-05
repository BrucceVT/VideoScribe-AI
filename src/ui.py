import streamlit as st

from .config import (
    SERVICE_NAME,
    LANG_OPTIONS,
    AUDIO_PROFILES,
    PRECISION_LEVELS,
    get_model_options,
    is_streamlit_cloud,
)


def _inject_css():
    st.markdown(
        """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Línea de progreso visible (alto contraste) */
.vs-working {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.90);
  border: 1px solid rgba(15, 23, 42, 0.18);
  color: rgba(15, 23, 42, 0.95);
  font-size: 0.95rem;
}
.vs-working strong { color: rgba(15, 23, 42, 0.98); }

@media (prefers-color-scheme: dark) {
  .vs-working {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.25);
    color: rgba(255, 255, 255, 0.95);
  }
  .vs-working strong { color: rgba(255, 255, 255, 0.99); }
  .vs-spinner {
    border: 2px solid rgba(255, 255, 255, 0.25);
    border-top: 2px solid rgba(255, 255, 255, 0.95);
  }
}

.vs-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(15, 23, 42, 0.25);
  border-top: 2px solid rgba(15, 23, 42, 0.95);
  border-radius: 50%;
  animation: vs-spin 0.9s linear infinite;
  flex: 0 0 auto;
}
@keyframes vs-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Footer fijo (visual). Además se muestra en sidebar (permanente). */
.block-container { padding-bottom: 70px; }
.vs-footer-fixed {
  position: fixed;
  left: 0;
  bottom: 0;
  width: 100%;
  padding: 10px 14px;
  z-index: 9999;
  backdrop-filter: blur(8px);
  background: rgba(255, 255, 255, 0.88);
  border-top: 1px solid rgba(15, 23, 42, 0.15);
  font-size: 0.9rem;
  color: rgba(15, 23, 42, 0.92);
  text-align: center;
}
.vs-footer-fixed a { text-decoration: none; }
@media (prefers-color-scheme: dark) {
  .vs-footer-fixed {
    background: rgba(2, 6, 23, 0.55);
    border-top: 1px solid rgba(255, 255, 255, 0.18);
    color: rgba(255, 255, 255, 0.92);
  }
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_header():
    _inject_css()
    st.title(f"{SERVICE_NAME} — Transcripción")
    st.write("Convierte videos a texto con Inteligencia Artificial.")


def render_author_fixed():
    st.markdown(
        """
<div class="vs-footer-fixed">
  Desarrollado por <b>BrucceVT</b> ·
  <a href="https://github.com/BrucceVT" target="_blank">github.com/BrucceVT</a>
</div>
""",
        unsafe_allow_html=True,
    )


def render_author_sidebar():
    st.markdown("---")
    st.caption("Desarrollado por **BrucceVT**")
    st.markdown("[github.com/BrucceVT](https://github.com/BrucceVT)")


def fmt_time(seconds: float) -> str:
    if seconds is None:
        return "—"
    seconds = max(0, int(seconds))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def show_step(text: str):
    st.info(text)


def working_line(text: str):
    st.markdown(
        f"""
<div class="vs-working">
  <div class="vs-spinner"></div>
  <div><strong>En progreso:</strong> {text}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def sidebar_settings() -> dict:
    with st.sidebar:
        st.header("Configuración")

        language_label = st.selectbox(
            "Idioma del audio",
            tuple(LANG_OPTIONS.keys()),
            index=0,
            help="Ayuda al modelo a evitar mezclar idiomas.",
        )
        language_code = LANG_OPTIONS[language_label]

        st.divider()

        model_options = get_model_options()
        if is_streamlit_cloud():
            st.info(
                "Por limitaciones de recursos en Streamlit Cloud, el modelo disponible es "
                "**Estándar (small)**. Para usar medium/large, despliega en un servidor con más RAM "
                "o migra a faster-whisper."
            )

        model_label = st.selectbox(
            "Modelo de transcripción",
            tuple(model_options.keys()),
            index=0,
        )
        model_key = model_options[model_label]

        st.divider()

        audio_profile = st.selectbox("Perfil de audio", AUDIO_PROFILES, index=1)
        precision = st.selectbox("Nivel de precisión", PRECISION_LEVELS, index=2)

        normalize_audio = st.checkbox(
            "Mejorar audio (normalización ligera)",
            value=True,
        )

        use_vocals = False
        if "Música" in audio_profile:
            use_vocals = st.checkbox(
                "Separar voz (mejora letras)",
                value=True,
                help="Aísla la voz del instrumental antes de transcribir.",
            )

        st.divider()
        st.subheader("Calidad del texto")

        clean_text = st.checkbox(
            "Limpieza automática",
            value=True,
            help="Reduce basura típica (muchos signos) y líneas vacías repetidas.",
        )

        normalize_elongations = st.checkbox(
            "Normalizar alargamientos (su-u-u / soooo)",
            value=True if "Música" in audio_profile else False,
            help="Convierte alargamientos en una forma más legible (sin cambiar palabras).",
        )

        max_consecutive_repeats = st.slider(
            "Repeticiones consecutivas máximas (por línea)",
            min_value=2,
            max_value=12,
            value=6 if "Música" in audio_profile else 3,
            help="Evita loops infinitos. Los coros suelen repetirse.",
        )

        st.divider()
        st.subheader("Segmentación")

        default_db = -35 if "Música" in audio_profile else -40
        default_min_sil = 0.30 if "Música" in audio_profile else 0.45
        default_min_seg = 1.20 if "Música" in audio_profile else 1.50

        silence_db = st.slider("Umbral de silencio (dB)", -60, -15, default_db)
        min_silence = st.slider("Silencio mínimo (seg)", 0.10, 2.0, default_min_sil, 0.05)
        min_segment = st.slider("Segmento mínimo (seg)", 0.50, 5.0, default_min_seg, 0.10)

        render_author_sidebar()

    return {
        "language_label": language_label,
        "language_code": language_code,
        "model_label": model_label,
        "model_key": model_key,
        "audio_profile": audio_profile,
        "precision": precision,
        "normalize_audio": normalize_audio,
        "use_vocals": use_vocals,
        "clean_text": clean_text,
        "normalize_elongations": normalize_elongations,
        "max_consecutive_repeats": max_consecutive_repeats,
        "silence_db": silence_db,
        "min_silence": min_silence,
        "min_segment": min_segment,
    }


def render_file_info(uploaded):
    st.video(uploaded)
    st.write(f"Archivo: `{uploaded.name}` — {uploaded.size / 1024 / 1024:.2f} MB")
