from __future__ import annotations
import numpy as np
from abc import ABC, abstractmethod
from simulation.agents.context import SimContext
from simulation.control.control_law import attraction as ctrl_attraction
from simulation.control.repulsion import repulsion as ctrl_repulsion


VALID_STATUSES = {"active", "deploying", "idle", "out_of_range"}


class BaseAgent(ABC):
    """
    Clase base abstracta para todos los agentes de la simulación.
 
    Cada subclase implementa step() con su propia ley de control.
    La física común (atracción + repulsión + clamp de velocidad) vive
    aquí como helpers para evitar duplicación.
 
    Attributes:
        agent_id   : identificador único (coincide con agents[].id del contrato)
        pos        : posición actual [x, y] en el grid 256x256
        max_speed  : velocidad máxima en unidades/tick
        status     : estado del agente (active | deploying | idle | out_of_range)
    """
     
    def __init__(
            self,
            agent_id: int,
            pos: np.ndarray,
            max_speed: float,
            status: str = "active"
    ) -> None:
        
        if status not in VALID_STATUSES:
            raise ValueError(F"status invalido: {status!r}. Opciones: {VALID_STATUSES}")

        self.agent_id = id
        self.pos = pos.astype(float)
        self.max_speed = max_speed
        self.status = status

    @abstractmethod
    def step(self, dt: int, context: SimContext) -> None:
        """
        Avanza el agente un tick de duración dt.
 
        Debe actualizar self.pos y self.status.
        No retorna nada — el Engine lee el estado tras llamar step().
        """
        ...

    def _attraction(self, target: np.ndarray, alpha: float) -> np.ndarray:
        return ctrl_attraction(self.pos, target, alpha)

    def _repulsion(self, neighbors: list["BaseAgent"], min_dist: float = 10.0) -> np.ndarray:
        return ctrl_repulsion(
            self.pos,
            [n.pos for n in neighbors],
            min_dist=min_dist,
        )
    
    def _move(self, force: np.ndarray, dt: float, grid_size: int = 256) -> None:
        """
        Aplica la fuerza resultante a la posición, respetando max_speed
        y los límites del grid.
        """
        
        speed = np.linalg.norm(force)

        if speed > self.max_speed:
            force = force / speed * self.max_speed
        
        self.pos = self.pos + force * dt
        self.pos = np.clip(self.pos, 0.0, grid_size - 1)

    def _nearest(self, cells: list[list[int]]) -> np.ndarray | None:
        """
        Retorna el punto más cercano a self.pos de entre una lista [[x,y], ...].
        Retorna None si la lista está vacía.
        """

        if not cells:
            return None
        
        pts = np.array(cells, dtype=float)
        dists = np.linalg.norm(pts - self.pos, axis=1)
        return pts[np.argmin(dists)]
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.agent_id}, "
            f"pos={self.pos.round(1)}, status={self.status!r})"
        )