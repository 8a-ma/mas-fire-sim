from __future__ import annotations
import pygame
from settings.settings import Settings
from environment.cell import FireState
from environment.terrain import Terrain
from patterns.registry import PatternRegistry
from typing import Tuple, Dict, TYPE_CHECKING, List


if TYPE_CHECKING:
    from environment.cell import Cell
    from simulation.agents.base_agents import BaseAgent


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
        
    def draw_agents(self, agents: List[BaseAgent]) -> None:
        pass
    
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


class Camera:
    """Gestiona el modo de vista y el agente seguido."""

    def __init__(self):
        self.mode: str = "eagle"  # eagle | agent
        self.followed_agent: 'BaseAgent' | None = None
    
    def follow(self, agent: 'BaseAgent') -> None:
        self.mode = "agent"
        self.followed_agent = agent
    
    def release(self) -> None:
        self.mode = "eagle"
        self.followed_agent = None

    def world_to_screen(self):
        """
        Convierte coordenada de mundo a píxel de pantalla.
        En EAGLE_VIEW se ve todas las casillas
        En AGENT_VIEW modifica el brillo de las casillas que se pueden ver de las que no. Las casillas prendidas fuego, quemadas o ardiendo no se pueden ver hasta que el agente pueda verlas
        """
        ...