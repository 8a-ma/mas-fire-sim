from __future__ import annotations
import numpy as np
from simulation.agents.context import SimContext
from simulation.agents.base_agent import BaseAgent



class GroundAgent(BaseAgent):
    """
    Agente terrestre (bombero / camión).
 
    Rol en el sistema:
    - Se mueve lentamente hacia el frente del fuego.
    - Cuando está dentro de water_range, aplica agua:
      convierte la celda más cercana en "firebreak" para
      detener la propagación (modifica el Terrain directamente).
    - status = "deploying" mientras aplica agua, "active" en movimiento.
 
    Ley de control:
        fuerza = α·(perimetro_cercano - pos) + repulsión_vecinos
 
    La baja velocidad compensa con water_range —
    no necesita estar exactamente sobre el fuego para actuar.
    """

    MAX_SPEED: float = 1.5
    WATER_RANGE: float = 3.0

    def __init__(self, agent_id: int, pos: np.ndarray) -> None:
        super().__init__(agent_id=agent_id, pos=pos, max_speed=self.MAX_SPEED)

    def step(self, dt: float, context: SimContext) -> None:
        perimeter = context.fire.perimeter

        if not perimeter:
            self.status = "idle"
            return
        
        target = self._nearest(perimeter)
        dist_to_target = float(np.linalg.norm(target - self.pos))

        if dist_to_target <= self.WATER_RANGE:
            tx, ty = int(round(target[0])), int(round(target[1]))

            context.fire.terrain.set_state(tx, ty, "firebreak")

            self.status = "deploying"
        
        else:
            force = self._attraction(target, context.alpha) + self._repulsion(context.neighbors)

            self._move(force, dt)
            self.status = "active"