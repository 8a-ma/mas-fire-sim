import json
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from simulation.fire import Fire
    from simulation.agents.base_agents import BaseAgent


@dataclass
class Event:
    tick: int
    event_type: str
    timestamp: float = field(default_factory=time.time)
    payload: dict = field(default_factory=dict)


class EventLogger:
    """
    Registro cronológico de todos los eventos de la simulación.
    Escribe en memoria durante la simulación y puede volcar a JSON al final.
    """

    def __init__(self) -> None:
        self._events: list[Event] = []

    def log(self, tick: int, event_type: str, **payload) -> None:
        self._events.append(
            Event(
                tick=tick,
                event_type=event_type,
                payload=payload
            )
        )
    
    def log_terrain(self, tick: int, grid_size: int, seed: int | None, patterns_counts: int) -> None:
        self.log(
            tick,
            "TERRAIN_GENERATED",
            grid_size=grid_size,
            seed=seed,
            patterns_counts=patterns_counts
        )
    
    def log_fire_start(self, tick: int, x: int, y: int, wind_dir: int, wind_speed: float) -> None:
        self.log(
            tick,
            "FIRE_STARTED",
            x=x,
            y=y,
            wind_dir=wind_dir,
            wind_speed=wind_speed
        )
    
    def log_fire_state(self, tick: int, fire: 'Fire') -> None:
        self.log(
            tick,
            "FIRE_SPREAD",
            active_cells=len(fire.cells),
            total_area=fire.area,
            is_extinguished=fire.is_extinguished
        )
    
    def log_agent_step(self, tick: int, agent: 'BaseAgent') -> None:
        self.log(
            tick,
            "AGENT_MOVED",
            agent_id=agent.id,
            type=type(agent).__name__,
            pos=agent.pos.tolist(),
            status=agent.status
        )
    
    def dump_json(self, path: str | Path) -> None:
        """Vuelca todos los eventos a un archivo JSON."""
        data = [asdict(e) for e in self._events]
        Path(path).write_text(json.dumps(data, indent=2))
    
    def summary(self) -> dict:
        """Resumen estadístico al final de la simulación."""
        types = [e.event_type for e in self._events]
        return {t: types.count(t) for t in set(types)}