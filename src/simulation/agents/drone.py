from __future__ import annotations
import numpy as np
from simulation.agents.context import SimContext
from simulation.agents.base_agent import BaseAgent


class Drone(BaseAgent):
    """
    Agente observador (drone).
 
    Rol en el sistema:
    - Recorre el perímetro del fuego con visión radial.
    - No lleva agua — nunca pasa a status "deploying".
    - Publica su posición al grafo para que otros agentes sepan
      dónde está el frente activo (esto lo gestiona el Engine).
 
    Ley de control:
        fuerza = α·(perimetro_cercano - pos) + repulsión_vecinos
 
    El drone se mueve rápido y trata de distribuirse sobre el perímetro,
    lo que garantiza que el frente siempre esté observado.
    """

    MAX_SPEED = 4.0

    def __init__(self, agent_id: str, pos: np.ndarray) -> None:
        super().__init__(
            agent_id=agent_id,
            pos=pos,
            max_speed=self.MAX_SPEED
        )

    def step(self, dt: float, context: SimContext) -> None:
        perimeter = context.fire.perimeter

        if not perimeter:
            self.status = "idle"
            return
    
        target = self._nearest(perimeter)

        force = self._attraction(target, context.alpha) + self._repulsion(context.neighbors)

        self._move(force, dt)
        self.status = "active"
