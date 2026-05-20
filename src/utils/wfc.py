import random
from environment.terrain import Terrain
from environment.pattern import Pattern
from typing import Optional, Set, Dict


class WaveFunctionCollapse:
    """
    Implementación del algoritmo Wave Function Collapse para generar terrenos.
    
    El algoritmo:
    1. Inicia con celdas en superposición (múltiples posibilidades)
    2. Colapsa celdas a un tipo específico basado en probabilidades
    3. Propaga restricciones a las celdas vecinas
    4. Repite hasta que toda la grilla esté colapsada o falla
    """

    def __init__(self, grid_size: int, seed: Optional[int] = None):
        if seed is not None: random.seed(seed)

        self.grid_size = grid_size
        self.terrain: Optional[Terrain] = None
        self.adjacency_map: Dict[str, Set[str]] = Pattern.build_adjacency_map()
        self.all_types: Set[str] = Pattern.get_all_types()

    def generate(self, max_attempts: int = 10) -> bool:
        """
        Genera el terreno usando Wave Function Collapse.
        """

        for attempt in range(max_attempts):
            self.terrain = Terrain(self.grid_size, self.all_types)

            # Iniciar con una celda aleatoria
            start_row = random.randint(0, self.grid_size - 1)
            start_col = random.randint(0, self.grid_size - 1)

            # Colapsar celda inicial con un tipo aleatorio
            initial_type = random.choice(list(self.all_types))

            if not self._collapse_cell(start_row, start_col, initial_type):
                continue

             # Continuar colapsando celdas con menor entropía
            while True:
                cell_coords = self.terrain.get_minimum_entropy_cell()
 
                if cell_coords is None:
                    # Todas las celdas colapsadas
                    self._finalize_grid()
                    return True
 
                row, col = cell_coords
 
                # Colapsar con una posibilidad aleatoria
                cell = self.terrain.get_cell(row, col)
                possible_types = list(cell.possibilities)
                chosen_type = random.choice(possible_types)
 
                if not self._collapse_cell(row, col, chosen_type):
                    # El colapso falló, intentar siguiente iteración
                    break
            
            return False
    
    def _collapse_cell(self, row: int, col: int, pattern_type: str) -> bool:
        """
        Colapsa una celda a un tipo específico y propaga restricciones.
        """

        cell = self.terrain.get_cell(row, col)
        cell.collapse(pattern_type)
 
        return self._propagate()
    
    def _propagate(self) -> bool:
        """
        Propaga las restricciones a través del terreno.
        Itera hasta que no haya cambios o se encuentra una contradicción
        """

        changed = True
 
        while changed:
            changed = False
 
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    cell = self.terrain.get_cell(row, col)
 
                    # Verificar contradicción
                    if cell.get_entropy == 0:
                        return False
 
                    # Si la celda no está colapsada, restringir basándose en vecinos
                    if not cell.is_collapsed:
                        new_possibilities = set(cell.possibilities)
 
                        for nr, nc, _ in self.terrain.get_neighbors(row, col):
                            neighbor_cell = self.terrain.get_cell(nr, nc)
 
                            # Si el vecino está colapsado, restringir mi tipo
                            if neighbor_cell.is_collapsed:
                                neighbor_type = neighbor_cell.get_pattern_type()
                                
                                # Mantener solo tipos válidos que pueden ser vecinos del tipo colapsado
                                valid_types = {
                                    my_type for my_type in new_possibilities
                                    if neighbor_type in self.adjacency_map.get(my_type, set())
                                }
 
                                if valid_types != new_possibilities:
                                    if not cell.constrain(valid_types):
                                        return False
                                    new_possibilities = cell.possibilities
                                    changed = True
 
        return True

    def _finalize_grid(self) -> None:
        """
        Finaliza el terreno colapsando cualquier celda restante.
        """
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell = self.terrain.get_cell(row, col)

                if not cell.is_collapsed and cell.get_entropy > 0:
                    chosen_type = random.choice(list(cell.possibilities))
                    cell.collapse(chosen_type)
    
    def render(self) -> str:
        """
        Renderiza el terreno como una cadena de caracteres usando emojis
        """

        if self.terrain is None:
            return "❌ Terreno no generado"
        
        lines = []

        for row in range(self.grid_size):
            line = ""

            for col in range(self.grid_size):
                cell = self.terrain.get_cell(row, col)

                if cell.is_collapsed:
                    pattern_type = cell.get_pattern_type()

                    icon = Pattern.get_icon_by_type(pattern_type)
                    line += icon
                
                else:
                    line += "❓"
            
            lines.append(line)
        
        return "\n".join(lines)