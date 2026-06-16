from __future__ import annotations
import numpy as np
from pygame import Surface
from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from simulation.control.control_law import attraction as ctrl_attraction, repulsion as ctr_repulsion


if TYPE_CHECKING:
    from simulation.agents.context import SimContext


class AgentState(Enum):
    ACTIVE = auto()
    DEPLOYING = auto()
    IDLE = auto()
    OUT_OF_RANGE = auto()


class BaseAgent(ABC):
    """
    Clase base abstracta para todos los agentes.

    Cada subclase implementa step() con su propia ley de control.
    La física común (atracción, repulsión, movimiento) vive aquí.
    """

    _sprite: Surface | None = None

    def __init__(self, id: int, pos: np.ndarray, max_speed: float, comm_radius: float, vision_radius: float, status: AgentState = AgentState.ACTIVE):
        self.id = id
        self.pos = pos.astype(float)
        self.max_speed = max_speed
        self.comm_radius = comm_radius
        self.vision_radius = vision_radius
        self.status = status
    
    @abstractmethod
    def step(self, dt: float, context: 'SimContext') -> None:
        """Avanza el agente un tick. Debe actualizar self.pos y self.status."""
        pass

    @classmethod
    def _build_sprite(cls) -> Surface:
        """Cada subclase define cómo construir su sprite una sola vez."""
        raise NotImplementedError

    def get_sprite(self) -> Surface:
        cls = type(self)

        if cls._sprite is None:
            cls._sprite = cls._build_sprite()
        
        return cls._sprite

    def _attraction(self, target: np.ndarray, alpha: float) -> np.ndarray:
        return ctrl_attraction(self.pos, target, alpha)
    
    def _repulsion(self, neighbors: list['BaseAgent'], beta: float = 2.0, min_dist: float = 10.0) -> np.ndarray:
        return ctr_repulsion(
            self.pos,
            [n.pos for n in neighbors],
            beta=beta,
            d0=min_dist,
        )

    def _move(self, force: np.ndarray, dt: float, grid_size: int) -> None:
        speed = np.linalg.norm(force)

        if speed > self.max_speed:
            force = force / speed * self.max_speed
        
        self.pos = np.clip(self.pos + force * dt, 0.0, grid_size - 1)
    
    def _nearest(self, cells: list[list[int]]) -> np.ndarray | None:
        if not cells: return None

        pts = np.array(cells, dtype=float)
        dists = np.linalg.norm(pts - self.pos, axis=1)

        return pts[np.argmin(dists)]

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"pos={self.pos.round(1)}, status={self.status})"
        )