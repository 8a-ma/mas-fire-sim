import random
from collections import defaultdict
from typing import List, Set, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from environment.pattern import Pattern


class WaveFunctionCollapse:
    """
    Implementación del algoritmo Wave Function Collapse para generar terrenos.
    El algoritmo usa constraints (reglas) definidas en los patrones para generar
    terrenos coherentes y válidos.
    """

    def __init__(self, patterns: 'Pattern', grid_size: int, seed: Optional[int] = None):
        if seed is not None: random.seed(seed)

        self.patterns = patterns
        self.grid_size = grid_size
        self.grid: List[List[Optional[dict]]] = [[None for _ in range(grid_size)] for _ in range(grid_size)]

        # Cada celda comienza con todas las posibilidades
        self.possibilities: List[List[Set[str]]] = [
            [set(p.get('type', 'unknown')) for p in patterns for _ in range(grid_size)]
            for _ in range(grid_size)
        ]

        # Construir diccionario de patrones para búsqueda rápida
        self.pattern_dict = {p.get('type', 'unknown'): p for p in patterns}

        # Mapear qué tipos pueden coexistir
        self._build_adjacency_rules()

    def _build_adjacency_rules(self) -> None:
        """
        Construye las reglas de adyacencia basadas en los 'rules' de cada patrón.
        """

        self.adjacency = defaultdict(set)

        for pattern in self.patterns:
            pattern_type = pattern.get('type', 'unknown')

            for rule in pattern['rules']:
                self.adjacency[pattern_type].add(rule)
            
            # Un patrón puede estar adyacente a sí mismo si está en sus reglas
            if pattern_type in pattern['rules']:
                self.adjacency[pattern_type].add(pattern_type)
    
    def _get_neighbors(self, row: int, col: int) -> List[Tuple[int, int, str]]:
        """
        Obtiene los vecinos de una celda (arriba, abajo, izquierda, derecha).
        Retorna: Lista de (row, col, dirección)
        """

        neighbors = []
        directions = [
            (-1, 0, 'up'),
            (1, 0, 'down'),
            (0, -1, 'left'),
            (0, 1, 'right')
        ]

        for y, x, direction in directions:
            nr, nc = row + y, col + x

            if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                neighbors.append((nr, nc, direction))
        
        return neighbors

    def _propagate(self, row: int, col: int) -> bool:
        """
        Propaga las restricciones cuando una celda es colapsada.
        Retorna True si es válido, False si hay contradicción.
        """

        changed = True

        while changed:
            changed = False

            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    if len(self.possibilities[r][c]) == 0: return False  # Contradicción: celda sin posibilidades

                    if len(self.possibilities[r][c]) > 1:
                        # Filtrar posibilidades basadas en vecinos colapsados
                        new_possibilities = set(self.possibilities[r][c])

                        for nr, nc, direction in self._get_neighbors(r, c):
                            neighbor_possibilities = self.possibilities[nr][nc]

                            # Si el vecino está colapsado
                            if len(neighbor_possibilities) == 1:
                                neighbor_type = list(neighbor_possibilities)[0]

                                # Filtrar my_type basado en lo que puede ser adyacente
                                valid_types = set()

                                for my_type in new_possibilities:
                                    # Verificar si mi_type puede tener neighbor_type como vecino
                                    if neighbor_type in self.adjacency.get(my_type, set()):
                                        valid_types.add(my_type)
                                
                                if valid_types != new_possibilities:
                                    new_possibilities = valid_types
                                    changed = True
                        
                        self.possibilities[r][c] = new_possibilities
            
        return True
    
    def _get_minimum_entropy_cell(self) -> Optional[Tuple[int, int]]:
        """
        Obtiene la celda no colapsada con menor entropía (menos posibilidades).
        """
        min_entropy = float('inf')
        best_cell = None

        for y in range(self.grid_size):
            for x in range(self.grid_size):
                possibilities_count = len(self.possibilities[x][y])

                # Ignorar celdas colapsadas (entropía 0)
                if 1 < possibilities_count < min_entropy:
                    min_entropy = possibilities_count
                    best_cell = (y, x)

        return best_cell
    
    def generate(self, max_attempts: int = 10) -> bool:
        """
        Genera el terreno usando Wave Function Collapse.
        Retorna True si la generación fue exitosa, False si falla
        """

        attempt = 0

        while attempt < max_attempts:
            self.grid = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
            self.possibilities = [
                [set(p['type'] for p in self.patterns) for _ in range(self.grid_size)]
                for _ in range(self.grid_size)
            ]

            # Iniciar con una celda aleatoria
            start_row = random.randint(0, self.grid_size - 1)
            start_col = random.randint(0, self.grid_size - 1)

            # Colapsar la celda inicial
            initial_type = random.choice(list(self.patterns[0]['type'] for _ in [0]))

            if not self._collapse_cell(start_row, start_col, initial_type):
                attempt += 1
                continue

            # Continuar colapsando celdas
            while True:
                cell = self._get_minimum_entropy_cell()

                if cell is None:
                    self._finalize_grid()
                    return True

                row, col = cell

                # Colapsar con una posibilidad aleatoria
                possible_types = list(self.possibilities[row][col])
                chosen_type = random.choice(possible_types)

                if not self._collapse_cell(row, col, chosen_type):
                    # El colapso falló, intentar nuevamente
                    break
            
            attempt += 1
        
        return False
    
    def _collapse_cell(self, row: int, col: int, pattern_type: str) -> bool:
        """
        Colapsa una celda a un tipo específico y propaga las restricciones.
        Retorna True si es válido, False si hay contradicción.
        """

        self.possibilities[row][col] = {pattern_type}
        self.grid[row][col] = self.pattern_dict[pattern_type]

        return self._propagate(row, col)

    def _finalize_grid(self) -> None:
        """Finaliza el grid colapsando cualquier celda restante."""

        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if self.grid[y][x] is None and len(self.possibilities[y][x]) > 0:
                    chosen_type = random.choice(list(self.possibilities[y][x]))
                    self.grid[y][x] = self.pattern_dict[chosen_type]
    
    def render(self) -> str:
        """Renderiza el terreno como una cadena de caracteres usando emojis."""
        result = []

        for row in self.grid:
            line = ""

            for cell in row:
                if cell is not None:
                    line += cell["icon"]
                else:
                    line += "❌"
            
            result.append(line)
        
        return "\n".join(result)