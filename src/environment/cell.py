from __future__ import annotations
from typing import Set, Optional
from enum import Enum, auto


class FireState(Enum):
    NORMAL = auto()
    BURNING = auto()
    BURNED = auto()


class Cell:
    """
    Representa una celda individual en el terreno.
    Cada celda puede estar en estado colapsado (un solo tipo) o en superposición (múltiples posibilidades).
    """

    def __init__(self, possible_types: Set[str]):
        self.possibilities: Set[str] = possible_types.copy()
        self.collapsed_type: Optional[str] = None
        self.fire_state: FireState = FireState.NORMAL
    
    # --- WFC ---
    
    def collapse(self, pattern_type: str) -> None:
        """
        Colapsa la celda a un tipo específico.
        """

        self.possibilities = {pattern_type}
        self.collapsed_type = pattern_type
    
    @property
    def is_collapsed(self) -> bool:
        """Verifica si la celda está colapsada (tiene un único tipo)."""
        return len(self.possibilities) == 1

    @property
    def get_entropy(self) -> int:
        """Retorna la entropía (número de posibilidades) de la celda."""
        return len(self.possibilities)

    def constrain(self, valid_types: Set[str]) -> bool:
        """
        Reduce las posibilidades a solo las válidas.
        """

        self.possibilities &= valid_types

        if not self.possibilities:
            return False
        
        return True

    def get_pattern_type(self) -> Optional[str]:
        """Retorna el tipo colapsado o None si está en superposición."""
        if self.is_collapsed: return self.collapsed_type

        return None
    
    # --- FSM ---

    @property
    def is_flammable(self) -> bool:
        """
        True si la celda puede ser encendida.
        Requiere: estar colapsada, el patrón registrado como inflamable, y no estar ya ardiendo o quemada.
        """

        from patterns.registry import PatternRegistry
        
        if not self.is_collapsed or self.fire_state != FireState.NORMAL: return False

        return PatternRegistry.is_flammable(self.collapsed_type)
    
    def ignite(self) -> bool:
        """NORMAL → BURNING. Retorna True si la transición ocurrió."""

        if self.fire_state == FireState.NORMAL and self.is_flammable:
            self.fire_state = FireState.BURNING

            return True
    
        return False
    
    def burn_out(self) -> None:
        """BURNING → BURNED."""
        if self.fire_state == FireState.BURNING:
            self.fire_state = FireState.BURNED