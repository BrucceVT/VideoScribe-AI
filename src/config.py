SERVICE_NAME = "VideoScribe-AI"

# 🔓 PREMIUM LIBERADO (por ahora)
IS_PRO = True

# Modelos Whisper disponibles
MODEL_OPTIONS = {
    "Estándar": "small",
    "Alta precisión": "medium",
    "Precisión máxima (experimental)": "large",
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
