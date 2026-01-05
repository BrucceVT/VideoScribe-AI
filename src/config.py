import os

SERVICE_NAME = "VideoScribe-AI"

# PREMIUM LIBERADO (por ahora)
IS_PRO = True

# Modelos (etiqueta UI -> clave Whisper)
ALL_MODEL_OPTIONS = {
    "Estándar": "small",
    "Alta precisión": "medium",
    "Precisión máxima (experimental)": "large",
}

# En Community Cloud, por recursos, lo estable suele ser SMALL
CLOUD_SAFE_MODEL_OPTIONS = {
    "Estándar": "small",
}

# Para control futuro (paywall)
PRO_MODELS = {"medium", "large"}

# Idiomas soportados (UI en español, esto es SOLO para ayudar al modelo)
LANG_OPTIONS = {
    "Español": "es",
    "Inglés": "en",
}

AUDIO_PROFILES = [
    "Voz clara (clases, entrevistas, podcasts)",
    "Música / ruido (canciones, conciertos, fondo fuerte)",
]

PRECISION_LEVELS = [
    "Rápido",
    "Equilibrado",
    "Máxima precisión",
]


def is_streamlit_cloud() -> bool:
    """
    Heurística práctica para Streamlit Community Cloud.

    - En Community Cloud suelen existir variables relacionadas al entorno y/o
      se ejecuta sin consola interactiva.
    - Permitimos override manual con APP_ENV=local|cloud si quieres forzar.
    """
    forced = (os.getenv("APP_ENV") or "").strip().lower()
    if forced in {"cloud", "streamlit"}:
        return True
    if forced in {"local", "dev"}:
        return False

    # Variables que suelen aparecer en despliegues/containers
    # (no todas están garantizadas, por eso es heurística)
    if os.getenv("STREAMLIT_CLOUD") == "1":
        return True

    # Community Cloud corre dentro de contenedor; HOSTNAME suele estar.
    # En Windows local también puede existir, pero es menos común.
    # Si quieres máxima precisión, fuerza APP_ENV=local en tu PC.
    if os.getenv("HOSTNAME") and os.getenv("GITHUB_REPOSITORY"):
        return True

    return False


def get_model_options() -> dict:
    """
    Retorna el catálogo de modelos disponible según el entorno.
    """
    return CLOUD_SAFE_MODEL_OPTIONS if is_streamlit_cloud() else ALL_MODEL_OPTIONS
