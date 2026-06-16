import numpy as np
from typing import TYPE_CHECKING, List, Dict, Optional, Set


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
    
    def drone_backbone_components(self) -> Dict[int, Set['BaseAgent']]:
        """Componentes conexas considerando solo aristas dron-dron."""
        from simulation.agents.drone_agent import DroneAgent

        drones = [a for a in self.agents if isinstance(a, DroneAgent)]
        visited: Set[int] = set()
        components: Dict[int, Set['BaseAgent']] = {}

        for drone in drones:
            if drone.id in visited:
                continue
            component = self._bfs_component(drone, visited, only_type=DroneAgent)

            for d in component:
                components[d.id] = component
        
        return components
    
    def _bfs_component(drone: 'BaseAgent', visited: set, only_type: 'BaseAgent'):
        ...

    def relayed_drones_for(self, ground_agent: 'BaseAgent') -> Set['BaseAgent']:
        """Drones alcanzables por `ground_agent`: 1 salto directo + backbone de cada uno."""
        from simulation.agents.drone_agent import DroneAgent

        components = self.drone_backbone_components()
        direct_drones = [n for n in self.neighbors_of(ground_agent) if isinstance(n, DroneAgent)]
        reachable: Set['BaseAgent'] = set()

        for d in direct_drones:
            reachable |= components.get(d.id, {d})
            
        return reachable
