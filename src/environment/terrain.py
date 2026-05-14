from __future__ import annotations


VALID_TERRAIN: list[str] = ["water", "grass"]


class Cell:
    def __init__(self, x: int, y: int, type: str = 'grass') -> None:
        self.x, self.y = x, y
        self.type = type

    def __repr__(self):
        icons = {"grass": "🌿", "water": "💧"}

        return icons.get(self.type, "❓")


# class Terrain:
#     def __init__(self, n: int):
#         self.n = n
#         self.grid: list[list[Cell]] = [[Cell(x, y) for y in range(n)] for x in range(n)]
    
#     def get_cell(self, x: int, y: int) -> Cell | None:
#         if 0 <= x < self.n and 0 <= y < self.n:
#             return self.grid[x][y]
#         return None

#     def _set_type(self, x: int, y: int, type: str) -> bool:
#         cell: Cell | None = self.get_cell(x, y)

#         if type in VALID_TERRAIN and cell is not None:
#             cell.type = type
#             return True

#         return False