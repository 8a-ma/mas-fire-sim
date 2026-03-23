from __future__ import annotations
import numpy as np


def attraction(
        pos: np.ndarray,
        target: np.ndarray,
        alpha: float,
    ) -> None:
    """
    Término de atracción de la ley de control de primer orden.
 
    Implementa directamente la ecuación del documento:
        ẋᵢ = α · (x_deseado - xᵢ)
 
    Args:
        pos    : posición actual del agente [x, y]
        target : posición objetivo (punto en el perímetro del fuego)
        alpha  : ganancia de control (configurable via POST /sim/control)
 
    Returns:
        Vector fuerza 2D de atracción.
    """

    return alpha * (target - pos)


def consensus(
        pos: np.ndarray,
        neighbors_pos: list[np.ndarray],
        alpha: float,
    ) -> np.ndarray:

    """
    Término de consenso distribuido basado en la matriz Laplaciana.
 
    Cuando el grafo es conexo, este término hace que los agentes
    converjan a posiciones de equilibrio respecto a sus vecinos.
    Es la extensión multi-agente de la ley de atracción individual.
 
    Implementa:
        ẋᵢ = -α · Σⱼ∈Nᵢ (xᵢ - xⱼ)
 
    Args:
        pos           : posición del agente i
        neighbors_pos : lista de posiciones de vecinos j ∈ Nᵢ
        alpha         : ganancia de control
 
    Returns:
        Vector fuerza 2D de consenso.
    """

    if not neighbors_pos:
        return np.zeros(2)
    
    force = np.zeros(2)
    
    for n_pos in neighbors_pos:
        force += (pos - n_pos)

    return alpha * force


def combined(
    pos: np.ndarray,
    target: np.ndarray,
    neighbors_pos: list[np.ndarray],
    alpha: float,
    consensus_weight: float = 0.3,
) -> np.ndarray:
    """
    Ley completa: atracción al objetivo + consenso con vecinos.
 
    El Engine llama a esta función cuando quiere aplicar la ley
    completa sin pasar por los métodos del agente (por ejemplo,
    para calcular fuerzas en batch o para logging).
 
    Args:
        consensus_weight : cuánto peso tiene el consenso vs la atracción.
                           0.0 = solo atracción, 1.0 = solo consenso.
    """
    f_attr = attraction(pos, target, alpha)
    f_cons = consensus(pos, neighbors_pos, alpha)
    return f_attr + consensus_weight * f_cons