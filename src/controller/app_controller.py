import threading
import os
from typing import Callable, Optional

from src.model.image_converter import ImageConverter
from src.model.media_converter import MediaConverter

class AppController:
    """
    Controlador encargado de unificar los modelos y la interfaz gráfica.
    Asegura que todas las tareas de procesamiento corran en Background Threads
    para no congelar la UI jamás.
    """
    def __init__(self, view=None):
        self.view = view
        
    def start_conversion(self, input_path: str, output_path: str, quality: str, 
                         progress_callback: Callable[[int], None],
                         completion_callback: Callable[[bool, str], None]):
        """
        Detona el Job de conversión en un hilo Daemon.
        """
        thread = threading.Thread(
            target=self._run_conversion,
            args=(input_path, output_path, quality, progress_callback, completion_callback),
            daemon=True
        )
        thread.start()
        
    def _run_conversion(self, input_path, output_path, quality, progress_callback, completion_callback):
        ext = os.path.splitext(input_path)[1].lower()
        img_exts = ['.jpg', '.jpeg', '.png', '.webp', '.avif']
        vid_aud_exts = ['.mp3', '.wav', '.flac', '.aac', '.mp4', '.mkv', '.avi', '.mov', '.mts']
        
        try:
            if ext in img_exts:
                converter = ImageConverter(input_path, output_path, quality)
            elif ext in vid_aud_exts:
                converter = MediaConverter(input_path, output_path, quality)
            else:
                raise ValueError(f"Formato no soportado por la arquitectura interna: {ext}")
                
            # Llama a la lógica de negocio que dispara eventos al callback proporcionado
            success = converter.convert(progress_callback)
            
            # Finalización exitosa
            completion_callback(success, "Conversión completada con éxito." if success else "Falló la conversión (Sin errores mostrados).")
            
        except Exception as e:
            # Captura de errores (ej: archivo malogrado, FFmpeg no instalado globalmente, etc)
            completion_callback(False, str(e))
