from environment.cell import Cell
from typing import List, Tuple, Optional, Dict, Set


class Terrain:
    """
    Representa la grilla completa del terreno.
    Gestiona todas las celdas y proporciona métodos para acceder y modificar el estado
    """

    def __init__(self, grid_size: int, initial_possibilities: Dict[str, any]):
        self.grid_size = grid_size
        self.grid: List[List[Cell]] = [
            [Cell(initial_possibilities.copy()) for _ in range(grid_size)]
            for _ in range(grid_size)
        ]
    
    def get_cell(self, row: int, col: int) -> Optional[Cell]:
        """Obtiene una celda específica."""
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            return self.grid[row][col]
        return None
    
    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int, str]]:
        """
        Obtiene los vecinos de una celda (arriba, abajo, izquierda, derecha)
        """

        neighbors = []
        directions = [
            (-1, 0, 'up'),
            (1, 0, 'down'),
            (0, -1, 'left'),
            (0, 1, 'right')
        ]

        for dy, dx, direction in directions:
            nr, nc = row + dy, col + dx
            if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                neighbors.append((nr, nc, direction))
        
        return neighbors
    
    @property
    def is_fully_collapsed(self) -> bool:
        """Verifica si todas las celdas están colapsadas."""
        
        for row in self.grid:
            for cell in row:
                if not cell.is_collapsed:
                    return False
        
        return True
    
    @property
    def has_contradiction(self) -> bool:
        """Verifica si existe alguna celda sin posibilidades (contradicción)."""

        for row in self.grid:
            for cell in row:
                if cell.get_entropy == 0:
                    return True

        return False

    def reset(self, initial_possibilities: Set[str]) -> None:
        """Reinicia todas las celdas a su estado inicial."""

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.grid[row][col] = Cell(initial_possibilities.copy())
    
    def get_minimum_entropy_cell(self) -> Optional[Tuple[int, int]]:
        """
        Obtiene la celda no colapsada con menor entropía.
        """

        min_entropy = float('inf')
        best_cell = None

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell = self.grid[row][col]
                
                # Ignorar celdas colapsadas
                if not cell.is_collapsed:
                    entropy = cell.get_entropy
                    if entropy < min_entropy:
                        min_entropy = entropy
                        best_cell = (row, col)
 
        return best_cell

    def set_state(self, row: int, col: int, state: str) -> None:
        """
        Cambia el fire_state de la celula.
        state: "burned" | "burning" | "normal"
        """

        from environment.cell import FireState


        cell = self.get_cell(row, col)

        if cell is None: return

        mapping = {
            "normal": FireState.NORMAL,
            "burning": FireState.BURNING,
            "burned": FireState.BURNED,
        }

        if state in mapping:
            cell.fire_state = mapping[state]
