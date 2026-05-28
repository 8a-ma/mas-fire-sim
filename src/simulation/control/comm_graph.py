import numpy as np
from typing import TYPE_CHECKING, List, Dict, Optional


if TYPE_CHECKING:
    from simulation.agents.base_agents import BaseAgent


class CommGraph:
    """
    Grafo dinámico de comunicación entre agentes.

    Una arista (i, j) existe si ‖pos_i − pos_j‖ ≤ min(r_comm_i, r_comm_j).
    Se reconstruye en cada tick porque los agentes se mueven.
    """

    def __init__(self, agents: List['BaseAgent']):
        self.agents = agents
        self._edges: Dict[int, list] = {}  # {id: [vecinos]}
    
    def rebuild(self) -> None:
        self._edges = {agent.id: [] for agent in self.agents}

        for idx, agent in enumerate(self.agents):
            for b in self.agents[idx + 1:]:
                dist = np.linalg.norm(agent.pos - b.pos)

                if dist <= min(agent.comm_radius, b.comm_radius):
                    self._edges[agent.id].append(b)
                    self._edges[b.id].append(agent)
    
    def neighbors_of(self, agent: 'BaseAgent') -> List[Optional['BaseAgent']]:
        return self._edges.get(agent.id, [])

    def degree(self, agent: 'BaseAgent') -> int:
        return len(self.neighbors_of(agent))