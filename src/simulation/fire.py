from __future__ import annotations
import math
import numpy as np
from settings.settings import Settings
from typing import TYPE_CHECKING, Optional, Dict, Tuple, Set, List


if TYPE_CHECKING:
    from simulation.wind import Wind
    from environment.terrain import Terrain


class Fire:
    """
    Autómata celular de propagación de incendio sobre un Terrain.

    - Cada celda activa intenta encender sus 8 vecinos en cada tick.
    - La probabilidad de propagación se modula por la alineación entre
      la dirección al vecino y el bias_vector del viento.
    - Una celda activa arde FIRE_BURN_DURATION ticks; al agotarse se
      marca BURNED en el Terrain y Cell.

    Propiedades públicas:
        cells           → [[x, y], ...]  celdas actualmente en llamas
        perimeter       → [[x, y], ...]  frente de avance del fuego
        area            → int            total de celdas afectadas
        is_extinguished → bool
    """

    def __init__(self, terrain: 'Terrain', wind: 'Wind', seed: Optional[int] = None):
        self.terrain = terrain
        self.wind = wind
        
        self.base_spread_prob = Settings.get_setting('FIRE_SPREAD_PROB')
        self.burn_duration = Settings.get_setting('FIRE_BURN_DURATION')

        self._rng = np.random.default_rng(seed)

        self._active: Dict[Tuple[int, int], int] = {}  # {(x,y): ticks_restantes}
        self._burned: Set[Tuple[int, int]] = set()
    
    def ignite(self, x: int, y: int) -> bool:
        """
        Enciende manualmente la celda (x, y).
        Retorna True si la ignición fue exitosa.
        """

        cell = self.terrain.get_cell(y, x)

        if cell is None or not cell.is_flammable or (x, y) in self._active:
            return False
        
        cell.ignite()
        self._active[(x, y)] = self.burn_duration

        return True

    def step(self, dt: float = 1.0) -> None:
        """Avanza la simulación un tick."""

        bias = self.wind.bias_vector
        new_ignitions: Set[Tuple[int, int]] = set()
        to_burnout: Set[Tuple[int, int]] = set()

        for (cx, cy), remaining in list(self._active.items()):
            # intentar propagar a los 8 vecinos
            for nx, ny in self._neighbor_coords(cx, cy):
                if (nx, ny) in self._active or (nx, ny) in new_ignitions:
                    continue

                cell = self.terrain.get_cell(ny, nx)

                if cell is None or not cell.is_flammable:
                    continue

                prob = self._spread_probability(cx, cy, nx, ny, bias) * dt

                if self._rng.random() < prob:
                    new_ignitions.add((nx, ny))
            
            # contar down del tick
            ticks_left = remaining - 1

            if ticks_left <= 0:
                to_burnout.add((cx, cy))
            
            else:
                self._active[(cx, cy)] = ticks_left
            
        for pos in to_burnout:
            x, y = pos
            self.terrain.set_state(y, x, 'burned')
            del self._active[pos]
            self._burned.add(pos)
        
        for pos in new_ignitions:
            x, y = pos
            cell = self.terrain.get_cell(y, x)

            if cell: cell.ignite()

            self._active[pos] = self.burn_duration
    
    @property
    def cells(self) -> List[List[int]]:
        return [[x, y] for x, y in self._active]
    
    @property
    def perimeter(self) -> List[List[int]]:
        perim: List[List[int]] = []

        for cx, cy in self._active:
            for nx, ny in self._neighbor_coords(cx, cy):
                cell = self.terrain.get_cell(ny, nx)

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

    def _neighbor_coords(self, x: int, y: int) -> List[Tuple[int, int]]:
        n, coords = self.terrain.grid_size, []

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: continue

                nx, ny = x + dx, y + dy

                if 0 <= nx < n and 0 <= ny < n: coords.append((nx, ny))
        
        return coords

    def _spread_probability(self, fx: int, fy: int, nx: int, ny: int, bias: Tuple[float, float]) -> float:
        dx, dy = nx - fx, ny - fy
       
        length = math.sqrt(dx ** 2 + dy ** 2)
        dx_n, dy_n = dx / length, dy / length
        
        alignment = dx_n * bias[0] + dy_n * bias[1]

        prob = self.base_spread_prob * (
            1.0 + self.wind.speed * Settings.get_setting('WIND_INFLUENCE') * alignment
        )

        return max(0.0, min(1.0, prob))
    