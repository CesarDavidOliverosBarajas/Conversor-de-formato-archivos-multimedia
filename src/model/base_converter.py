from abc import ABC, abstractmethod
from typing import Optional, Callable

class BaseConverter(ABC):
    """
    Clase base abstracta (Interface) para los diferentes conversores de la aplicación.
    Fuerza a todos los conversores a implementar la misma lógica genérica de entrada/salida.
    """
    
    def __init__(self, input_path: str, output_path: str, quality: str):
        """
        :param input_path: Ruta absoluta al archivo de origen.
        :param output_path: Ruta absoluta al archivo de destino (con la nueva extensión).
        :param quality: Nivel de calidad ("Sin pérdida", "Alta", "Media", "Baja").
        """
        self.input_path = input_path
        self.output_path = output_path
        self.quality = quality
        
    @abstractmethod
    def convert(self, progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        """
        Método que toda clase hija debe implementar para ejecutar la conversión real.
        
        :param progress_callback: Una función bloqueante o asíncrona a llamar para actualizar 
                                  la barra de progreso de la GUI. Recibe un entero de 0 a 100.
        :return: True si la conversión fue exitosa. Arroja excepciones en caso de error.
        """
        pass
