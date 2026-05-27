import numpy as np


def attraction(pos: np.ndarray, target: np.ndarray, alpha: float) -> np.ndarray:
    """
    Fuerza de atracción hacia target.
    F = -∇U_attr = -α · (pos - target) = α · (target - pos)

    La fuerza crece linealmente con la distancia al objetivo.
    """

    return alpha * (target - pos)


def repulsion(pos: np.ndarray, neighbor_pos: list[np.ndarray], beta: float = 2.0, d0: float = 10.0) -> np.ndarray:
    """
    Fuerza de repulsión agregada de todos los vecinos cercanos.
    Solo actúa si la distancia al vecino es menor que d0.

    F_rep = Σ β · max(0, 1/d - 1/d0) · (pos - x_j) / d³
    """

    force = np.zeros(2)

    for xj in neighbor_pos:
        diff = pos - xj
        d = np.linalg.norm(diff)
        if 0 < d < d0:
            magnitude = beta * max(0, 1.0 / d - 1.0 / d0) / (d ** 2)
            force += magnitude * diff
    
    return force