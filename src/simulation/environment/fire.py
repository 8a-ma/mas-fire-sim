from __future__ import annotations
import math
import numpy as np
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from simulation.environment.terrain import Terrain
    from simulation.environment.wind import Wind


# Número de ticks que una celda permanece activa antes de apagarse
DEFAULT_BURN_DURATION: int = 8

# Probabilidad base de propagación por tick (sin viento)
DEFAULT_SPREAD_PROB: float = 0.25

# Cuánto amplifica el viento la probabilidad (factor multiplicador)
WIND_INFLUENCE: float = 0.4

class Fire:
    """
    Modelo de propagación de incendio sobre un Terrain, influido por un Wind.
 
    Lógica de autómata celular:
    - Cada celda activa intenta encender sus 8 vecinos en cada tick.
    - La probabilidad de propagación se modula por la alineación entre la
      dirección al vecino y el vector de viento (bias_vector).
    - Una celda activa permanece encendida DEFAULT_BURN_DURATION ticks;
      al agotarse, se marca como "burned" en el Terrain.
 
    Propiedades expuestas (coinciden con el API contract):
        cells      → [[x, y], ...]  celdas actualmente en llamas
        perimeter  → [[x, y], ...]  borde exterior del fuego
        area       → int            celdas quemadas acumuladas (burned + active)
    """

    def __init__(
            self,
            terrain: "Terrain",
            wind: "Wind",
            base_spread_prob: float = DEFAULT_SPREAD_PROB,
            burn_duration: int = DEFAULT_BURN_DURATION,
            seed: int | None = None,
    ) -> None:
        self.terrain = terrain
        self.wind = wind
        self.base_spread_prob = base_spread_prob
        self.burn_duration = burn_duration
        self._rng = np.random.default_rng(seed)
        
        # {(x, y): ticks_restantes_de_combustion}
        self._active: dict[tuple[int, int], int] = {}

        # celdas ya apagadas
        self._burned: set[tuple[int, int]] = set()
    
    def ignite(self, x: int, y: int) -> bool:
        """
        Enciende manualmente la celda (x, y) si es inflamable.
        Retorna True si la ignición fue exitosa.
        """
        cell = self.terrain.get_cell(x, y)

        if cell is not None and cell.is_flammable and (x, y) not in self._active:
            self._active[(x, y)] = self.burn_duration
            return True
        
        return False

    def step(self, dt: float = 1.0) -> None:
        """
        Avanza la simulación un tick.
 
        dt escala la probabilidad de propagación, permitiendo pasos de
        tiempo variables sin cambiar base_spread_prob.
        """

        bias = self.wind.bias_vector
        new_ignitions: set[tuple[int, int]] = set()
        to_burnout: set[tuple[int, int]] = set()

        for (cx, cy), remaining in self._active.items():
            for nx, ny in self._neighbor_coords(cx, cy):
                if (nx, ny) in self._active or (nx, ny) in new_ignitions:
                    continue
                cell = self.terrain.get_cell(nx, ny)

                if cell is None or not cell.is_flammable:
                    continue
                
                prob = self._spread_probability(cx, cy, nx, ny, bias) * dt
                if self._rng.random() < prob:
                    new_ignitions.add((nx, ny))

            ticks_left = remaining - 1

            if ticks_left <= 0:
                to_burnout.add((cx, cy))
            
            else:
                self._active[(cx, cy)] = ticks_left
        
        # apagar celdas agotadas
        for pos in to_burnout:
            self.terrain.set_state(*pos, "burned")
            del self._active[pos]
            self._burned.add(pos)
        
        for pos in new_ignitions:
            self._active[pos] = self.burn_duration
    
    @property
    def cells(self) -> list[list[int]]:
        return [[x, y] for x, y in self._active]
    
    @property
    def perimeter(self) -> list[list[int]]:
        """
        Celdas activas que tienen al menos un vecino inflamable (no ardiendo).
        Representa el frente de avance del fuego.
        """

        perim: list[list[int]] = []

        for (cx, cy) in self._active:
            for nx, ny in self._neighbor_coords(cx, cy):
                cell = self.terrain.get_cell(nx, ny)

                if cell is not None and cell.is_flammable:
                    perim.append([cx, cy])
                    break
        
        return perim

    @property
    def area(self) -> int:
        return len(self._active) + len(self._burned)
    
    @property
    def is_extinguished(self) -> bool:
        return len(self._active) == 0
    
    def _neighbor_coords(self, x: int, y: int) -> list[tuple[int, int]]:
        n = self.terrain.n
        coords = []

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                
                nx, ny = x + dx, y + dy

                if 0 <= nx < n and 0 <= ny < n:
                    coords.append((nx, ny))
        return coords

    def _spread_probability(
            self,
            fx: int,
            fy: int,
            nx: int,
            ny: int,
            bias: tuple[float, float],
    ) -> float:
        """
        Calcula la probabilidad de propagación de (fx, fy) → (nx, ny).
 
        Formula:
            p = base_spread_prob * (1 + wind_speed * WIND_INFLUENCE * alignment)
 
        donde alignment ∈ [-1, 1] es el coseno del ángulo entre la dirección
        de propagación y el bias_vector del viento.
        """
        dx, dy = nx - fx, ny - fy
        length = math.sqrt(dx * dx + dy * dy)
        dx_n, dy_n = dx / length, dy / length

        alignment = dx_n * bias[0] + dy_n * bias[1]
        prob = self.base_spread_prob * (1.0 + self.wind.speed * WIND_INFLUENCE * alignment)

        return max(0.0, min(1.0, prob))