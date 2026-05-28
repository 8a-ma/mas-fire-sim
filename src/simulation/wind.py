from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Wind:
    """
    Modelo de viento para la simulación.
 
    direction_deg: ángulo en grados desde el que sopla el viento
                   (0° = Norte, 90° = Este, 180° = Sur, 270° = Oeste).
    speed:         intensidad del viento en unidades de simulación (≥ 0).
    """

    direction_deg: float
    speed: float = 0.0

    def __post_init__(self) -> None:
        if self.speed < 0:
            ValueError(f"speed debe ser >= 0, recibido: {self.speed}")
        
        self.direction_deg = self.direction_deg % 360

    @property
    def bias_vector(self) -> Tuple[float, float]:
        """
        Vector unitario (dx, dy) que representa la dirección de propagación del viento.
        El eje y crece hacia abajo (convención de grid 2D).
 
        Ejemplos:
            direction_deg=0   → (0, -1)  viento del Norte, propaga hacia el Sur
            direction_deg=90  → (1,  0)  viento del Este,  propaga hacia el Oeste... 
            
        Nota: el viento "sopla desde" direction_deg, por eso el vector apunta
        en la dirección opuesta (hacia donde empuja las llamas).
        """
        
        rad = math.radians(self.direction_deg)
        dx = math.sin(rad)
        dy = -math.cos(rad)

        return (dx, dy)