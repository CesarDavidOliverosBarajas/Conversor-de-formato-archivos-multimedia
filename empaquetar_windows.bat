@echo off
title Compilador del Conversor de Archivos - MODO SEGURO OFFLINE
echo =========================================================================
echo  COMPILADOR WINDOWS (.EXE) - CONVERSOR MULTIMEDIA PRO                 
echo =========================================================================
echo.
echo === CONFIRMACION DE SEGURIDAD OFF-LINE (PRIVACIDAD TOTAL) ===
echo Toda la aplicacion esta disenhada para ejecutarse 100%% en modo local 
echo (en tu propia computadora) usando las librerias locales de Pillow y FFmpeg.
echo Este codigo no contiene NINGUNA libreria web (requests, urllib, socket) 
echo ni sube archivos a ningun servidor de la nube de forma garantizada.
echo =========================================================================
echo.
echo == IMPORTANTE: FFMPEG PARA WINDOWS 10/11 ==
echo Si el ffmpeg.exe actual da problemas en Windows 10, descarga una version
echo compatible desde: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
echo.
echo Pasos:
echo   1. Descarga el ZIP del link de arriba
echo   2. Extrae el archivo "ffmpeg.exe" y colocalo en la carpeta "bin\" 
echo      (reemplazando el existente si es necesario)
echo   3. Ejecuta este .bat nuevamente
echo.
echo NOTA: Para obtener el instalador '.exe' nativo de Windows, debes
echo ejectutar este archivo (.bat) desde una computadora con Windows real
echo (con Python pre-instalado y corriendo 'pip install -r requirements.txt').
echo.
pause

echo Empaquetando la aplicacion en un solo archivo ejecutable...
echo.
pyinstaller --noconsole --onefile --windowed --name "Conversor_Multimedia_Pro" --icon="app.ico" --add-binary "bin\ffmpeg.exe;." main.py

echo.
echo ¡Proceso Finalizado! Tu ejecutable esta en la carpeta "dist".
echo.
echo NOTA: En Windows 10, si el .exe compilado falla al iniciar, instala:
echo   - Microsoft Visual C++ Redistributable 2015-2022 (x64)
echo   Descarga: https://aka.ms/vs/17/release/vc_redist.x64.exe
pause
