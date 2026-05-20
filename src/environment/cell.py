from typing import Set, Optional


class Cell:
    """
    Representa una celda individual en el terreno.
    Cada celda puede estar en estado colapsado (un solo tipo) o en superposición (múltiples posibilidades).
    """

    def __init__(self, possible_types: Set[str]):
        self.possibilities: Set[str] = possible_types.copy()
        self.collapsed_type: Optional[str] = None
    
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