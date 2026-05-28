import numpy as np


def vote_consensus(my_vote: np.ndarray, neighbor_votes: list[np.ndarray], neighbor_distances: list[float], epsilon: float = 0.3) -> np.ndarray:
    """
    Un paso del protocolo de consenso de votos ponderado por distancia.

    Cada vecino tiene peso w = 1 / (1 + d_vecino_a_su_target).
    Cuanto más cerca está un agente bombero de su zona propuesta, más peso tiene.

    Retorna el nuevo voto para este tick.

    vote_i(t+1) = vote_i(t) + ε · Σ w_ij · [vote_j(t) − vote_i(t)]

    Garantía de convergencia: ε < 1 / max_degree_esperado (usar ε ≤ 0.3
    es seguro para grafos con hasta 3 vecinos simultáneos).
    """

    if not neighbor_votes: return my_vote.copy()

    correction = np.zeros(2)

    for vote_j, dist_j in zip(neighbor_votes, neighbor_distances):
        w_ij = 1.0 / (1.0 + dist_j)
        correction += w_ij * (vote_j - my_vote)
    
    return my_vote + epsilon * correction