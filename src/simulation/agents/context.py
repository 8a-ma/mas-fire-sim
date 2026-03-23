from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from simulation.agents.base_agent import BaseAgent
    from simulation.environment.fire import Fire


@dataclass
class SimContext:
    """
    Paquete de información que el Engine entrega a cada agente en step().
 
    El Engine lo construye una vez por tick y lo pasa a todos los agentes.
    Cada agente lee solo lo que necesita según su rol.
 
    Attributes:
        fire         : instancia del fuego (acceso a cells, perimeter, area)
        neighbors    : lista de agentes dentro del radio de comunicación
                       del grafo (ya filtrados por CommGraph)
        alpha        : ganancia de control global (configurable via API)
        assigned_target : solo relevante para AerialAgent.
                          Coordenada [x, y] del punto crítico asignado por los drones.
    """
    fire: "Fire"
    neighbors: list["BaseAgent"] = field(default_factory=list)
    alpha: float = 1.0
    assigned_target: np.ndarray | None = None

