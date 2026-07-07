#!/bin/bash
echo "=========================================================="
echo "    COMPILADOR MAC OS (.app) - CON FFMPEG INCLUIDO EN RAM"
echo "=========================================================="
echo ""

VERSION=$(cat VERSION 2>/dev/null || echo "1.0.0")
APP_NAME="Oli Converter v${VERSION}"

FFMPEG_PATH="bin/ffmpeg"
VOSK_MODEL=$(ls -d bin/vosk-model-* 2>/dev/null | head -1)

if [ ! -f "$FFMPEG_PATH" ]; then
    echo "¡ERROR! No se encontro $FFMPEG_PATH."
    echo "Descarga el binario estatico de FFmpeg para Mac y ponlo en la carpeta bin/"
    exit 1
fi

echo "» Version: ${VERSION}"
echo "» FFmpeg local detectado en: $FFMPEG_PATH"
if [ -n "$VOSK_MODEL" ]; then
    echo "» Modelo Vosk detectado en: $VOSK_MODEL"
fi
echo "» Construyendo el archivo .app..."

ADD_DATA="--add-data ${FFMPEG_PATH}:."
if [ -n "$VOSK_MODEL" ]; then
    VOSK_DIRNAME=$(basename "$VOSK_MODEL")
    ADD_DATA="${ADD_DATA} --add-data ${VOSK_MODEL}:${VOSK_DIRNAME}"
fi

pyinstaller --noconfirm --windowed --name "${APP_NAME}" ${ADD_DATA} main.py

echo ""
echo "=== ¡LISTO! ==="
echo "Encuentra tu app en: dist/${APP_NAME}.app"
