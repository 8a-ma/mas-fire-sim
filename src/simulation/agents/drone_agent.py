import numpy as np
from pygame import Surface
from simulation.agents.base_agents import BaseAgent, AgentState
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from simulation.agents.context import SimContext


class DroneAgent(BaseAgent):
    """
    Dron observador. Alta velocidad, visión amplia, sin extinción.

    Parámetros por defecto:
        max_speed     = 5.0   unidades/tick
        comm_radius   = 50.0  celdas
        vision_radius = 40.0  celdas
    """

    def __init__(self, id: int, pos: np.ndarray) -> None:
        super().__init__(
            id=id,
            pos=pos,
            max_speed=5.0,
            comm_radius=50.0,
            vision_radius=40.0,
        )

        self.last_visible_cells: list[list[int]] = []
    
    def step(self, dt: float, context: 'SimContext') -> None:
        self.last_visible_cells = context.fire_cells

        target = self._nearest(context.fire_perimeter)
        if target is None: 
            self.status = AgentState.IDLE
            return

        self.status = AgentState.ACTIVE
        drone_neighbors = [n for n in context.neighbors if type(n).__name__ == 'DroneAgent']

        force = self._attraction(target, alpha=context.alpha) + self._repulsion(drone_neighbors, min_dist=20.0)

        self._move(force, dt, context.terrain.grid_size)
    
    def get_sprite(self) -> Surface:
        sprite = Surface((2, 2))
        sprite.fill("#051054")
        return sprite