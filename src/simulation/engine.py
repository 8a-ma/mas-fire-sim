from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING, List, Optional
from simulation.agents.context import SimContext
from simulation.control.comm_graph import CommGraph


if TYPE_CHECKING:
    from simulation.fire import Fire
    from simulation.wind import Wind
    from environment.terrain import Terrain
    from settings.event_logger import EventLogger
    from simulation.agents.base_agents import BaseAgent
    from simulation.agents.drone_agent import DroneAgent


class Engine:
    """
    Orquestador principal del loop de simulación.
    Tiene visión global pero no toma decisiones de control.
    """

    def __init__(self, terrain: 'Terrain', fire: 'Fire', wind: 'Wind', agents: List['BaseAgent'], logger: 'EventLogger'):
        self.terrain = terrain
        self.fire = fire
        self.wind = wind

        self.agents = agents
        self.logger = logger
        self.graph = CommGraph(agents)
        self.tick_n = 0

    def step(self, dt: float = 1.0) -> None:
        self.tick_n += 1
        self.graph.rebuild()

        for agent in self.agents:
            neighbors = self.graph.neighbors_of(agent)
            context = self._build_context(agent, neighbors)
            agent.step(dt, context)

            self.logger.log_agent_step(self.tick_n, agent)
        
        self.fire.step(dt)
        self.logger.log_fire_state(self.tick_n, self.fire)
    
    def _build_context(self, agent: 'BaseAgent', neighbors: List[Optional['BaseAgent']]) -> SimContext:
        """
        Construye el SimContext filtrado por el radio de visión del agente.
        El agente solo ve las celdas de fuego dentro de su vision_radius.
        """
        visible_cells = self._filter_by_fow(agent, self.fire.cells)
        visible_perimeter = self._filter_by_fow(agent, self.fire.perimeter)

        if not isinstance(agent, 'DroneAgent'):
            for drone in self.graph.relayed_drones_for(agent):
                # visible_cells = _merge_unique(visible_cells, self._filter_by_fow(drone, self.fire.cells))
                # visible_perimeter = _merge_unique(visible_perimeter, self._filter_by_fow(drone, self.fire.perimeter))
                pass

        return SimContext(
            fire_cells=visible_cells,
            fire_perimeter=visible_perimeter,
            fire_area=self.fire.area,
            neighbors=neighbors,
            alpha=1.0,
            terrain=self.terrain,
            agent_pos=agent.pos,
            vision_radius=agent.vision_radius,
        )
    
    def _filter_by_fow(self, agent: 'BaseAgent', cells: List[List[int]]) -> List[Optional[List[int]]]:
        """Filtra celdas fuera del radio de visión del agente."""
        
        if not cells: return []

        pts = np.array(cells, dtype=float)
        dists = np.linalg.norm(pts - agent.pos, axis=1)

        return [c for c, d in zip(cells, dists) if d <= agent.vision_radius]