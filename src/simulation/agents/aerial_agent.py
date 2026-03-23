from __future__ import annotations
import numpy as np
from simulation.agents.context import SimContext
from simulation.agents.base_agent import BaseAgent


class AerialAgent(BaseAgent):
    """
    Agente aéreo (helicóptero / avión).
 
    Rol en el sistema:
    - Espera un target asignado por el Engine (que lo obtiene de los drones).
    - Cuando recibe un target, vuela hacia él a velocidad media.
    - Al llegar al radio de descarga, aplica agua en área (DROP_RADIUS celdas).
    - Tras descargar, regresa a status "idle" hasta la próxima asignación.
 
    assigned_target viene desde SimContext — es el Engine quien lo decide
    basándose en la tasa de propagación reportada por los drones. Esto
    produce el campo aerial_deployments en las métricas del contrato.
 
    Ley de control (solo traslación, sin repulsión — vuela sobre los demás):
        fuerza = α·(target - pos)
    """

    MAX_SPEED: float = 3.0
    DROP_RANGE: float = 6.0
    DROP_RADIUS: int = 4

    def __init__(self, agent_id: int, pos: np.ndarray) -> None:
        super().__init__(
            agent_id=agent_id,
            pos=pos,
            max_speed=self.MAX_SPEED,
            status="idle"
        )
    
    def step(self, dt: float, context: SimContext) -> None:
        target = context.assigned_target

        if target is None:
            self.status = "idle"
            return
    
        dist = float(np.linalg.norm(target - self.pos))

        if dist <= self.DROP_RANGE:
            self._drop_water(target, context)
            self.status = "deploying"
        
        else:
            force = self._attraction(target, context.alpha)
            self._move(force, dt)
            self.status = "active"
        
    def _drop_water(self, target: np.ndarray, context: SimContext) -> None:
        tx, ty = int(round(target[0])), int(round(target[1]))
        terrain = context.fire.terrain

        for dx in range(-self.DROP_RADIUS, self.DROP_RADIUS + 1):
            for dy in range(-self.DROP_RADIUS, self.DROP_RADIUS + 1):
                if dx * dx + dy * dy <= self.DROP_RADIUS ** 2:
                    terrain.set_state(tx + dx, ty + dy, "firebreak")



