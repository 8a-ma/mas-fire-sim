from __future__ import annotations
import numpy as np


def repulsion(
    pos: np.ndarray,
    neighbors_pos: list[np.ndarray],
    min_dist: float = 10.0,
    strength: float = 1.0,
) -> np.ndarray:
    """
    Término de repulsión entre agentes vecinos.

    Implementa el Σ f_rep(xᵢ, xⱼ).
    La fuerza es inversamente proporcional a la distancia:
    cuanto más cerca está un vecino, mayor la repulsión.
    Fuera de min_dist la fuerza es cero (sin influencia).

    Args:
        pos           : posición del agente i
        neighbors_pos : posiciones de agentes j ∈ Nᵢ (del grafo)
        min_dist      : radio de influencia en unidades del grid
        strength      : escalar para modular la intensidad global

    Returns:
        Vector fuerza 2D resultante de la repulsión acumulada.
    """

    force = np.zeros(2)

    for n_pos in neighbors_pos:
        diff = pos - n_pos
        dist = float(np.linalg.norm(diff))

        if 0 < dist < min_dist:
            magnitude = strength * (min_dist - dist) / min_dist
            force += (diff / dist) * magnitude

    return force


def perimeter_coverage_repulsion(
    pos: np.ndarray,
    neighbors_pos: list[np.ndarray],
    perimeter_target: np.ndarray,
    spread_radius: float = 20.0,
) -> np.ndarray:
    """
    Variante de repulsión orientada a cubrir el perímetro.

    Además de alejarse de vecinos cercanos, empuja al agente
    hacia zonas del perímetro que no están cubiertas por nadie.

    Usada por Drone para garantizar que el frente completo
    esté observado (distribución uniforme sobre el perímetro).

    Args:
        perimeter_target : punto del perímetro asignado a este agente
        spread_radius    : distancia a la que un vecino "bloquea" la zona

    Returns:
        Vector fuerza 2D combinada.
    """
    base = repulsion(pos, neighbors_pos)

    # Si hay un vecino muy cerca del mismo target, desviarse lateralmente
    target_dir = perimeter_target - pos
    target_dist = float(np.linalg.norm(target_dir))
    if target_dist < 1e-6:
        return base

    target_unit = target_dir / target_dist
    lateral = np.array([-target_unit[1], target_unit[0]])  # perpendicular

    crowding = 0.0
    
    for n_pos in neighbors_pos:
        dist_to_target = float(np.linalg.norm(n_pos - perimeter_target))
        if dist_to_target < spread_radius:
            crowding += (spread_radius - dist_to_target) / spread_radius

    return base + lateral * crowding * 0.5