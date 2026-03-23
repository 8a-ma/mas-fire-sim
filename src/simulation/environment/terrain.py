from __future__ import annotations


VALID_TRANSITIONS: dict[str, list[str]] = {
    "normal":    ["burned", "firebreak"],
    "firebreak": [],
    "burned":    [],
}


class Cell:
    def __init__(self, x: int, y: int, state: str="normal") -> None:
        self.x = x
        self.y = y
        self.state = state

    @property
    def is_flammable(self) -> bool:
        return self.state == "normal"
    
    def transition_to(self, new_state: str) -> bool:    
        if new_state in VALID_TRANSITIONS.get(self.state, []):
            self.state = new_state
            return True

        return False
    
    def __repr__(self):
        icons = {"normal": "🌲", "burned": "🔥", "firebreak": "🧱"}
        return icons.get(self.state, "❓")


class Terrain:
    def __init__(self, n: int) -> None:
        self.n = n
        self.grid: list[list[Cell]] = [[Cell(x, y) for y in range(n)] for x in range(n)]
    
    def get_cell(self, x: int, y: int) -> Cell | None:
        if 0 <= x < self.n and 0 <= y < self.n:
            return self.grid[x][y]
        return None
    
    def set_state(self, x: int, y: int, state: str) -> bool:
        cell = self.get_cell(x, y)

        if cell is None:
            return False
        
        return cell.transition_to(state)

    def get_neighbors(self, x: int, y: int, diagonal: bool = True) -> list[Cell]:
        offsets = ([(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)] if diagonal else [(-1, 0), (0, -1), (0, 1), (1, 0)])

        neighbors  = []

        for dx, dy in offsets:
            cell = self.get_cell(x + dx, y + dy)

            if cell is not None:
                neighbors.append(cell)
            
        return neighbors