# VideoScribe-AI 🎙️🎬

Herramienta de transcripción de **video y audio** a texto impulsada por **OpenAI Whisper**. Extrae el audio de archivos multimedia y lo convierte en texto con alta precisión en español e inglés. Ofrece dos formas de uso: un **script por terminal** (rápido y directo) y una **interfaz web interactiva** con opciones avanzadas como separación de voz, selección de modelo y post-procesamiento del texto.

> **Nota:** Este proyecto está configurado y probado específicamente para **Windows**.

### Formatos soportados

| Tipo | Extensiones |
|---|---|
| 🎬 Video | MP4, MOV, AVI, MKV |
| 🎵 Audio | MP3, WAV, OGG, FLAC, M4A |

---

## 🚀 Requisitos Previos

### 1. Python 3.8 o superior
Asegúrate de tener Python instalado y agregado al PATH.

### 2. FFmpeg (Obligatorio)
1. Descarga `ffmpeg-release-essentials.zip` desde [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
2. Extrae la carpeta en `C:\ffmpeg`.
3. Agrega `C:\ffmpeg\bin` a las **Variables de Entorno (PATH)** de tu sistema.
4. Verifica la instalación:
   ```bash
   ffmpeg -version
   ```

---

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/BrucceVT/VideoScribe-AI
cd VideoScribe-AI
```

### 2. Crear y activar el entorno virtual
```bash
python -m venv .venv
```

- **CMD (Windows):**
  ```bash
  .venv\Scripts\activate
  ```
- **Git Bash / Linux / macOS:**
  ```bash
  source .venv/Scripts/activate   # Git Bash en Windows
  source .venv/bin/activate       # Linux / macOS
  ```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## ⚡ Inicio Rápido

Una vez instaladas las dependencias, la forma más fácil de iniciar es con el script `start.sh`:

```bash
bash start.sh
```

El script activa automáticamente el entorno virtual, detecta tu sistema operativo y te presenta un menú para elegir el modo de transcripción:

```
==========================================
  🎙️  VideoScribe-AI
==========================================

  ¿Cómo deseas transcribir?

  1) Terminal   — Rápido y directo
  2) Interfaz   — Web con opciones avanzadas

  Selecciona una opción (1/2):
```

---

## 📝 Uso Detallado

### Opción 1: Modo Terminal (Script directo)

La forma más rápida y sencilla. Ejecuta el script `transcriptor.py` y arrastra un archivo de video o audio a la terminal cuando lo solicite:

```bash
python transcriptor.py
```

**¿Cómo funciona?**
1. El script te pide la ruta del archivo (puedes arrastrar el archivo directamente a la terminal).
2. Detecta automáticamente si es video o audio.
3. Si es video, extrae el audio. Si es audio, lo procesa directamente.
4. Utiliza el modelo **medium** de Whisper para transcribir con alta precisión en español.
5. Genera un archivo `.txt` con el mismo nombre del archivo en la misma carpeta.

**Ejemplo:**
```
--- TRANSCRIPTOR PRO (ESPAÑOL) ---
    Formatos soportados: AAC, AVI, FLAC, FLV, M4A, MKV, MOV, MP3, MP4, OGG, OPUS, WAV, WEBM, WMA, WMV
Arrastra el archivo aquí: C:\Users\Usuario\Música\cancion.mp3

--- 1. Archivo de audio detectado, procesando directamente ---
--- 2. Cargando modelo Whisper MEDIUM (Más preciso) ---
--- 3. Transcribiendo en Español Latino... ---

✅ ¡Listo! Transcripción mejorada en: C:\Users\Usuario\Música\cancion.txt
```

---

### Opción 2: Interfaz Web (Streamlit)

Una interfaz gráfica completa con opciones avanzadas de configuración. Ideal para usuarios que prefieren una experiencia visual o necesitan ajustar parámetros de transcripción.

```bash
streamlit run app.py
```

Esto abrirá la aplicación en tu navegador (por defecto en `http://localhost:8501`).

**Características de la interfaz:**
- 📤 **Subida de archivos**: Sube videos o audios (máx. 250 MB, 25 min).
- 🌐 **Idioma**: Selecciona entre Español e Inglés.
- 🤖 **Modelos**: Elige entre Estándar (small), Alta precisión (medium) o Precisión máxima (large).
- 🎵 **Perfiles de audio**: Optimizado para voz clara o música/ruido.
- 🎤 **Separación de voz**: Usa Demucs para aislar la voz del instrumental (ideal para canciones).
- ✨ **Post-procesamiento**: Limpieza automática del texto, normalización de alargamientos y control de repeticiones.
- 📊 **Segmentación**: Ajusta umbrales de silencio y duración de segmentos.
- 💾 **Descarga**: Descarga la transcripción como archivo `.txt`.

---

## ✨ Tecnologías

| Tecnología | Descripción |
|---|---|
| [OpenAI Whisper](https://github.com/openai/whisper) | Motor de transcripción por IA |
| [Streamlit](https://streamlit.io/) | Framework para la interfaz web |
| [MoviePy](https://zulko.github.io/moviepy/) | Extracción de audio de video |
| [Demucs](https://github.com/facebookresearch/demucs) | Separación de voz/instrumental |
| [FFmpeg](https://ffmpeg.org/) | Procesamiento multimedia |

---

## 👤 Autor

Desarrollado por [BrucceVT](https://github.com/BrucceVT)
