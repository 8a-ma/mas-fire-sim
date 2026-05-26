import random
from collections import deque
from typing import Optional, Set, Dict
from environment.terrain import Terrain
from environment.pattern import Pattern


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

        for _ in range(max_attempts):
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
                chosen_type = self._get_weighted_type(row, col, cell.possibilities)
 
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
 
        return self._propagate(row, col)
    
    def _propagate(self, start_row: int, start_col: int) -> bool:
        """
        Propaga las restricciones a través del terreno.
        Itera hasta que no haya cambios o se encuentra una contradicción
        """
        queue = deque([(start_row, start_col)])
        in_queue = {(start_row, start_col)}

        while queue:
            row, col = queue.popleft()
            in_queue.discard((row, col))

            for nr, nc, _ in self.terrain.get_neighbors(row, col):
                neighbor = self.terrain.get_cell(nr, nc)

                if neighbor.is_collapsed:
                    continue
                    
                before = len(neighbor.possibilities)

                collapsed_neighbor = self.terrain.get_cell(nr, nc)

                if collapsed_neighbor.is_collapsed:
                    neighbor_type = collapsed_neighbor.get_pattern_type()
                    
                    valid = {
                        t for t in neighbor.possibilities
                        if neighbor_type in self.adjacency_map.get(t, set())
                    }

                    if not neighbor.constrain(valid):
                        return False

                if len(neighbor.possibilities) < before and (nr, nc) not in in_queue:
                    queue.append((nr, nc))
                    in_queue.add((nr, nc))
        
        return True

    def _finalize_grid(self) -> None:
        """
        Finaliza el terreno colapsando cualquier celda restante.
        """

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell = self.terrain.get_cell(row, col)

                if not cell.is_collapsed and cell.get_entropy > 0:
                    chosen_type = self._get_weighted_type(row, col, cell.possibilities)
                    cell.collapse(chosen_type)
    
    def _get_weighted_type(self, row: int, col: int, possibilities: set) -> str:
        """
        Elige un tipo de entre las posibilidades usando los pesos acumulados
        de los vecinos ya colapsados.
 
        Para cada vecino colapsado se consultan sus rules: cada rule define
        qué tipos quiere tener como vecino y con qué peso. Se acumulan los
        pesos sobre los tipos posibles de esta celda y se elige con
        random.choices(), respetando así las probabilidades de Pattern.
 
        Si ningún vecino está colapsado aún (p.ej. la celda inicial),
        se trata cada tipo con peso uniforme.
        """

        # Acumular pesos: {tipo: peso_total} para los tipos posibles
        accumulated: Dict[str, float] = {t: 0.0 for t in possibilities}

        for nr, nc, _ in self.terrain.get_neighbors(row, col):
            neighbor_cell = self.terrain.get_cell(nr, nc)

            if neighbor_cell.is_collapsed:
                neighbor_type = neighbor_cell.get_pattern_type()

                neighbor_weights = Pattern.get_neighbor_weights(neighbor_type)

                for candidate_type, weight in neighbor_weights.items():
                    if candidate_type in accumulated:
                        accumulated[candidate_type] += weight
        
        types = list(accumulated.keys())
        weights = [accumulated[t] for t in types]

        if sum(weights) == 0:
            weights = [1.0] * len(types)
        
        return random.choices(types, weights=weights, k=1)[0]
    
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