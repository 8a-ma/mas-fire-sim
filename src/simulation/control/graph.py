from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from simulation.agents.base_agent import BaseAgent


class CommGraph:
    """
    Grafo de comunicación entre agentes.
 
    Responsabilidades:
    1. Decidir qué agentes son vecinos (radio de comunicación).
    2. Calcular la matriz Laplaciana del grafo actual.
    3. Exponer λ₂ (segundo valor propio del Laplaciano) como métrica
       de conectividad
 
    El grafo es dinámico: se reconstruye en cada tick porque los agentes
    se mueven, por lo que las aristas cambian continuamente.
 
    λ₂ = 0   → grafo desconexo (al menos un agente aislado)
    λ₂ > 0   → grafo conexo (todos pueden comunicarse)
    λ₂ grande → grafo más robusto (más redundancia de conexiones)
    """

    def __init__(self, comm_radius: float = 15.0) -> None:
        self.comm_radius = comm_radius

        self._laplacian: np.ndarray | None = None
        self._agent_ids: list[int] = []
    
    def build(self, agents: list["BaseAgent"]) -> dict[int, list["BaseAgent"]]:
        """
        Construye el grafo para el tick actual.
 
        Conecta todos los pares de agentes cuya distancia es <= comm_radius
        (grafo de disco unitario — el modelo estándar para redes ad-hoc).
        """

        n = len(agents)
        adjacency: dict[int, list["BaseAgent"]] = {a.agent_id: [] for a in agents}

        # Matriz de posiciones para calcular distancias eficientemente
        positions = np.array([a.pos for a in agents])

        for i in range(n):
            for j  in range(i + 1, n):
                dist = float(np.linalg.norm(positions[i] - positions[j]))

                if dist <= self.comm_radius:
                    adjacency[agents[i].agent_id].append(agents[j])
                    adjacency[agents[j].agent_id].append(agents[i])
        
        # Actualizar caché para λ₂
        self._laplacian = self._compute_laplacian(agents, adjacency)
        self._agent_ids = [a.agent_id for a in agents]

        return adjacency

    @property
    def lambda2(self) -> float:
        """
        Segundo valor propio de la matriz Laplaciana (algebraic connectivity).
 
        λ₂ = 0  → grafo desconexo
        λ₂ > 0  → grafo conexo; cuanto mayor, más robusto
 
        Retorna 0.0 si el grafo aún no ha sido construido.
        """

        if self._laplacian is None:
            return 0.0
        
        eigenvalues = np.linalg.eigvalsh(self._laplacian)

        # eigvalsh retorna valores ordenados; el primero es siempre ~0
        # el segundo (índice 1) es λ₂
        return float(eigenvalues[1]) if len(eigenvalues) > 1 else 0.0
    
    @property
    def is_connected(self) -> bool:
        """True si el grafo es conexo (λ₂ > umbral numérico)."""
        return self.lambda2 > 1e-6
    
    def degree(self, agent_id: int) -> int:
        """Número de vecinos del agente con agent_id en la última build."""

        if self._laplacian is None:
            return 0
        
        try:
            idx = self._agent_ids.index(agent_id)
            return int(round(self._laplacian[idx, idx]))
        
        except ValueError:
            return 0
    
    def _compute_laplacian(
        self,
        agents: list["BaseAgent"],
        adjacency: dict[int, list["BaseAgent"]],
    ) -> np.ndarray:
        """
        Calcula la matriz Laplaciana L = D - A.
 
        D : matriz diagonal de grados
        A : matriz de adyacencia (1 si hay arista, 0 si no)
 
        L es simétrica semidefinida positiva, lo que garantiza que
        todos sus valores propios son >= 0.
        """

        n = len(agents)
        id_to_idx = {a.agent_id: i for i, a in enumerate(agents)}

        A = np.zeros((n, n))

        for agent in agents:
            i = id_to_idx[agent.agent_id]

            for neighbor in adjacency[agent.agent_id]:
                j = id_to_idx[neighbor.agent_id]

                A[i, j] = 1.0

        D = np.diag(A.sum(axis=1))

        return D - A