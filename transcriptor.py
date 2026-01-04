import os
import whisper
from moviepy import VideoFileClip

def extraer_y_transcribir(ruta_video):
    ruta_video = ruta_video.replace('"', '').replace("'", "").strip()
    nombre_audio = "temp_audio.mp3"
    
    print("\n--- 1. Extrayendo audio del video ---")
    try:
        with VideoFileClip(ruta_video) as video:
            video.audio.write_audiofile(nombre_audio, logger=None)
        
        # --- MEJORA: Seleccionamos un modelo más potente ---
        # 'base' < 'small' < 'medium' < 'large'
        # 'medium' es excelente para español latino.
        print("\n--- 2. Cargando modelo Whisper MEDIUM (Más preciso) ---")
        model = whisper.load_model("medium") 
        
        print("--- 3. Transcribiendo en Español Latino... ---")
        # --- MEJORA: Forzamos el idioma y desactivamos FP16 para evitar el aviso del CPU ---
        resultado = model.transcribe(
            nombre_audio, 
            language="es",   # Forzar español
            fp16=False       # Evita el error/aviso de CPU
        )
        
        nombre_txt = os.path.splitext(ruta_video)[0] + ".txt"
        with open(nombre_txt, "w", encoding="utf-8") as f:
            f.write(resultado["text"])
            
        print(f"\n✅ ¡Listo! Transcripción mejorada en: {nombre_txt}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if os.path.exists(nombre_audio):
            os.remove(nombre_audio)

if __name__ == "__main__":
    print("--- TRANSCRIPTOR PRO (ESPAÑOL) ---")
    archivo = input("Arrastra el video aquí: ")
    extraer_y_transcribir(archivo)