from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from environment.terrain import Terrain
    from simulation.agents.base_agents import BaseAgent


@dataclass
class SimContext:
    """
    Información que el Engine entrega a cada agente en step().
    Todo está filtrado por el radio de visión del agente (fog of war).

    Campos:
        fire_cells        : celdas BURNING visibles por este agente [[x,y],...]
        fire_perimeter    : borde del fuego visible [[x,y],...]
        fire_area         : área total quemada (global, propagada por drones)
        neighbors         : agentes dentro del radio de comunicación
        alpha             : ganancia de atracción global
        terrain           : referencia al Terrain (para consultar tipos de celda)
        agent_pos         : posición del propio agente (copia, no referencia)
        vision_radius     : radio de visión del agente
        assigned_target   : zona objetivo asignada por consenso (puede ser None)
        water_level       : solo Truck; nivel de agua actual
    """

    fire_cells: list  #[[x, y], ...]
    fire_perimeter: list  #[[x, y], ...]
    fire_area: int
    neighbors: list['BaseAgent' | None]
    alpha: float
    terrain: 'Terrain'
    agent_pos: np.ndarray
    vision_radius: float
    assigned_target: np.ndarray | None = None
    water_level: float | None = None