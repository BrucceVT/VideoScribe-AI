# Transcriptor de Video a Texto (Whisper) 🎙️🎬

Este es un script de Python diseñado para extraer el audio de archivos de video y convertirlo a texto utilizando la tecnología de Inteligencia Artificial **Whisper** de OpenAI.

> **Nota:** Este proyecto está configurado y probado específicamente para **Windows**.

## 🚀 Requisitos Previos

### 1. Instalar FFmpeg (Obligatorio en Windows)
Este script requiere FFmpeg para procesar archivos multimedia.

1. Descarga el archivo `ffmpeg-release-essentials.zip` desde [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
2. Extrae la carpeta en `C:\ffmpeg`.
3. Agrega `C:\ffmpeg\bin` a las **Variables de Entorno (PATH)** de tu sistema.
4. Verifica la instalación abriendo una terminal y escribiendo:
   ```bash
   ffmpeg -version
   ```

### 2. Python 3.8 o superior
Asegúrate de tener Python instalado y agregado al PATH.

## 🛠️ Instalación y Uso

### 1. Clonar el repositorio
```bash
git clone https://github.com/BrucceVT/VideoScribe-AI
cd VideoScribe-AI
```

### 2. Crear y activar el entorno virtual
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install moviepy openai-whisper torch
```

### 4. Ejecutar el script
```bash
python transcriptor.py
```

## 📝 Cómo funciona
- El script extrae el audio del video en formato `.mp3`.
- Utiliza el modelo **medium** de Whisper para una alta precisión en Español Latinoamericano.
- Genera un archivo `.txt` con el mismo nombre del video en la carpeta de origen.

## ✨ Créditos
- OpenAI Whisper  
- MoviePy  

---

## 📤 Pasos para subirlo a GitHub

Si ya creaste el repositorio vacío en GitHub, ejecuta estos comandos en tu terminal (dentro de la carpeta del proyecto):

### 1. Inicializar el repositorio local
```bash
git init
```

### 2. Agregar los archivos
```bash
git add .
```

### 3. Primer commit
```bash
git commit -m "Versión inicial: Extracción de audio y transcripción con Whisper medium"
```

### 4. Conectar con GitHub
```bash
git branch -M main
git remote add origin https://github.com/BrucceVT/VideoScribe-AI
```

### 5. Subir todo
```bash
git push -u origin main
```

---

## 🚧 Próximas mejoras (Roadmap)
- Soporte para múltiples archivos (batch processing).
- Interfaz gráfica sencilla (GUI).
- Exportación a formato de subtítulos `.srt`.
