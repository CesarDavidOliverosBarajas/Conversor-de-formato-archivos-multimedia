import os
from PIL import Image
from typing import Optional, Callable
from .base_converter import BaseConverter

class ImageConverter(BaseConverter):
    """
    Controlador para convertir Imágenes usando Pillow (PIL).
    Soporta eficientemente: JPG, PNG, WEBP, AVIF, entre otros.
    """

    def convert(self, progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        try:
            if progress_callback:
                progress_callback(10)  # Progreso inicial
                
            img = Image.open(self.input_path)
            
            # Ciertas conversiones (ej. de PNG transparente a JPEG) requieren remover el canal alpha (A).
            if img.mode in ("RGBA", "P", "LA"):
                target_ext = os.path.splitext(self.output_path)[1].lower()
                if target_ext in ['.jpg', '.jpeg']:
                    # Creamos un fondo blanco y pegamos la imagen original encima para evitar fondos negros
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "RGBA" or img.mode == "LA":
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background
            
            if progress_callback:
                progress_callback(50)  # Procesamiento intermedio (lectura en memoria completada)
                
            # Mapeo dinámico de las calidades especificas para los motores de JPEG/WEBP
            quality_map = {
                "Sin pérdida": 100,
                "Alta": 90,
                "Media": 70,
                "Baja": 40
            }
            q_val = quality_map.get(self.quality, 90)
            
            # Formatos que soportan "lossless" internamente en Pillow (ej: WebP)
            save_kwargs = {}
            target_ext = os.path.splitext(self.output_path)[1].lower()
            
            if target_ext == '.webp' and self.quality == "Sin pérdida":
                save_kwargs['lossless'] = True
            elif target_ext in ['.jpg', '.jpeg', '.webp', '.avif']:
                save_kwargs['quality'] = q_val
                save_kwargs['optimize'] = True
                
            # Ejecutar el guardado
            img.save(self.output_path, **save_kwargs)
            
            if progress_callback:
                progress_callback(100) # Cierre del proceso
                
            return True
            
        except Exception as e:
            raise Exception(f"Error procesando la imagen:\n{str(e)}")
