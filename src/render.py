import pygame
from settings.settings import Settings
from environment.cell import FireState
from environment.terrain import Terrain
from patterns.registry import PatternRegistry
from typing import Tuple, Dict, TYPE_CHECKING


if TYPE_CHECKING:
    from environment.cell import Cell


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    h = hex_color.lstrip("#")

    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class Renderer:
    """
    Dibuja el estado del Terrain sobre una Surface de pygame.
    No maneja eventos ni lógica; sólo renderiza.
    """

    def __init__(self, settings: 'Settings'):
        pygame.init()

        self.settings = settings
        
        self.screen = pygame.display.set_mode((self.settings.WINDOW_W, self.settings.WINDOW_H))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption(self.settings.TITLE)

        # Cachear colores base por tipo para no recalcular cada frame
        self._color_cache: Dict[str, Tuple[int, int, int]] = {}
    
    def draw(self, terrain: Terrain):
        """Dibuja todos los tiles del terreno en pantalla."""

        for row in range(terrain.grid_size):
            for col in range(terrain.grid_size):
                cell = terrain.get_cell(row, col)

                color = self._resolve_color(cell)
                
                rect = pygame.Rect(
                    col * self.settings.CELL_PX,
                    row * self.settings.CELL_PX,
                    self.settings.CELL_PX, self.settings.CELL_PX
                )

                pygame.draw.rect(self.screen, color, rect)
    
    def present(self) -> None:
        """Flip del buffer. Llamar una vez por frame, después de draw()."""
        pygame.display.flip()

    def tick(self) -> None:
        self.clock.tick(self.settings.FPS)
    
    def _resolve_color(self, cell: 'Cell') -> tuple[int, int, int]:
        if cell is None: return self.settings.COLOR_FALLBACK
        
        if cell.fire_state == FireState.BURNING: return self.settings.COLOR_BURNING
        
        elif cell.fire_state == FireState.BURNED: return self.settings.COLOR_BURNED
        
        pattern_type = cell.get_pattern_type()

        if pattern_type is None: return self.settings.COLOR_FALLBACK

        if pattern_type not in self._color_cache:
            pattern = PatternRegistry._get(pattern_type)

            self._color_cache[pattern_type] = hex_to_rgb(
                pattern.get('color', '#505050')
            )
        
        return self._color_cache[pattern_type]