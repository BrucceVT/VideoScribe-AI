#!/bin/bash

# ============================================
#  VideoScribe-AI — Script de inicio
# ============================================

# Detectar sistema operativo y activar venv
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "mingw"* || "$OSTYPE" == "cygwin" ]]; then
    # Git Bash / MSYS2 / Cygwin en Windows
    source .venv/Scripts/activate
elif [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    # Linux / macOS
    source .venv/bin/activate
else
    echo "⚠️  Sistema no reconocido ($OSTYPE). Intentando activación estilo Windows..."
    source .venv/Scripts/activate
fi

echo ""
echo "=========================================="
echo "  🎙️  VideoScribe-AI"
echo "=========================================="
echo ""
echo "  ¿Cómo deseas transcribir?"
echo ""
echo "  1) Terminal   — Rápido y directo"
echo "  2) Interfaz   — Web con opciones avanzadas"
echo ""
read -p "  Selecciona una opción (1/2): " opcion

case $opcion in
    1)
        echo ""
        echo "  ▶ Iniciando modo Terminal..."
        echo ""
        python transcriptor.py
        ;;
    2)
        echo ""
        echo "  ▶ Iniciando interfaz web..."
        echo ""
        streamlit run app.py
        ;;
    *)
        echo ""
        echo "  ❌ Opción no válida. Usa 1 o 2."
        echo ""
        ;;
esac
