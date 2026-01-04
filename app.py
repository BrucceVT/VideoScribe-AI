import streamlit as st
import os
import whisper
from moviepy import VideoFileClip
import time

# --- Configuración de la página (Minimalista) ---
st.set_page_config(
    page_title="VideoScribe-AI",
    page_icon="🎙️",
    layout="centered"
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("🎙️ VideoScribe-AI")
st.write("Transforma tus videos en texto con Inteligencia Artificial. Optimizado para Español Latino.")

# --- Barra lateral para configuraciones ---
with st.sidebar:
    st.header("⚙️ Configuración")
    st.write("Selecciona la potencia del modelo de IA.")
    # Selector de modelo
    modelo_seleccionado = st.selectbox(
        "Modelo Whisper:",
        ("base", "small", "medium", "large"),
        index=2, # Por defecto selecciona 'medium' (índice 2)
        help="Base es rápido pero menos preciso. Medium/Large son lentos pero muy precisos."
    )
    st.info(f"Modelo seleccionado: **{modelo_seleccionado}**")

# --- Función principal de procesamiento (Backend) ---
# Usamos @st.cache_resource para cargar el modelo solo una vez y no en cada clic
@st.cache_resource
def cargar_modelo(nombre_modelo):
    print(f"Cargando modelo {nombre_modelo}...")
    return whisper.load_model(nombre_modelo)

def procesar_video(ruta_video_temp, modelo_nombre):
    ruta_audio_temp = "temp_audio_web.mp3"
    
    try:
        # 1. Extraer Audio
        with st.spinner('Extrayendo audio del video... 🎧'):
            with VideoFileClip(ruta_video_temp) as video:
                video.audio.write_audiofile(ruta_audio_temp, logger=None)
        
        # 2. Cargar Modelo (usando caché)
        with st.spinner(f'Cargando el cerebro de la IA ({modelo_nombre})... 🧠'):
            model = cargar_modelo(modelo_nombre)
            
        # 3. Transcribir
        with st.spinner('Transcribiendo... esto puede tomar unos minutos ⏳'):
            # Forzamos español y desactivamos fp16 para evitar warnings en CPU
            resultado = model.transcribe(ruta_audio_temp, language="es", fp16=False)
            return resultado["text"]

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
        return None
    finally:
        # Limpieza de archivos temporales
        if os.path.exists(ruta_audio_temp):
            os.remove(ruta_audio_temp)
        if os.path.exists(ruta_video_temp):
            os.remove(ruta_video_temp)

# --- Interfaz Principal (Frontend) ---

# Widget para subir archivo
archivo_subido = st.file_uploader("Arrastra tu video aquí o haz clic para buscar (MP4, MOV, AVI)", type=["mp4", "mov", "avi", "mkv"])

if archivo_subido is not None:
    # Detalles del archivo
    st.video(archivo_subido) # Muestra una vista previa del video
    st.write(f"Archivo: `{archivo_subido.name}` - Tamaño: `{archivo_subido.size / 1024 / 1024:.2f} MB`")

    # Botón de acción
    if st.button("🚀 Iniciar Transcripción", type="primary"):
        # Streamlit maneja el archivo en memoria, necesitamos guardarlo temporalmente en disco
        # para que MoviePy pueda leerlo.
        temp_video_path = f"temp_{archivo_subido.name}"
        with open(temp_video_path, "wb") as f:
            f.write(archivo_subido.getbuffer())
        
        # Llamamos a la función de procesamiento
        texto_transcrito = procesar_video(temp_video_path, modelo_seleccionado)
        
        if texto_transcrito:
            st.success("✅ ¡Transcripción completada!")
            
            # Mostrar el resultado en un área de texto
            st.text_area("Resultado:", value=texto_transcrito, height=300)
            
            # Botón para descargar el archivo TXT
            nombre_descarga = os.path.splitext(archivo_subido.name)[0] + ".txt"
            st.download_button(
                label="📥 Descargar Transcripción (.txt)",
                data=texto_transcrito,
                file_name=nombre_descarga,
                mime="text/plain"
            )

st.divider()
st.caption("VideoScribe-AI v2.0 - Desarrollado con Streamlit y Whisper")