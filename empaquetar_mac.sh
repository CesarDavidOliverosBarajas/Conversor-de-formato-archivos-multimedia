#!/bin/bash
echo "=========================================================="
echo "    COMPILADOR MAC OS (.app) - CON FFMPEG INCLUIDO EN RAM"
echo "=========================================================="
echo ""

# Se asume que descargaste ffmpeg y lo colocaste en la carpeta bin/ del proyecto
FFMPEG_PATH="bin/ffmpeg"

if [ ! -f "$FFMPEG_PATH" ]; then
    echo "¡ERROR! No se encontro $FFMPEG_PATH."
    echo "Descarga el binario estatico de FFmpeg para Mac y ponlo en la carpeta bin/"
    exit 1
fi

echo "» FFmpeg local detectado en: $FFMPEG_PATH"
echo "» Construyendo el archivo .app..."

# Ejecutamos Pyinstaller.
# --add-binary "$FFMPEG_PATH:." le ordena que chupe ffmpeg, lo meta a tu app,
# y no le pida jamás al cliente final que lo instale por su cuenta.
pyinstaller --noconfirm --windowed --name "Oli Converter" --add-binary "$FFMPEG_PATH:." main.py

echo ""
echo "=== ¡LISTO! ==="
echo "Encuentra tu aplicacion portable final (Oli Converter.app) dentro de la carpeta 'dist'."
echo "Puedes enviar esa app a cualquier otra Mac."
